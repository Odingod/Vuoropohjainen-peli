class NotSaveableException(Exception): pass
class NotLoadableException(Exception): pass

def saveable(obj):
    if obj is None:
        return None

    try:
        return obj.__saveable__()
    except Exception as e:
        print e
        print obj
        print '!!!'
        raise NotSaveableException('Type {0} cannot be saved.'.format(type(obj)))

def load(typ, d, *args, **kwargs):
    if d is None:
        return None

    try:
        return typ.__load__(d, *args, **kwargs)
    except Exception as e:
        print e
        raise NotLoadableException(
                'Type {0} could not be loaded from {1}'.format(typ, d[:50]))
