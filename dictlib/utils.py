# -*- coding: utf-8 -*-
#
# This file is part of dictlib.
#
# Copyright (C) 2011  Frank Ploss
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

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
        yield (u'%s.%s' % (field_name, key) if field_name else key,
               value)
        if hasattr(value, u'iteritems'):
            for pair in walk(value, key):
                yield pair

def map_dict(doc, fn):
    """ Return a new directory where each key/value pair is replaced by the
    result `(key, value)` tuple of the mapping function `fn`.

    As an example for encoding all unicode keys in a dictionary to UTF-8
    encoded byte-strings:
    >>> d = {u'a': {u'b': 42}}
    >>> map_dict(d, lambda k,v: (unicode(k) if type(k) is unicode else k, v))
    {'a': {'b': 42}}

    :param doc: A dictionary to apply the mapping function to.
    :param fn: A mapping function which has the signature `fn(key,value)->(key,value)`
    """
    new_dict = {}
    for key, value in doc.iteritems():
        if isinstance(value, collections.Mapping):
            new_value = map_dict(value, fn)
            new_key, _ = fn(key, None)
        else:
            new_key, new_value = fn(key, value)
        new_dict[new_key] = new_value
    return new_dict



def _get_container_and_key(doc, key):
    """ For a (possibly) dotted `key`, return the value in `doc`.
    """
    container = doc
    while u'.' in key:
        key, _, rest = key.partition(u'.')
        try:
            index = int(key)
            container = container.__getitem__(index)
        except ValueError:
            if key not in container.keys():
                raise KeyError()
            container = container.__getitem__(key)
        key = rest

    try:
        return container, int(key)
    except ValueError:
        return container, key

def getitem(doc, key):
    """ Get the value of `key` in dictionary `doc` (optionally in dotted
    notation).

    Examples for keys of dictionary `doc`:
     - doc['a'] -> doc['a']
     - doc['a.b'] -> doc['a']['b']  # b is interpreted as dictionary key
     - doc['a.2'] -> doc['a'][2]    # 1 is interpreted as list index
    """
    container, key = _get_container_and_key(doc, key)

    # Make sure we don't get in the way of subclass implementations of
    # __getitem__()
    return container.__getitem__(key)

def throws(excs, f, *args, **kwargs):
    """ Execute `f` with the `args` and `kwargs` as parameters and return
    `True` if the call raised an exception in `exc`. Return `False` if `f`
    returned without an exception. If an exception not in `excs` is raised,
    it will be re-raised.

    :param excs: A list of exception classes or a single exception class
    :param f: A callable
    :param *args: Any non-keyword arguments
    :param *kwargs: Any keyword arguments
    """
    if not isinstance(excs, collections.Sequence):
        excs = [excs]
    try:
        f(*args, **kwargs)
        return False
    except Exception as e:
        if e.__class__ in excs:
            return True
        else:
            raise e

def setitem(doc, key, value):
    """ Set the value of `key` in dictionary `doc` (optionally in dotted
    notation).

    :raises KeyError: If the `key` was not found in `doc`
    :todo: Make this much faster
    """
    container = doc
    rest = key
    while rest:
        key, _, rest = rest.partition('.')
        try:
            key = int(key)
        except ValueError:
            pass

        if rest:
            rest_key, _, _ = rest.partition('.')
            # Handle non-existing sub-container
            if throws([IndexError, KeyError], container.__getitem__, key):
                try:
                    # Check if sub-key is integer
                    int(rest_key)
                    # If it is, create an empty list
                    sub_container = list()
                except ValueError:
                    # Assume it's a dict
                    sub_container = dict()

                if isinstance(container, collections.MutableSequence) and key == len(container):
                    container.__setslice__(key, key+1, [sub_container])
                else:
                    container.__setitem__(key, sub_container)

            container = container.__getitem__(key)

    if isinstance(container, collections.MutableSequence) and key == len(container):
        container.__setslice__(key, key+1, [value])
    else:
        container.__setitem__(key, value)

def delitem(doc, key):
    container, key = _get_container_and_key(doc, key)

    container.__delitem__(key)

def contains(doc, key):
    container, key = _get_container_and_key(doc, key)
    return container.__contains__(key)

def without(doc, key):
    doc_without = doc.copy()

    if key in doc_without:
        del doc_without[key]

    return doc_without
