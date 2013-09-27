from io import BytesIO

_max_depth = 10

def _convert_to_string(d):
    return ("\"%s\"" % (str(d).\
                            replace('\\', '\\\\').\
                            replace('"', '\\"')))

def get_as_python(d, level=0):
    if level == 0 and issubclass(d.__class__, dict) is False:
        raise TypeError("The outer-most type must be a dictionary.")
    elif level > _max_depth:
        raise Exception("Data is too deep. Abort.")

    if d is None:
        return ('None')
    elif issubclass(d.__class__, basestring):
        return (_convert_to_string(d))
    elif issubclass(d.__class__, (int,float,long)):
        return ("%s" % (d))
    elif issubclass(d.__class__, (tuple,list)):
        i = 0
        l = len(d)
        s = BytesIO()
        s.write('[')
        while i < l:
            if i > 0:
                s.write(',')
        
            s.write(get_as_python(d[i], level + 1))
            i += 1

        s.write(']')
        return s.getvalue()
    elif issubclass(d.__class__, dict):
        s = BytesIO()
        if level == 0:
            # We're at the top-layer, and serializing the root dictionary. We need
            # to return Python code.
            
            for k, v in d.items():
                s.write(str(k))
                s.write(' = ')
                s.write(get_as_python(v, level + 1))
                s.write('\n')

            s.write('\n')
        else:
            s.write('{')
            i = 0
            for k, v in d.items():
                if i > 0:
                    s.write(',')
                
                s.write(_convert_to_string(k))
                s.write(':')
                s.write(get_as_python(v, level + 1))
                i += 1
            
            s.write('}')
        return s.getvalue()
    else:
        raise TypeError("Could not encode type [%s]." % (d.__class__.__name__))

