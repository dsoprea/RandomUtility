"""An XML-RPC <-> Magento PoC."""

import os
import json

import xml.etree.ElementTree as ET

import requests

# http://xmlrpc.scripting.com/spec.html

_HOSTNAME = os.environ['MAGENTO_HOSTNAME']
_USERNAME = os.environ['MAGENTO_USERNAME']
_PASSWORD = os.environ['MAGENTO_PASSWORD']

_URL = "http://" + _HOSTNAME + "/api/xmlrpc"

_HEADERS = {
    'Content-Type': 'text/xml',
}

def _pretty_print(results):
    print(json.dumps(
            results, 
            sort_keys=True,
            indent=4, 
            separators=(',', ': ')))

def _send_request(payload):
    r = requests.post(_URL, data=payload, headers=_HEADERS)
    r.raise_for_status()

    root = ET.fromstring(r.text)
    return root

def _send_array(session_id, method_name, args):

    data_parts = []
    for (type_name, value) in args:
        data_parts.append('<value><' + type_name + '>' + str(value) + '</' + type_name + '></value>')
                        
    payload = """\
<?xml version='1.0'?>
<methodCall>
    <methodName>call</methodName>
    <params>
        <param>
            <value><string>""" + session_id + """\
</string></value>
        </param>
        <param>
            <value><string>""" + method_name + """\
</string></value>
        </param>
        <param>
            <value>
                <array>
                    <data>
                        """ + ''.join(data_parts) + """
                    </data>
                </array>
            </value>
        </param>
    </params>
</methodCall>
"""

    return _send_request(payload)

def _send_struct(session_id, method_name, args):
    struct_parts = []

    for (type_name, argument_name, argument_value) in args:
        struct_parts.append("<member><name>" + argument_name + "</name><value><" + type_name + ">" + str(argument_value) + "</" + type_name + "></value></member>")
                        
    payload = """\
<?xml version='1.0'?>
<methodCall>
    <methodName>call</methodName>
    <params>
        <param>
            <value><string>""" + session_id + """\
</string></value>
        </param>
        <param>
            <value><string>""" + method_name + """\
</string></value>
        </param>
        <param>
            <value>
                <struct>
                    """ + ''.join(struct_parts) + """
                </struct>
            </value>
        </param>
    </params>
</methodCall>
"""

    return _send_request(payload)

def _send_login(args):
    param_parts = []
    for (type_name, value) in args:
        param_parts.append('<param><value><' + type_name + '>' + value + '</' + type_name + '></value></param>')

    payload = """\
<?xml version="1.0"?>
<methodCall>
    <methodName>login</methodName>
    <params>""" + ''.join(param_parts) + """\
</params>
</methodCall>
"""

    return _send_request(payload)


class XmlRpcFaultError(Exception):
    pass

def _distill(value_node):
    type_node = value_node[0]
    type_name = type_node.tag

    if type_name == 'nil':
        return None
    elif type_name in ('int', 'i4'):
        return int(type_node.text)
    elif type_name == 'boolean':
        return bool(type_node.text)
    elif type_name == 'double':
        return float(type_node.text)
    elif type_name == 'struct':
        values = {}
        for member_node in type_node:
            key = member_node.find('name').text

            value_node = member_node.find('value')
            value = _distill(value_node)

            values[key] = value

        return values
    elif type_name == 'array':
        flat = []
        for i, child_value_node in enumerate(type_node.findall('data/value')):
            flat.append(_distill(child_value_node))

        return flat
    elif type_name in ('string', 'dateTime.iso8601', 'base64'):
        return type_node.text
    else:
        raise ValueError("Invalid type: [{0}] [{1}]".format(type_name, type_node))

def _parse_response(root):
    if root.find('fault') is not None:
        for e in root.findall('fault/value/struct/member'):
            if e.find('name').text == 'faultString':
                message = e.find('value/string').text
                raise XmlRpcFaultError(message)

        raise ValueError("Malformed fault response")

    value_node = root.find('params/param/value')
    result = _distill(value_node)

    return result

def _main():
    args = [
        ('string', _USERNAME),
        ('string', _PASSWORD),
    ]
    
    root = _send_login(args)
    session_id = _parse_response(root)

    resource_name = 'catalog_product.info'

    args = [
        ('int', 'productId', '314'),
    ]

    root = _send_struct(session_id, resource_name, args)
    result = _parse_response(root)
    _pretty_print(result)

if __name__ == '__main__':
    _main()
