from dictlib.schema import Schema, UnicodeField
import unittest

class TestSchemaCreate(unittest.TestCase):
    def test_create_empty_doc(self):
        # Empty schema
        schema = Schema({})
        self.assertEquals({}, schema.create())

        # Schema with only optional fields
        schema = Schema({u'a': UnicodeField(optional=True)})
        self.assertEquals({}, schema.create())
        
    def test_create_with_defaults(self):
        schema = Schema({u'a': UnicodeField(default=u'hello world')})
        self.assertEquals({u'a': u'hello world'}, schema.create())
        
        # test creating instance with given default value
        schema = Schema({u'a': UnicodeField(default=u'hello world'),
                         u'b': UnicodeField(default=u'hello good bye')})
        self.assertEquals({u'a': u'hello venus', u'b': u'hello good bye'}, 
                          schema.create({u'a': u'hello venus'}))

    def create_nested(self):
        schema = Schema({u'a': {u'b': UnicodeField(default=u'hello world')}})
        self.assertEquals({u'a': {u'b': u'hello world'}}, schema.create())        
