#!/usr/bin/env python
# A distant cousin of : https://gist.githubusercontent.com/chrishamant/1556484/raw/366c0d1ba0c653a04ccf0fd0274db7f004ae585d/s3_multipart_upload.py

import gevent.monkey
gevent.monkey.patch_all()

import os.path
import math
import logging
import functools 

import gevent

import boto.s3.multipart
import boto.s3.connection

_MIN_MULTIPART_SIZE_B = 30 * 1024 * 1024

# Chunks have to be at least 5M.
_DEFAULT_CHUNK_SIZE_B = 20 * 1024 * 1024

_DEFAULT_MONITOR_INTERVAL_S = 10

_logger = logging.getLogger(__name__)


class S3ParallelUpload(object):
    def __init__(self, ak, sk, bucket_name, key_name, filepath, 
                 chunk_size_b=_DEFAULT_CHUNK_SIZE_B,
                 monitor_interval_s=_DEFAULT_MONITOR_INTERVAL_S):
        self.__ak = ak
        self.__sk = sk

        self.__bucket_name = bucket_name
        self.__key_name = key_name
        self.__filepath = filepath
        self.__chunk_size_b = chunk_size_b
        self.__coverage = 0.0
        self.__monitor_interval_s = _DEFAULT_MONITOR_INTERVAL_S

        self.__filesize_b = os.path.getsize(self.__filepath)
        self.__chunks = int(math.ceil(float(self.__filesize_b) / 
                                      float(self.__chunk_size_b)))

        self.__progress = [0.0] * self.__chunks

    def __get_bucket(self, bucket_name):
        conn = boto.s3.connection.S3Connection(self.__ak, self.__sk)
        return conn.get_bucket(bucket_name)

    def __standard_upload(self):
        bucket = self.__get_bucket(self.__bucket_name)
        new_s3_item = bucket.new_key(self.__key_name)
        new_s3_item.set_contents_from_filename(
            self.__filepath, 
            cb=self.__standard_cb, 
            num_cb=20)

    def __standard_cb(self, current, total):
        _logger.debug("Status: %.2f%%", float(current) / float(total) * 100.0)

    def __multipart_cb(self, i, current, total):
        self.__progress[i] = float(current) / float(total) * 100.0

    def __transfer_part(self, (mp_info, i, offset)):
        (mp_id, mp_key_name, mp_bucket_name) = mp_info

        bucket = self.__get_bucket(mp_bucket_name)
        mp = boto.s3.multipart.MultiPartUpload(bucket)
        mp.key_name = mp_key_name
        mp.id = mp_id

        # At any given time, this will describe the farther percentage into the 
        # file that we're actively working on.
        self.__coverage = max(
                            (float(offset) / float(self.__filesize_b) * 100.0), 
                            self.__coverage)

        # The last chunk might be shorter than the rest.
        eff_chunk_size = min(offset + self.__chunk_size_b, 
                             self.__filesize_b) - \
                         offset

        with open(self.__filepath, 'rb') as f:
            f.seek(offset)
            mp.upload_part_from_file(
                f, 
                i + 1, 
                size=eff_chunk_size, 
                cb=functools.partial(self.__multipart_cb, i), 
                num_cb=100)

    def __mp_show_progress(self):
        while 1:
            columns = [("%3d%% " % self.__progress[i]) 
                       for i 
                       in range(self.__chunks)]

            pline = ' '.join(columns)
            _logger.debug(pline)

            gevent.sleep(self.__monitor_interval_s)

    def __multipart_upload(self):
        bucket = self.__get_bucket(self.__bucket_name)

        mp = bucket.initiate_multipart_upload(self.__key_name)
        mp_info = (mp.id, mp.key_name, mp.bucket_name)
        chunk_list = range(0, self.__filesize_b, self.__chunk_size_b)

        try:
            gen = ((mp_info, i, offset) 
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
        except:
            mp.cancel_upload()
            raise
        else:
            mp.complete_upload()

    def start(self):
        if self.__filesize_b < _MIN_MULTIPART_SIZE_B:
            self.__standard_upload()
        else:
            self.__multipart_upload()

def upload(*args):
    return S3ParallelUpload(*args).start()

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
              "key_name, and file-path to upload.")
        sys.exit(1)

    (_ignore, ak, sk, bucket_name, key_name, filepath) = sys.argv
    upload(ak, sk, bucket_name, key_name, filepath)
