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

from dictlib.exceptions import ValidationError, SchemaFieldNotFound
from dictlib.utils import update_recursive
import collections
import datetime
import re
import time
import types

class SchemaDefinitionError(Exception):
    pass

class Field(object):
    """ The base class for schema fields. Do not use this class directly, but
    only its subclasses.
    """ 
    default = None
    can_be_none = False
    description = None
    title = None
    optional = False
    
    """ The base class for fields in a `DictSchema`.
    """
    def __init__(self, optional=None, default=None, can_be_none=None,
                 title=None, description=None):
        """ Constructor.
         
        :param optional: Whether this field must exist (`False`) or may not
        exist (`True`).
        :param default: The default value if this field is unset (default: `None`).
        :param can_be_none: Whether the value of this field may have a value of
        `None`.
        :param title: An optional title for this field.
        :param description: An optional long description of this field.
        """
        self.optional = optional if optional is not None else self.optional
        self.default = default if default is not None else self.default
        self.can_be_none = can_be_none if can_be_none is not None else self.can_be_none
        self.title = title if title is not None else self.title
        self.description = description if description is not None else self.description
    
    def validate(self, value, field_name=u'', partial=False):
        """ Validate the field. Subclasses should invoke their parent's
        `validate()` method subsequently.
        
        :raises: `ValidationError` if the given `value` is invalid.
        """
        if value is None and not self.can_be_none:
            raise ValidationError(u'Field %s: Value cannot be None' % field_name)
        
    def from_json(self, value):
        """ Process value `value` from a dictionary decoded from JSON and 
        convert it to the program-internal representation. By default, this 
        simply returns the value itself. 
        
        :param value: The value to convert from JSON format.
        """
        return value
    
    def to_json(self, value):
        """ Convert value `value` to a JSON-encodable type. Re-implement in your
        subclass if your type is not normally representable in JSON.

        :param value: The value to convert to JSON format.
        """
        return value
    
    def __unicode__(self):
        return u'<%s: optional=%r default=%r can_be_none=%r title=%s description=%s>' % (
                self.__class__.__name__,
                self.optional, self.default, self.can_be_none, self.title,
                self.description)

class AnyField(Field):
    """ A field that can hold any value of any type.
    """
    pass

class TypeField(Field):
    """ A `TypeField` is an abstract baseclass for schema fields that have a specific 
    Python type.
    """
    type = None

    def validate(self, value, field_name=None, partial=False):
        super(TypeField, self).validate(value, field_name, partial)
        if not isinstance(value, self.type) and \
                not (value is None and self.can_be_none):
            raise ValidationError(u'Field %s: Value %r has wrong type %s' %
                                  (field_name, value, type(value)))

class FieldField(TypeField):
    """ A `FieldField` can only have a `Field` instance as a value. This is
    used to convert schema definitions themselves.
    """
    type = Field
            
class NoneField(TypeField):
    """ A schema field with type None, i. e. a field that can only be `None`.
    """
    type = types.NoneType

    def __init__(self, optional=False, default=None, title=None, description=None):
        super(NoneField, self).__init__(optional=optional, default=default, 
                                        can_be_none=True, title=title,
                                        description=description)

class AbstractNumericField(TypeField):
    """ The base class for numeric schema fields. In addition to the default
    parameters, numeric fields have `min` and `max` constructor parameters.
    """
    def __init__(self, optional=False, default=None, can_be_none=False,
                 min=None, max=None, title=None, description=None):
        """ See `TypeField`.
        
        :param min: Minimum value this field may have.
        :param max: Maximum value this field may have.
        """
        super(AbstractNumericField, self).__init__(optional=optional, default=default,
                                                   can_be_none=can_be_none,
                                                   title=title,
                                                   description=description)
        self.min = min
        self.max = max
        
    def validate(self, field_value, field_name=None, partial=False):
        super(AbstractNumericField, self).validate(field_value, field_name, partial)
        if field_value is None and self.can_be_none:
            return

        if self.min is not None and field_value < self.min:
            raise ValidationError(u'Field %s: Value %s is smaller than %r' % (field_name, field_value, self.min))
        if self.max is not None and field_value > self.max:
            raise ValidationError(u'Field %s: Value %s is larger than %r' % (field_name, field_value, self.max))

