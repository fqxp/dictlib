"""
This file is part of dictlib.

Dictlib is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Dictlib is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with dictlib.  If not, see <http://www.gnu.org/licenses/>.
"""
import collections

def update_recursive(doc, update_doc, skip_none=False):
    """ 
    Updates the dictionary-like object `doc` with the value from `update_doc`
    recursively, e. g.:
    >>> d1 = {'a': 1, 'b': {'c': 3, 'd': 4}}
    >>> update_recursive(d1, {'a': 2, 'b': {'c': 5}}
    {'a': 2, 'b': {'c': 5, 'd': 4}}

    :param doc: The dictionary to update; will modified in-place
    :param update_doc: The update_doc to update the dictionary with
    :param skip_none: if True, do not update values which would become None
        in the result.
    :returns: The updated dictionary `doc`
    """
    for k, v in update_doc.iteritems():
        if isinstance(v, collections.Mapping):
            inner_doc = doc.get(k)
            if not isinstance(inner_doc, collections.Mapping):
                doc[k] = {}
            update_recursive(doc[k], v, skip_none)
        elif v is None and skip_none:
            continue
        else:
            doc[k] = update_doc[k]
    return doc


def walk(d, field_name=None):
    """ Walk a dictionary `d` recursively by yielding a (`PATH`, `VALUE`) tuple
    for each key/value pair. `PATH` is a list of keys in dot notation.
    
    :param d: A dictionary (nested dictionary or flat dot notation or even mixed)
    :param field_name: Optional parameter to use as initial prefix for dotted
        path
    """ 
    for key, value in d.iteritems():
        assert u'.' not in key, u'walk() doesn\'t accept key in dot notation: %s' % key
        if hasattr(value, u'iteritems'):
            for pair in walk(value, key):
                yield pair
        else:
            yield (u'%s.%s' % (field_name, key) if field_name else key,
                   value)

def map_dict(dict, fn):
    new_dict = {}
    for key, value in dict.iteritems():
        if isinstance(value, collections.MutableMapping):
            value = map_dict(value, fn)
        new_key, new_value = fn(key, value)
        new_dict[new_key] = new_value
    return new_dict

def without(d, exclude_keys):
    for key in exclude_keys:
        if key in d:
            del d[key]
    return d

def _get_container_and_key(doc, key):
    container = doc
    while u'.' in key:
        key, sep, rest = key.partition(u'.')
        try:
            key = int(key)
        except ValueError:
            pass
    
        if key not in container.keys():
            raise KeyError()
        
        if rest:
            container = container.__getitem__(key)
            key = rest
            
    return container, key


def getitem(doc, key):
    """ Get the value of `key` in dictionary `doc` (optionally in dotted
    notation).
        
    Examples for keys of dictionary `doc`:
     * doc['a'] -> doc['a']
     * doc['a.b'] -> doc['a']['b']  # b is interpreted as dictionary key
     * doc['a.2'] -> doc['a'][2]    # 1 is interpreted as list index
    """
    container, key = _get_container_and_key(doc, key)

    # Make sure we don't get in the way of subclass implementations of 
    # __getitem__()
    return dict.__getitem__(container, key)

def setitem(doc, key, value):
    """ Set the value of `key` in dictionary `doc` (optionally in dotted notation).
    """
    container = doc
    rest = key
    while rest:
        key, sep, rest = rest.partition(u'.')
        try:
            key = int(key)
        except ValueError:
            pass
        
        if rest:
            rest_key, sep, rest_rest = rest.partition(u'.')
            try:
                index = int(rest_key)
                try:
                    sub_container = container.__getitem__(key)
                    cnt_len = len(sub_container)
                    sub_container[cnt_len:index+1] = [None]*(index+1-cnt_len)
                except KeyError:
                    dict.__setitem__(container, key, [None]*(index+1))
            except ValueError:
                if key not in container.keys():
                    dict.__setitem__(container, key, dict())
            container = dict.__getitem__(container, key)

    container.__setitem__(key, value)

def delitem(doc, key):
    container, key = _get_container_and_key(doc, key)

    dict.__delitem__(container, key)

def contains(doc, key):
    container, key = _get_container_and_key(doc, key)
    return dict.__contains__(container, key)
