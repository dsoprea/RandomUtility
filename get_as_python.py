from io import StringIO

_max_depth = 10

def _convert_to_string(d):
    return _str("\"%s\"" % (_str(d).\
                             replace('\\', '\\\\').\
                             replace('"', '\\"')))

# Python 2/3 compatibility.

_str = str

try:
    unicode
    long
except NameError:
    unicode = str
    long = int
else:
    # If we're not in Python3, use 'unicode' to write to the buffer.
    _str = unicode

_comma = _str(',')
_start_paren = _str('(')
_stop_paren = _str(')')
_start_square = _str('[')
_stop_square = _str(']')
_start_curly = _str('{')
_stop_curly = _str('}')
_equal = _str(' = ')
_colon = _str(':')
_nl = _str('\n')

def get_as_python(d, level=0):
    if level == 0 and issubclass(d.__class__, dict) is False:
        raise TypeError("The outer-most type must be a dictionary.")
    elif level > _max_depth:
        raise Exception("Data is too deep. Abort.")

    if d is None:
        return _str('None')
    elif issubclass(d.__class__, (str, unicode)):
        return _convert_to_string(d)
    elif issubclass(d.__class__, (int,float,long)):
        return _str("%s" % (d))
    elif issubclass(d.__class__, (tuple,list)):
        if issubclass(d.__class__, tuple):
            start_char = _start_paren
            stop_char = _stop_paren
        else:
            start_char = _start_square
            stop_char = _stop_square
    
        i = 0
        l = len(d)
        s = StringIO()
        s.write(start_char)
        while i < l:
            if i > 0:
                s.write(_comma)
        
            s.write(get_as_python(d[i], level + 1))
            i += 1

        s.write(stop_char)
        return s.getvalue()
    elif issubclass(d.__class__, dict):
        s = StringIO()
        if level == 0:
            # We're at the top-layer, and serializing the root dictionary. We need
            # to return Python code.
            
            for k, v in d.items():
                s.write(_str(k))
                s.write(_equal)
                s.write(get_as_python(v, level + 1))
                s.write(_nl)

            s.write(_nl)
        else:
            s.write(_start_curly)
            i = 0
            for k, v in d.items():
                if i > 0:
                    s.write(_comma)
                
                s.write(_convert_to_string(k))
                s.write(_colon)
                s.write(get_as_python(v, level + 1))
                i += 1
            
            s.write(_stop_curly)
        return s.getvalue()
    else:
        raise TypeError("Could not encode type [%s]." % (d.__class__.__name__))

