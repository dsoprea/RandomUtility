#!/usr/bin/env python

import gevent.monkey
gevent.monkey.patch_all()

import os.path
import math
import logging
import functools 
import tempfile
import shutil

import gevent

import boto.s3.multipart
import boto.s3.connection

_MIN_MULTIPART_SIZE_B = 30 * 1024 * 1024
_DEFAULT_CHUNK_SIZE_B = 20 * 1024 * 1024
_DEFAULT_MONITOR_INTERVAL_S = 10

_logger = logging.getLogger(__name__)


class S3ParallelDownload(object):
    def __init__(self, ak, sk, bucket_name, key_name,
                 chunk_size_b=_DEFAULT_CHUNK_SIZE_B,
                 monitor_interval_s=_DEFAULT_MONITOR_INTERVAL_S):
        self.__ak = ak
        self.__sk = sk

        self.__bucket_name = bucket_name
        self.__key_name = key_name
        self.__chunk_size_b = chunk_size_b
        self.__monitor_interval_s = _DEFAULT_MONITOR_INTERVAL_S

        self.__coverage = 0.0

    def __get_bucket(self):
        _logger.debug("Connecting bucket [%s]: AK=[%s] SK=[%s]", 
                     self.__bucket_name, self.__ak, self.__sk)

        conn = boto.s3.connection.S3Connection(self.__ak, self.__sk)
        return conn.get_bucket(self.__bucket_name)

    def __standard_download(self, filesize_b):
        k = self.__get_key()
        
        with tempfile.NamedTemporaryFile(delete=False) as f:
            k.get_contents_to_file(
                f, 
                cb=self.__standard_cb, 
                num_cb=20)

            return f.name

    def __standard_cb(self, current, total):
        _logger.debug("Status: %.2f%%", float(current) / float(total) * 100.0)

    def __multipart_cb(self, i, eff_chunk_size_b, current, total):
        self.__progress[i] = float(current) / float(eff_chunk_size_b) * 100.0

    def __get_key(self):
        b = self.__get_bucket()
        k = b.get_key(self.__key_name)
        if k is None:
            raise KeyError(self.__key_name)

        return k

    def __transfer_part(self, (i, offset, filesize_b, filepath)):
        _logger.debug("Initiating download for chunk (%d) at offset: "
                     "(%d)/(%d)", i, offset, filesize_b)

        k = self.__get_key()

        with open(filepath, 'wb') as f:
            f.seek(offset)

            eff_chunk_size_b = min(offset + self.__chunk_size_b, 
                                   filesize_b) - \
                               offset

            range_string = 'bytes=%d-%d' % \
                           (offset, offset + eff_chunk_size_b - 1)

            headers = { 'Range': range_string }

            cb = functools.partial(self.__multipart_cb, i, eff_chunk_size_b)
            k.get_contents_to_file(f, headers=headers, cb=cb, num_cb=100)

    def __mp_show_progress(self):
        while 1:
            columns = [("%3d%%" % self.__progress[i]) 
                       for i 
                       in range(self.__chunks)]

            pline = ' '.join(columns)
            _logger.debug(pline)

            gevent.sleep(self.__monitor_interval_s)

    def __multipart_download(self, filesize_b):
        chunk_list = range(0, filesize_b, self.__chunk_size_b)

        self.__chunks = len(chunk_list)
        self.__progress = [0.0] * self.__chunks

        with tempfile.NamedTemporaryFile(delete=False) as f:
            filepath = f.name

            gen = ((i, offset, filesize_b, filepath) 
                   for (i, offset) 
                   in enumerate(chunk_list))

            f = functools.partial(gevent.spawn, self.__transfer_part)

            if self.__monitor_interval_s > 0:
                p = gevent.spawn(self.__mp_show_progress)

            g_list = map(f, gen)

            gevent.joinall(g_list)

            if self.__monitor_interval_s > 0:
                p.kill()
                p.join()

            return filepath

    def start(self):
        _logger.debug("Reading key size.")
        filesize_b = self.__get_key().size

        _logger.debug("Size: %d", filesize_b)

        if filesize_b < _MIN_MULTIPART_SIZE_B:
            self.__standard_download(filesize_b)
        else:
            self.__multipart_download(filesize_b)

def download(*args):
    return S3ParallelDownload(*args).start()

if __name__ == '__main__':
    _logger.setLevel(logging.DEBUG)
    logging.getLogger('boto').setLevel(logging.INFO)

    ch = logging.StreamHandler()

    FMT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(FMT)
    ch.setFormatter(formatter)
    _logger.addHandler(ch)

    import sys
    if len(sys.argv) < 5:
        print("Please provide the access-key, secret-key, bucket-name, "
              "and key_name to download.")
        sys.exit(1)

    (_ignore, ak, sk, bucket_name, key_name) = sys.argv
    download(ak, sk, bucket_name, key_name)