class IntField(AbstractNumericField):
    """ A schema field for `int` values.
    """
    type = int
    
class LongField(AbstractNumericField):
    """ A schema field for `long` values.
    """
    type = long
    
class FloatField(AbstractNumericField):
    """ A schema field for `float` values.
    """
    type = float
    
class UnicodeField(TypeField):
    """ A schema field for `unicode` values.
    """
    type = unicode
    length = None
    min_len = None
    max_len = None
    match = None
    
    def __init__(self, optional=False, default=None, can_be_none=False,
                 length=None, min_len=None, max_len=None, match=None,
                 title=None, description=None):
        """ See parameters, see `TypeField`.
        
        :param match: A regular expression values of this field must match.
        """
        super(UnicodeField, self).__init__(optional=optional, default=default, 
                                           can_be_none=can_be_none, title=title, 
                                           description=description)
        self.length = length if length is not None else self.length
        self.min_len = min_len if min_len is not None else self.min_len
        self.max_len = max_len if max_len is not None else self.max_len
        self.match = match if match is not None else self.match
        
    def validate(self, value, field_name=None, partial=False):
        super(UnicodeField, self).validate(value, field_name, partial)
        if value is None and self.can_be_none:
            return
        
        if self.length is not None and len(value) != self.length:
            raise ValidationError(u'Field %s: Value %s should have length %d' %
                                  (field_name, value, self.length))
        else:
            if self.min_len is not None and len(value) < self.min_len:
                raise ValidationError(u'Field %s: Value %s is shorter than min length %d' %
                                      (field_name, value, self.min_len))
            if self.max_len is not None and len(value) > self.max_len:
                raise ValidationError(u'Field %s: Value %s is longer than max length %d' %
                                      (field_name, value, self.max_len))
            if self.match and not self.match.match(value):
                raise ValidationError(u'Field %s: Value %s has wrong format' %
                                      (field_name, value))
                
    def from_json(self, v):
        if type(v) is str:
            return v.decode(u'utf-8')
        else:
            return v
    
    def to_json(self, v):
        if type(v) is unicode:
            return v.encode(u'utf-8')
        else:
            return v
            
class UuidField(UnicodeField):
    """ A field that only may hold UUID4 values, i. e. 256-bit values as
    32-character hexedecimal strings.
    """
    match = re.compile(ur'[0-9a-f]{32}')
    length = 32

class EmailField(UnicodeField):
    """ A field that only may hold UUID4 values, i. e. 256-bit values as
    32-character hexedecimal strings.
    """
    match = re.compile(ur'.+@.+')

class BaseDatetimeField(TypeField):
    """ A base class for schema fields for `datetime` values.
    
    Values are JSON-encoded to unicode values in ISO date/time format.
    """
    def from_json(self, v):
        timetuple = time.strptime(v, self.dt_format)
        return self.type(*timetuple[self.struct_time_index[0]:self.struct_time_index[1]])
    
    def to_json(self, v):
        return v.strftime(self.dt_format)

class DatetimeField(BaseDatetimeField):
    """ A schema field for date/time values. JSON datetimes must be strings in
    the format *YYYY-MM-DDThh-mm-ssZ*.
    """
    type = datetime.datetime
    dt_format = u'%Y-%m-%dT%H:%M:%SZ'
    struct_time_index = (0, 6)

class DateField(BaseDatetimeField):
    """ A schema field for date/time values. JSON datetimes must be strings in
    the format *YYYY-MM-DD*.
    """
    type = datetime.date
    dt_format = u'%Y-%m-%d'
    struct_time_index = (0, 3)

class TimeField(BaseDatetimeField):
    """ A schema field for date/time values. JSON datetimes must be strings in
    the format *hh-mm-ss*.
    """
    type = datetime.time
    dt_format = u'%H:%M:%S'
    struct_time_index = (3, 6)

