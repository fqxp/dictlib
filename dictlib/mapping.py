from UserDict import DictMixin
from dictlib.utils import setitem, getitem, delitem, contains, walk

__all__ = (u'DotNotationAdapter', u'DotNotationMixin', u'ObjectMappingAdapter', 
           u'ObjectMappingMixin')

class BaseDictAdapter(DictMixin):
    def __init__(self, doc=None):
        """ Default constructor internally memorizes the given `doc` (or any 
        empty dictionary if no `doc` is given). You can access the (possibly wrapped)
        dictionary through the `_doc` attribute.
        
        :see: `BaseDictAdapter.doc`
        """
        self.__dict__[u'_doc'] = doc if doc is not None else {}

    @property
    def doc(self):
        """ The original `dict`, without any wrappers around it. Recurses
        through possible subsequent `BaseDictAdapter`s. This is a read-only
        attribute.
        """
        obj = self
        while isinstance(obj, BaseDictAdapter):
            obj = obj._doc
        return obj

class DotNotationAdapter(BaseDictAdapter):
    def __getitem__(self, key):
        try:
            return getitem(self._doc, key)
        except IndexError as e:
            raise KeyError(e)

    def __setitem__(self, key, value):
        try:
            return setitem(self._doc, key, value)
        except IndexError as e:
            raise KeyError(e)

    def __delitem__(self, key):
        try:
            delitem(self._doc, key)
        except IndexError as e:
            raise KeyError(e)
        
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
        try:
            return getitem(super(DotNotationMixin, self), key)
        except IndexError as e:
            raise KeyError(e)

    def __setitem__(self, key, value):
        try:
            setitem(super(DotNotationMixin, self), key, value)
        except IndexError as e:
            raise KeyError(e)

    def __delitem__(self, key):
        try:
            delitem(super(DotNotationMixin, self), key)
        except IndexError as e:
            raise KeyError(e)
        
    def __contains__(self, key):
        return contains(super(DotNotationMixin, self), key)
        
    def keys(self):
        return super(DotNotationMixin, self).keys()

class ObjectMappingAdapter(BaseDictAdapter):
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
            if isinstance(value, dict):
                return ObjectMappingAdapter(value)
            else:
                return value
        except KeyError:
            raise AttributeError(u'Object has no attribute %s' % key)
        
    def __setattr__(self, key, value):
        self._doc[key] = value

class ObjectMappingMixin(object):
    def __getattr__(self, key):
        try:
            value = self[key]
            if isinstance(value, dict):
                return ObjectMappingAdapter(value)
            else:
                return value
        except KeyError:
            raise AttributeError(u'Object has no attribute %s' % key)
        
    def __setattr__(self, key, value):
        self[key] = value
