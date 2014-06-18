#!/usr/bin/env python2.7

import os.path
import argparse
import datetime
import hashlib
import random
import time

import M2Crypto.X509
import M2Crypto.ASN1
import M2Crypto.RSA
import M2Crypto.EVP

_OUTPUT_PATH = 'output'
_CA_PASSPHRASE = 'test'

_CA_KEY_PEM_FILENAME = 'output/ca.key.pem'
_CA_CRT_PEM_FILENAME = 'output/ca.crt.pem'

_SERIAL_NUMBER_GENERATOR_CB = lambda: \
                                hashlib.sha1(str(time.time()) + str(random.random())).\
                                    hexdigest()

def pem_private_to_rsa(private_key_pem, passphrase=None):
    def passphrase_cb(*args):
        return passphrase

    rsa = M2Crypto.RSA.load_key_string(
            private_key_pem, 
            callback=passphrase_cb)

    return rsa

def pem_csr_to_csr(csr_pem):
    return M2Crypto.X509.load_request_string(csr_pem)

def pem_certificate_to_x509(cert_pem):
    return M2Crypto.X509.load_cert_string(cert_pem)

def new_cert(ca_private_key_pem, csr_pem, validity_td, issuer_name, bits=2048,
             is_ca=False, passphrase=None):
    ca_rsa = pem_private_to_rsa(
                ca_private_key_pem, 
                passphrase=passphrase)

    def callback(*args):
        pass

    csr = pem_csr_to_csr(csr_pem)

    public_key = csr.get_pubkey()
    name = csr.get_subject()

    cert = M2Crypto.X509.X509()

    sn_hexstring = _SERIAL_NUMBER_GENERATOR_CB()
    sn = int(sn_hexstring, 16)

    cert.set_serial_number(sn)
    cert.set_subject(name)

    now_epoch = long(time.time())

    notBefore = M2Crypto.ASN1.ASN1_UTCTIME()
    notBefore.set_time(now_epoch)

    notAfter = M2Crypto.ASN1.ASN1_UTCTIME()
    notAfter.set_time(now_epoch + long(validity_td.total_seconds()))

    cert.set_not_before(notBefore)
    cert.set_not_after(notAfter)

    cert.set_issuer(issuer_name)
    cert.set_pubkey(public_key) 

    ext = M2Crypto.X509.new_extension('basicConstraints', 'CA:FALSE')
    cert.add_ext(ext)

    pkey = M2Crypto.EVP.PKey()
    pkey.assign_rsa(ca_rsa)

    cert.sign(pkey, 'sha1')
    cert_pem = cert.as_pem()

    return cert_pem

def sign(ca_key_filepath, ca_crt_filepath, csr_filepath, passphrase=None):
    with open(ca_crt_filepath) as f:
        ca_cert_pem = f.read()

    with open(ca_key_filepath) as f:
        ca_private_key_pem = f.read()

    ca_cert = pem_certificate_to_x509(ca_cert_pem)

    issuer_name = ca_cert.get_issuer()

    with open(csr_filepath) as f:
        csr_pem = f.read()

    validity_td = datetime.timedelta(days=400)
    return new_cert(
            ca_private_key_pem, 
            csr_pem, 
            validity_td, 
            issuer_name, 
            passphrase=passphrase)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sign a CSR')

    parser.add_argument('ca_key_filepath',
                        help='File-path of CA PEM private-key')

    parser.add_argument('ca_crt_filepath',
                        help='File-path of CA PEM certificate')

    parser.add_argument('csr_filepath',
                        help='File-path of PEM CSR')

    parser.add_argument('-p', '--passphrase',
                        help='CA passphrase')

    args = parser.parse_args()

    crt_pem = sign(
                args.ca_key_filepath,
                args.ca_crt_filepath,
                args.csr_filepath, 
                passphrase=args.passphrase)

    print(crt_pem)
