from dictlib.mixins import DotNotationMixin, ObjectMappingMixin, DotNotationAdapter
from dictlib.convert import Converter, JsonSchemaConverter
from dictlib.schema import UnicodeField, Schema, ObjectIdField
from pprint import pprint
from pymongo.objectid import ObjectId

class X(DotNotationMixin, dict):
    pass

class Y(ObjectMappingMixin, dict):
    pass

class Z(DotNotationMixin, ObjectMappingMixin, dict):
    pass

class A(dict):
    pass

if __name__ == u'__main__':
    s = Schema({u'a': UnicodeField(),
                u'b': {u'c': UnicodeField()}})
    pprint(JsonSchemaConverter().to_json(s))

def old():
    x = X()
    x[u'b.0'] = 5
    x[u'b.3'] = 666
    print x
    
    y = Y()
    y.a = 5
    y.b = {'c': 777}
    y.b.c = 888
    y.x = {}
    y.x.y = 500
    print y
    
    z = Z()
    z[u'z.0'] = 5
    z[u'z.3'] = 666
    z.a = 5
    z.b = {'c': 777}
    z.b.c = 888
    z[u'b.c'] = 999
    z.b = {'x.y': 777}
    z.x = {}
    z.x.y = 500
    print z
    
    a = {'a': 44, 'b': {'c': 22}}
    aa = DotNotationAdapter(a)
    aa[u'b.c'] = 33
    print u'b.c' in aa
    print aa
    
    schema = Schema({'a': UnicodeField()})
    converter = Converter(schema)
    json_doc = converter.to_json({'a': 'hello world'})
    pprint(json_doc)
    
    class UnderscoreConverter(Converter):
        rename = [(u'_id', u'id')]
        def exclude_field(self, doc, key):
            return key.startswith(u'_') or \
                super(UnderscoreConverter, self).exclude_field(doc, key)
    schema = Schema({'a': UnicodeField(), 
                     u'_id': ObjectIdField()})
    converter = UnderscoreConverter(schema)
    json_doc = converter.to_json({'_id': ObjectId(), 'a': 'hello world'})
    print 'json_doc=', json_doc
    print 'json_doc<json', converter.from_json(json_doc)
