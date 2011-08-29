from UserDict import DictMixin
from dictlib.utils import setitem, getitem, delitem, contains

class DotNotationAdapter(DictMixin, object):
    def __init__(self, doc):
        self.__dict__[u'_doc'] = doc
            
    def __getitem__(self, key):
        return getitem(self._doc, key)

    def __setitem__(self, key, value):
        return setitem(self._doc, key, value)

    def __delitem__(self, key):
        delitem(self._doc, key)
        
    def __contains__(self, key):
        return contains(self._doc, key)
        
    def keys(self):
        return self._doc.keys()


class DotNotationMixin(object):
    """ Return a field by `name`. This method can be used both for dotted
    paths (e. g. 'info.author.first_name') and for recursive walking through
    a schema (by using the `schema` parameter).
    
    :param name: The path of the field in dot notation.
    :param schema: If given, `schema` used as the schema description instead of
        `self.schema`.
    """
    def __getitem__(self, key):
        return getitem(super(DotNotationMixin, self), key)

    def __setitem__(self, key, value):
        setitem(super(DotNotationMixin, self), key, value)

    def __delitem__(self, key):
        delitem(super(DotNotationMixin, self), key)
        
    def __contains__(self, key):
        return contains(super(DotNotationMixin, self), key)
        
    def keys(self):
        return super(DotNotationMixin, self).keys()


class ObjectMappingAdapter(DictMixin):
    def __init__(self, doc):
        self.__dict__[u'_doc'] = doc

    def __getitem__(self, key):
        value = self._doc[key]
        if isinstance(value, dict):
            value = ObjectMappingAdapter(value)
        return value
    
    def __setitem__(self, key, value):
        self._doc[key] = value
        
    def __delitem__(self, key):
        del self._doc[key]
        
    def __contains__(self, key):
        return key in self._doc
        
    def keys(self):
        return self._doc.keys()
    
    def __getattr__(self, key):
        try:
            value = self._doc[key]
#            value = object.__getattribute__(self, u'_doc')[key]
            if isinstance(value, dict):
                return ObjectMappingAdapter(value)
        except KeyError:
            raise AttributeError(u'Object has no attribute %s' % key)
        
    def __setattr__(self, key, value):
        try:
            self._doc[key] = value
        except KeyError:
            raise AttributeError(u'Object has no attribute %s' % key)


class ObjectMappingMixin(object):
    def __getattr__(self, key):
        try:
            value = self[key]
            if isinstance(value, dict):
                return ObjectMappingAdapter(value)
        except KeyError:
            raise AttributeError(u'Object has no attribute %s' % key)
        
    def __setattr__(self, key, value):
        try:
            self[key] = value
        except KeyError:
            raise AttributeError(u'Object has no attribute %s' % key)

