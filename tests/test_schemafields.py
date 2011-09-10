import unittest
from dictlib.schema import Field, TypeField, UnicodeField, FieldField, NoneField,\
    IntField, LongField, UuidField, FloatField, ListField, Schema, DictField
from dictlib.exceptions import ValidationError
import re
import uuid

class Test(unittest.TestCase):
    def testField(self):
        field = Field(can_be_none=True)
        field.validate(u'hello')
        field.validate(666)
        field.validate(None)

        field = Field(can_be_none=False)
        field.validate(u'hello')
        field.validate(666)
        self.assertRaises(ValidationError, field.validate, None)
        
    def test_TypeField(self):
        field = TypeField()
        field.type = unicode
        field.validate(u'hello world')
        self.assertRaises(ValidationError, 
                          field.validate, 42)
        
    def test_FieldField(self):
        field = FieldField()
        field.validate(UnicodeField())
        
    def test_NoneField(self):
        field = NoneField()
        field.validate(None)
        self.assertRaises(ValidationError, 
                          field.validate, {})
        self.assertRaises(ValidationError, 
                          field.validate, u'')
        
    def test_IntField(self):
        field = IntField()
        field.validate(42)
        self.assertRaises(ValidationError, 
                          field.validate, 100000000000000L)
        self.assertRaises(ValidationError, 
                          field.validate, None)
        
        field = IntField(can_be_none=True)
        field.validate(None)

        field = IntField(min=41, max=43)
        field.validate(41)
        field.validate(43)
        self.assertRaises(ValidationError, 
                          field.validate, 40)
        self.assertRaises(ValidationError, 
                          field.validate, 44)

    def test_LongField(self):
        field = LongField()
        field.validate(100000000000L)
        self.assertRaises(ValidationError, 
                          field.validate, 42)
        self.assertRaises(ValidationError, 
                          field.validate, None)

        field = LongField(can_be_none=True)
        field.validate(None)

        field = LongField(min=41L, max=43L)
        field.validate(41L)
        field.validate(43L)
        self.assertRaises(ValidationError, 
                          field.validate, 40L)
        self.assertRaises(ValidationError, 
                          field.validate, 44L)

    def test_FloatField(self):
        field = FloatField()
        field.validate(3.1415927)
        self.assertRaises(ValidationError, 
                          field.validate, 42)
        self.assertRaises(ValidationError, 
                          field.validate, None)

        field = FloatField(can_be_none=True)
        field.validate(None)

        field = FloatField(min=41.5, max=42.5)
        field.validate(41.5)
        field.validate(42.5)
        self.assertRaises(ValidationError, 
                          field.validate, 41.0)
        self.assertRaises(ValidationError, 
                          field.validate, 43.0)

    def test_UnicodeField(self):
        field = UnicodeField()
        field.validate(u'')
        field.validate(u'hello world')
        self.assertRaises(ValidationError, 
                          field.validate, 'hello world') # n.b.: byte string
        self.assertRaises(ValidationError, 
                          field.validate, 42)

        field = UnicodeField(length=11)
        field.validate(u'hello world')
        self.assertRaises(ValidationError, 
                          field.validate, u'bye')

        field = UnicodeField(min_len=5, max_len=8)
        field.validate(u'hello')
        field.validate(u'12345678')
        self.assertRaises(ValidationError, 
                          field.validate, u'1234')
        self.assertRaises(ValidationError, 
                          field.validate, u'123456789')

        field = UnicodeField(match=re.compile(ur'hello .+'))
        field.validate(u'hello world')
        self.assertRaises(ValidationError, 
                          field.validate, u'bye world')
        
        field = UnicodeField(can_be_none=True)
        field.validate(u'hello world')
        field.validate(None)
        self.assertRaises(ValidationError, 
                          field.validate, {}) # n.b.: byte string


    def test_UuidField(self):
        field = UuidField()
        field.validate(unicode(uuid.uuid4().hex))
        self.assertRaises(ValidationError, 
                          field.validate, u'hello world')

    def test_ListField(self):
        field = ListField()
        field.validate([1, u'hello world'])

        field = ListField(UnicodeField())
        field.validate([])
        field.validate([u'hello moon', u'hello world'])
        self.assertRaises(ValidationError, 
                          field.validate, u'just a string')
        self.assertRaises(ValidationError, 
                          field.validate, [u'hello', 42])
        
        field = ListField(IntField(), min_len=3, max_len=5)
        field.validate([1, 2, 3])
        field.validate([1, 2, 3, 4, 5])
        self.assertRaises(ValidationError, field.validate, [])
        self.assertRaises(ValidationError, field.validate, [1, 2])
        self.assertRaises(ValidationError, field.validate, [1, 2, 3, 4, 5, 6])

        field = ListField(IntField(), min_len=3, max_len=5)
        self.assertRaises(ValidationError, field.validate, None)
        
    def test_DictField(self):
        field = DictField({u'a': DictField({u'b': UnicodeField()})})
        field.validate({u'a': {u'b': u'hello world'}})
        self.assertRaises(ValidationError, field.validate, None)
        
        field = DictField({u'a': DictField({u'b': UnicodeField()}, can_be_none=True)})
        field.validate({u'a': None})

        field = DictField({u'a': UnicodeField(), u'b': UnicodeField()})
        self.assertRaises(ValidationError, field.validate, {})
        self.assertRaises(ValidationError, field.validate, {u'a': u'hello world'})

    def test_Schema(self):
        schema = Schema({u'a': {u'b': UnicodeField()}})
        schema.validate({u'a': {u'b': u'hello world'}})
        
        self.assertTrue(schema.is_valid({u'a': {u'b': u'hello world'}}))
        self.assertFalse(schema.is_valid({u'a': {u'b': 42}}))

        self.assertFalse(schema.is_valid({u'a': {u'c': 42}}))
        self.assertFalse(schema.is_partially_valid({u'a': {u'c': 42}}))
        self.assertTrue(schema.is_partially_valid({u'a': {}}))
        self.assertFalse(schema.is_partially_valid({u'a': {u'b': 42}}))
        
        schema = Schema({unicode: UnicodeField()})
        schema.validate({u'a': u'hello world'})
        self.assertRaises(ValidationError, schema.validate, {u'a': 42})

        schema = Schema({int: UnicodeField()})
        schema.validate({42: u'hello world'})
        self.assertRaises(ValidationError, schema.validate, {u'a': 42})

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testField']
    unittest.main()