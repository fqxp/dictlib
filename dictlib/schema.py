#from bson.objectid import ObjectId
from dictlib.utils import update_recursive
from pymongo.objectid import ObjectId
from types import TypeType, NoneType
import datetime
import dateutil.parser
    
class ValidationError(Exception):
    pass

class SchemaFieldNotFound(Exception):
    pass

class Field(object):
    description = None
    title = None
    
    """ The base class for fields in a `DictSchema`.
    """
    def __init__(self, optional=False, default=None, can_be_none=False,
                 title=None, description=None):
        """ Constructor.
         
        :param optional: Whether this field must exist (`False`) or may not
            exist (`True`).
        :param default: The default value if this field is unset (default: `None`).
        :param can_be_none: Whether the value of this field may have a value of
            `None`.
        """
        self.optional = optional
        self.default = default
        self.can_be_none = can_be_none
        self.title = title
        self.description = description or self.description
    
    def validate(self, value, field_name, partial=False):
        """ Validate the field. Subclasses must invoke this method subsequently.
        """
        if value is None and not self.can_be_none:
            raise ValidationError(u'Field %s: Value cannot be None' % field_name)
        
    def from_json(self, v):
        """ Process value `v` from a dictionary decoded from JSON and convert
        it to the program-internal representation. By default, this simply
        returns the value itself.
        
        :todo: Rename this method?
        """
        return v
    
    def to_json(self, v):
        """ Convert value `v` to a JSON-encodable type. Re-implement in your
        subclass if your type is not normally representable in JSON.

        :todo: Rename this method?
        """ 
        return v
    

class TypeField(Field):
    """ A `TypeField` is a field that has a specific Python type.
    """
    type_ = None

    def validate(self, value, field_name=None, partial=False):
        super(TypeField, self).validate(value, field_name, partial)
        if not isinstance(value, self.type_) and \
                not (value is None and self.can_be_none):
            raise ValidationError(u'Field %s: Value %r has wrong type %s' %
                                  (field_name, value, type(value)))
            
    def __unicode__(self):
        return u'<TypeField: type=%s>' % self.type_
    
class FieldField(TypeField):
    type_ = Field

class AnyField(Field):
    pass
            
class NoneField(TypeField):
    """ A schema field with type None, i. e. a field that can only be `None`.
    """
    type_ = NoneType
    
    def __init__(self, optional=False, default=None, title=None, description=None):
        super(NoneField, self).__init__(optional=optional, default=default, 
                                        can_be_none=True)

class AbstractNumericField(TypeField):
    def __init__(self, optional=False, default=None, can_be_none=False,
                 min=None, max=None, description=None):
        super(AbstractNumericField, self).__init__(optional=optional, default=default,
                                                   can_be_none=can_be_none)
        self.min = min
        self.max = max
        
    def validate(self, field_value, field_name=None, partial=False):
        super(AbstractNumericField, self).validate(field_value, field_name, partial)
        if self.min is not None and field_value < self.min:
            raise ValidationError(u'Field %s: Value %s is smaller than %r' % self.min)
        if self.max is not None and field_value > self.max:
            raise ValidationError(u'Field %s: Value %s is larger than %r' % self.max)

class IntField(AbstractNumericField):
    """ A schema field for `long` values.
    """
    type_ = int
    
class LongField(AbstractNumericField):
    """ A schema field for `long` values.
    """
    type_ = long
    
class FloatField(AbstractNumericField):
    """ A schema field for `float` values.
    """
    type_ = float
    
class UnicodeField(TypeField):
    """ A schema field for `unicode` values.
    """
    type_ = unicode
    
class ObjectIdField(TypeField):
    """ A schema field for `ObjectId` values.
    
    Values are JSON-encoded to unicode values.
    """
    type_ = ObjectId
    
    def from_json(self, v):
        return ObjectId(v) if v else None
    
    def to_json(self, v):
        return unicode(v) if v else None

class DatetimeField(TypeField):
    """ A schema field for `datetime` values.
    
    Values are JSON-encoded to unicode values in ISO date/time format.
    """
    type_ = datetime.datetime
    
    def from_json(self, v):
        return dateutil.parser.parse(v) if v else None
    
    def to_json(self, v):
        return v.isoformat() if v else None
    
class EnumField(Field):
    """ A scheme field accepting values from a given list of possible values 
    only. 
    """
    def __init__(self, *args, **kwargs):
        """ Constructor. The list of non-keyword arguments provided is the list
        of possible values for this field. Keyword arguments are as in the 
        superclasses.
        """
        super(EnumField, self).__init__(**kwargs)
        self.values = args
        
    def validate(self, field_value, field_name=None, partial=False):
        if field_value not in self.values:
            raise ValidationError(u'Field %s: Value %r not allowed' %
                                  (field_name, field_value))
    
