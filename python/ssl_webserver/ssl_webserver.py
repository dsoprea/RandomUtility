#!/usr/bin/env python2.7

import os.path
import socket
import SocketServer
import BaseHTTPServer
import SimpleHTTPServer
import ssl
 
 
class _SecureHTTPRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def setup(self):
        self.connection = self.request
        self.rfile = socket._fileobject(self.request, 'rb', self.rbufsize)
        self.wfile = socket._fileobject(self.request, 'wb', self.wbufsize)
 
 
class _SecureHTTPServer(BaseHTTPServer.HTTPServer):
    def __init__(self, private_key_pem_filepath, cert_pem_filepath, 
                 binding=None, handler_cls=_SecureHTTPRequestHandler):
        if binding is None:
            # The default port is 1443 so that we don't have to be root.
            binding = ('', 1443)
         
        SocketServer.BaseServer.__init__(self, binding, handler_cls)
 
        s = socket.socket(self.address_family, self.socket_type)
        self.socket = ssl.SSLSocket(
                        s, 
                        keyfile=private_key_pem_filepath, 
                        certfile=cert_pem_filepath)
 
        self.server_bind()
        self.server_activate()
 
app_path = os.path.abspath(os.path.dirname(__file__))
 
private_key_pem_filepath = os.path.join(app_path, 'server.private_key.pem')
certificate_pem_filepath = os.path.join(app_path, 'server.crt.pem')
 
httpd = _SecureHTTPServer(
            private_key_pem_filepath, 
            certificate_pem_filepath)
 
print("Running.")
httpd.serve_forever()