class ListField(TypeField):
    """ A schema field for lists.
    """
    type = list

    def __init__(self, fields=None, optional=False, default=None, min_len=0, 
                 max_len=None, can_be_none=False, title=None, description=None):
        """ Constructor.

        :param fields: A list of possible fields for the elements of the list.
        :param optional: Whether the field may be missing.
        :param default: A default value for this field. Default: `[]`.
        :param min_len: The minimum length of the list. Default: `0`.
        :param max_len: The maximum length of the list. `None` means infinite.
        Default: `None`.
        :param can_be_none: Whether the value of the field may be `None` instead
        of a list.
        """
        super(ListField, self).__init__(optional=optional, default=default or [],
                                        can_be_none=can_be_none)
        if fields is None:
            fields = [AnyField()]
        elif not isinstance(fields, collections.Sequence):
            fields = [fields]
        self.fields = fields
        self.min_len = min_len
        self.max_len = max_len

    def from_json(self, v):
        assert isinstance(v, collections.Sequence)
        for i, value in enumerate(v[:]):
            # The first type that can handle this value wins
            for field in self.fields:
                try:
                    v[i] = field.from_json(value)
                    break
                except:
                    pass
        return v
    
    def to_json(self, v):
        assert isinstance(v, collections.Sequence)
        for i, value in enumerate(v[:]):
            for field in self.fields:
                if isinstance(value, field.type):
                    v[i] = field.to_json(value)
                    break
        return v
        
    def validate(self, field_value, field_name=None, partial=False):
        super(ListField, self).validate(field_value, field_name)

        # Validate list length
        if self.min_len is not None and len(field_value) < self.min_len:
            raise ValidationError(u'Field %s: List has too few elements (%d)' % 
                                  (field_name, len(field_value)))
        if self.max_len is not None and len(field_value) > self.max_len:
            raise ValidationError(u'Field %s: List has too many elements (%d)'
                                  % (field_name, len(field_value)))
        
        # Check type of each list item
        for i, value in enumerate(field_value):
            is_valid = False
            for field in self.fields:
                #if hasattr(field, u'type') and isinstance(value, field.type):
                try:
                    field.validate(value, field_name=u'%s[%d]' % (field_name, i))
                    is_valid = True
                    break
                except ValidationError:
                    pass

            if not is_valid:
                raise ValidationError(u'Field %s[%d]: field_value %r has none of the listed fields' %
                                      (field_name, i, value))

class DictField(TypeField):
    """ A `DictField` is used for building nested schemas. You could either
    insert direct `DictField` instances to a schema, or you could subclass
    `DictField` and re-use it in several schemas.
    """
    type = collections.MutableMapping
    _schema = {}

    def __init__(self, schema=None, **kwargs):
        super(DictField, self).__init__(**kwargs)

        # Update schema definition from base classes, enabling sub-classing
        # of schemas
        self._schema = {}
        for cls in reversed(filter(lambda cls: hasattr(cls, u'schema'), 
                                   self.__class__.__mro__)):
            if not isinstance(cls.schema, initial):
                raise SchemaDefinitionError(u'schema attribute in %s '
                                            u'is not a initial, but should be' %
                                            cls.__name__)
            self.extend(cls.schema)
        if schema:
            self.extend(schema)

    def extend(self, other_schema):
        """ Extend (overwrite) the current schema with fields from another
        schema.
        
        :param other_schema: Either a `DictField` instance or a dict schema
        definition
        :raises SchemaDefinitionError: If there is an error in the schema 
        definition
        """
        if isinstance(other_schema, Schema):
            other_schema = other_schema.schema
        for key, field in other_schema.iteritems():
            if not isinstance(field, (Field, dict)):
                raise SchemaDefinitionError(u'Schema attribute %s is not a Field' %
                                            key)
            # Recursively 
            if isinstance(field, (DictField, dict)) and \
                    key in self._schema and \
                    isinstance(self._schema[key], DictField):
                self._schema[key].extend(field._schema)
            else:
                self._schema[key] = field

        self._schema = self._mangle_schema(self._schema)

    def _mangle_schema(self, schema):
        # Take care that _mangle_schema(_mangle_schema(schema)) == _mangle_schema(schema)
        # for all values of schema
        # Convert all dictionaries in the schema definition by DictFields
        mangled_schema = {}
        if isinstance(schema, DictField):
            schema = schema._schema
        for key, value in schema.iteritems():
            if isinstance(value, dict):
                mangled_subschema = self._mangle_schema(value)
                mangled_schema[key] = DictField(mangled_subschema)
            else:
                mangled_schema[key] = value
        return mangled_schema

    def validate(self, field_value, field_name=None, partial=False):
        super(DictField, self).validate(field_value, field_name, partial)

        if field_value is None and self.can_be_none:
            return

        type_field_names = set()
        # For all keys in the document, check if they are defined in the schema
        for key, value in field_value.iteritems():
            full_field_name = u'%s%s' % (u'%s.' % field_name if field_name else u'', 
                                         key)
            try:
                field = self.get_field(key)
                field.validate(value, full_field_name, partial)
                if key not in self._schema:
                    type_field_names.add(key)
            except SchemaFieldNotFound:
                raise ValidationError(u'Field \'%s\' not defined in schema' % full_field_name)
            
        # Check if all required keys are present in the document
        if not partial:
            for key, field in self._schema.iteritems():
                full_field_name = u'%s%s' % (u'%s.' % field_name if field_name else u'', 
                                             key)
                if isinstance(key, types.TypeType):
                    if not field.optional and not any(isinstance(fn, key) for fn in type_field_names):
                        raise ValidationError(u'At least one field with key of type %s is required' % key)
                elif not field.optional and key not in field_value:
                    raise ValidationError(u'Field \'%s\' is missing' % full_field_name)

    def from_json(self, v):
        doc = {}
        for key, value in v.iteritems():
            key = key.decode(u'utf-8') if isinstance(key, str) else key
            doc[key] = self.get_field(key).from_json(value)
        return doc
    
    def to_json(self, v):
        return dict((key.encode(u'utf-8'), self.get_field(key).to_json(value))
                    for key, value in v.iteritems())

    def get_field(self, key):
        """ Return the field definition for `key`.
        
        :param key: A key defined in the dictionary
        :return: An `Field` subclass instance
        :raises KeyError: If `key` is not defined in the schema
        """
        if key in self._schema:
            return self._schema[key]
        elif type(key) in self._schema:
            return self._schema[type(key)]
        else:
            raise SchemaFieldNotFound(u'Key %s not defined in schema' % key)

    def get_schema(self):
        """ Returns the mangled schema definition.
        """
        return self._schema