class ListField(TypeField):
    """ A schema field taking for lists.
    """
    type_ = list
    
    def __init__(self, fields=None, optional=False, default=[], min_len=0, 
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
        super(ListField, self).__init__(optional=optional, default=default,
                                        can_be_none=can_be_none)
        if type(fields) not in (list, tuple):
            fields = [fields]
        self.fields = fields
        self.min_len = min_len
        self.max_len = max_len

    def from_json(self, v):
        assert type(v) in (list, tuple)
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
        assert type(v) in (list, tuple)
        for i, value in enumerate(v[:]):
            for field in self.fields:
                if type(value) is field.type_:
                    v[i] = field.to_json(value)
                    break
        return v
        
    def validate(self, field_value, field_name=None, partial=False):
        super(ListField, self).validate(field_value, field_name)
        
        if len(field_value) < self.min_len:
            raise ValidationError(u'Field %s: List has too few elements (%d)' % 
                                  (field_name, len(field_value)))
        if self.max_len is not None and len(field_value) > self.max_len:
            raise ValidationError(u'Field %s: List has too many elements (%d)'
                                  % (field_name, len(field_value)))
        
        for i, value in enumerate(field_value):
            validated = False
            for field in self.fields:
                if hasattr(field, u'type_') and type(value) is field.type_:
                    field.validate(value, field_name=u'%s[%d]' % (field_name, i))
                    validated = True
                    break

            # Extra-check enum fields because they have no type_ field to 
            # check against             
            if not validated:
                for enum_field in filter(lambda t: t.__class__ is EnumField, self.fields):
                    enum_field.validate(value, field_name='%s[%d]' % (field_name, i))
                    validated = True
                    break
                
            if not validated:
                raise ValidationError(u'Field %s[%d]: field_value %r has none of the listed fields' %
                                      (field_name, i, value))
 

class DictField(TypeField):
    type_ = dict
    
    def __init__(self, schema=None, **kwargs):
        super(DictField, self).__init__(**kwargs)

        self._schema = {}
        for cls in filter(lambda cls: hasattr(cls, u'schema'), self.__class__.__mro__):
            self._schema = update_recursive(cls.schema, self._schema)

        if schema:
            update_recursive(self._schema, schema)
            
        self._mangle_schema()

    def _mangle_schema(self, _schema=None):
        if _schema is None:
            _schema = self._schema
        for key, value in _schema.iteritems():
            if isinstance(value, dict):
                self._mangle_schema(value)
                _schema[key] = DictField(value)
            if isinstance(value, (list, tuple)):
                _schema[key] = ListField(*value)
            
    def validate(self, field_value, field_name=None, partial=False):
        super(DictField, self).validate(field_value, field_name, partial)

        type_field_names = set()
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
            
        if not partial:
            for key, field in self._schema.iteritems():
                full_field_name = u'%s%s' % (u'%s.' % field_name if field_name else u'', 
                                             key)
                if type(key) is TypeType:
                    if not field.optional and not any(type(fn) is key for fn in type_field_names):
                        raise ValidationError(u'At least one field with key of type %s is required' % key)
                elif not field.optional and key not in field_value:
                    raise ValidationError(u'Field \'%s\' is missing' % full_field_name)

    def from_json(self, v):
        """ Process value `v` from a dictionary decoded from JSON and convert
        it to the program-internal representation. By default, this simply
        returns the value itself.
        
        :todo: Rename this method?
        """
        for key, value in v.iteritems():
            yield (key, self.get_field(key).from_json(value))
    
    def to_json(self, v):
        """ Convert value `v` to a JSON-encodable type. Re-implement in your
        subclass if your type is not normally representable in JSON.

        :todo: Rename this method?
        """ 
        for key, value in v.iteritems():
            yield (key, self.get_field(key).to_json(value))

    def get_field(self, key):
        if key in self._schema:
            return self._schema[key]
        elif type(key) in self._schema:
            return self._schema[type(key)]
        else:
            raise SchemaFieldNotFound(u'Key %s not defined in schema' % key)

    def get_schema(self):
        """ Returns the mangled schema.
        """
        return self._schema


class Schema(DictField):
    def __init__(self, schema=None, description=None):
        super(Schema, self).__init__(schema, optional=False, default={}, can_be_none=False,
                                     description=None)

    def create(self, default={}, factory=dict, _subschema=None):
        """ Create a document from this schema by using the default values from
        the schema, possibly overwriting them with the default values from the
        `default` parameter and leaving out any optional fields.
        
        :default: A dictionary of default values which overrule the default
            values from the schema description. Default: empty.
        :return: A newly created dictionary matching the structure of the schema.
        """
        schema = _subschema or self._schema
        doc = factory()
        
        for key, field in schema.iteritems():
            if type(key) is TypeType:
                continue
            
            if not field.optional:
                if isinstance(field, DictField):
                    doc[key] = self.create(default.get(key, {}), 
                                           _subschema=field._schema)
                elif hasattr(field.default, u'__call__'):
                    doc[key] = field.default()
                else:
                    doc[key] = field.default
                
        update_recursive(doc, default)
                
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
        try:
            self.validate(doc, partial=True)
            return True
        except ValidationError:
            return False
################################################################################

#class SchemaFormInvalid(Exception):
#    pass
#
#class SchemaForm(object):
#    schema = None
#    # Field names in dot separated notation
#    include = []
#    exclude = []
#    
#    def __init__(self, data):
#        """
#        :param data: Either a dictionary or a string containing a JSON 
#            dictionary.
#        """
#        self.errors = []
#        if not isinstance(data, dict):
#            data = self.load_json(data)
#        self.data = self._decode_json_dict(data)
#
#    def is_valid(self):
#        self.errors = []
#        
#        for path, value in walk(self.data):
#            if self.exclude and path in self.exclude:
#                raise SchemaFormInvalid(u'Form var %s excluded from form' % path)
#            elif self.include and path not in self.include:
#                raise SchemaFormInvalid(u'Form var %s not included from form' % path)
#
#            try:      
#                self.schema.get_field(path).validate(value)
#            except SchemaFieldNotFound as e:
#                self.errors.append(unicode(e))
#            except ValidationError as e:
#                self.errors.append(unicode(e))
#                
#        return not self.errors
#    
#    def load_json(self, s):
#        doc = json.loads(s) #, object_hook=json_util.object_hook)
#        return self._decode_json_dict(doc)
#    
#    def _decode_json_dict(self, doc, _subschema=None):
#        schema = _subschema or self.schema.get_schema()
#        decoded_doc = {}
#        
#        for key, value in doc.iteritems():
#            try:
#                field = self.schema.get_field(key, schema)
#                
#                if type(field) is DictType:
#                    decoded_doc[key] = self._decode_json_dict(value, field)
#                else:
#                    decoded_doc[key] = field.from_json(value)
#            except SchemaFieldNotFound:
#                # Unknown field - we'll leave it as it is
#                decoded_doc[key] = value
#                
#        return decoded_doc
#
#    def dump_json(self, doc):
#        return json.dumps(self._encode_json_dict(doc))
#
#    def _encode_json_dict(self, doc, _subschema=None):
#        schema = _subschema or self.schema.get_schema()
#        encoded_doc = {}
#        
#        for key, value in doc.iteritems():
#            try:
#                field = self.schema.get_field(key, schema)
#                
#                if type(field) is DictType:
#                    encoded_doc[key] = self._encode_json_dict(value, field)
#                else:
#                    encoded_doc[key] = field.to_json(value)
#            except SchemaFieldNotFound:
#                encoded_doc[key] = value
#
#        return encoded_doc


###############################################################################

class MongoDbSchema(Schema):
    schema = {
        u'_id': ObjectIdField(optional=True),
    }

class CouchDbSchema(Schema):
    schema = {
        u'_id': UnicodeField(optional=True),
        u'_rev': UnicodeField(optional=True)}

#class AbstractNeteSchema(MongoDbSchema):
#    schema = {
#        u'name': UnicodeField(),
#        u'created': DatetimeField(default=datetime.datetime.utcnow),
#        u'updated': DatetimeField(can_be_none=True),
#        u'content_type': UnicodeField(default=u'text/html'),
#        u'links': ListField([ObjectIdField(), NoneField()]),
#        u'tags': ListField([EnumField(u'interesting', u'boring'), 
#                            ObjectIdField()]),
#    }
    
#class NoteSchema(AbstractNeteSchema):
#    schema = {
#        u'text': UnicodeField(),
#    }
#
#class NoteSchemaForm(SchemaForm):
#    schema = NoteSchema()
#    include = [u'name', u'content_type', u'text', u'links', u'tags',]

#===============================================================================
# class NoteSchema(DictSchema):
#    schema = {
#        u''
#    }
#===============================================================================

if __name__ == u'__main__':
    schema = NoteSchema()
    
##    d2 = schema.create({u'name': u'First test',
##                        u'text': u'First texxxxxxxxxxxxxxxxxxt',
##                        u'links': [ObjectId(), None],
##                        u'tags': [u'interesting', ObjectId()],
##                        })
#    print d2
#    schema.validate(d2)