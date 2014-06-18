Summary
-------

A simple X509 certificate signer. Ordinarily, you'd have to configure an 
OpenSSL CA in order to do this.


Usage
-----

Pass-in the CA key, CA certificate, and CSR. The signed certificate will be 
printed to standard-out.


Examples
--------

```
$ ./ssl_sign.py ca.key.pem ca.crt.pem csr.pem
```