class Schema(DictField):
    """ A definition of a schema. Either derive from this class and set the
    `schema` attribute statically or use `Schema` directly and provide a
    `schema` argument.
    """
    def __init__(self, schema=None, title=None, description=None):
        """
        :param schema: A schema definition. This is a dictionary with field name/
        field type to `Field` instance mapping, possibly nested.
        :see: Field
        """
        super(Schema, self).__init__(schema, optional=False, default={}, can_be_none=False,
                                     title=title, description=description)

    def create(self, initial=None, _subschema=None):
        """ Create a document from this schema by using the initial values from
        the schema, possibly overwriting them with the initial values from the
        `initial` parameter and leaving out any optional fields.
        
        :initial: A dictionary of initial values which overrule the initial
        values from the schema description. Default: empty.
        :return: A newly created dictionary matching the structure of the schema.
        """
        schema = _subschema or self._schema
        initial = initial if initial is not None else {}
        doc = {}
        
        for key, field in schema.iteritems():
            # Do not create default dictionary if key is a type, e.g. 
            # unicode, since we don't know a key name
            if isinstance(key, types.TypeType):
                continue
            
            if not field.optional:
                if isinstance(field, DictField):
                    doc[key] = self.create(initial.get(key, {}),
                                           _subschema=field._schema)
                elif hasattr(field.default, u'__call__'):
                    doc[key] = field.default()
                else:
                    doc[key] = field.default
                
        update_recursive(doc, initial)
                
        return doc

    def is_valid(self, doc):
        """ Check if the `doc` dictionary is a valid schema instance.

        :param doc: A nested dictionary.
        :return: `True` if the `doc` is valid, `False` otherwise.
        """
        try:
            self.validate(doc)
            return True
        except ValidationError:
            return False
        
    def is_partially_valid(self, doc):
        """ Check if `doc` partially matches the schema. A partial match only
        checks if the fields in `doc` match the schema, but not if all required
        fields are present. This may be useful for updating documents.
        """
        try:
            self.validate(doc, partial=True)
            return True
        except ValidationError:
            return False
        
class AnySchema(Schema):
    """ A schema that matches all kinds of documents.
    """
    schema = {unicode: AnyField(optional=True)}