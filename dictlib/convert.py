from dictlib.mixins import DotNotationAdapter
from dictlib.utils import walk
from dictlib.schema import AbstractNumericField, ListField, UnicodeField,\
    DictField, Schema, FieldField, NoneField, AnyField

class Converter(object):
    # Fields to exclude when converting to JSON (in dot notation)
    exclude = set()
    rename = list()
    
    def __init__(self, schema, exclude=[], rename=(), factory=dict):
        self.schema = schema
        self.exclude.update(exclude)
        self.rename.extend(rename)
        self.factory = factory
        self.rename_inv = list((v, k) for k, v in self.rename)
        
    def to_json(self, doc):
        json_doc = DotNotationAdapter(dict(self.schema.to_json(doc)))
        # Rename keys
        for rename_key, rename_value in self.rename:
            if rename_key in json_doc:
                json_doc[rename_value] = json_doc[rename_key]
                del json_doc[rename_key]
        # Exclude fields
        for key, value in walk(json_doc):
            if self.exclude_field(json_doc, key):
                del json_doc[key]
        return json_doc

    def from_json(self, json_doc):
        for rename_key, rename_value in self.rename_inv:
            if rename_key in json_doc:
                json_doc[rename_value] = json_doc[rename_key]
                del json_doc[rename_key]
        return self.factory(self.schema.from_json(json_doc))

    def exclude_field(self, json_doc, key):
        return key in self.exclude
    


"""

schema = {
    'a': UnicodeField(),
    'b': DictField({'c': UnicodeField()}
}
->



"""
class JsonSchemaSchema(Schema):
    schema = {
        unicode: FieldField(optional=True),
    }
    
class JsonSchemaConverter(Converter):
    """ A basic `Schema` to JSON Schema converter.
    
    For reference, see http://tools.ietf.org/html/draft-zyp-json-schema-03
    
    Some features that don't work yet include:
    * exclusive[Mininum,Maximum,minLength,maxLength]
    * enum on any list
    * AnyField (partially)
    """
    def __init__(self):
        super(JsonSchemaConverter, self).__init__(JsonSchemaSchema(), exclude=[], rename=(), factory=dict)
    
    def to_json(self, schema):
        schema = Schema(super(JsonSchemaConverter, self).to_json(schema.get_schema()))
        return self._field_to_json(schema)

    def _field_to_json(self, field):
        json_schema_doc = {}
        if not field.optional:
            json_schema_doc[u'required'] = True
        if field.title is not None:
            json_schema_doc[u'title'] = field.title
        if field.description is not None:
            json_schema_doc[u'description'] = field.description
        if field.default is not None:
            json_schema_doc[u'default'] = field.default

        if isinstance(field, DictField):
            json_schema_doc[u'type'] = u'object'
            json_schema_doc[u'properties']= {}
            for subfield_name, subfield in field.get_schema().iteritems():
                json_schema_doc[u'properties'][subfield_name] = self._field_to_json(subfield)
        elif isinstance(field, ListField):
            json_schema_doc[u'type'] = u'array'
            if field.min_len is not None:
                json_schema_doc[u'minItems'] = field.min_len
            if field.max_len is not None:
                json_schema_doc[u'maxItems'] = field.max_len
            if len(field.fields) == 1:
                json_schema_doc[u'items'] = self.to_json(field.fields[0])
            else:
                json_schema_doc[u'items'] = [self.to_json(field) for field in field.fields]
        elif isinstance(field, NoneField):
            json_schema_doc[u'type'] = u'null'
        elif isinstance(field, AnyField):
            json_schema_doc[u'type'] = u'any'
        elif isinstance(field, AbstractNumericField):
            json_schema_doc[u'type'] = u'number'
            if field.min is not None:
                json_schema_doc[u'minimum'] = field.min
            if field.max is not None:
                json_schema_doc[u'maximum'] = field.max
        elif isinstance(field, UnicodeField):
            json_schema_doc[u'type'] = u'string'

        return json_schema_doc
    
    def from_json(self, json_schema_doc):
        pass