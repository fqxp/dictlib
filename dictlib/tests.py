'''
Created on 28.08.2011

@author: frank
'''
import unittest
from dictlib.schema import DictField, LongField, UnicodeField, ValidationError,\
    ListField, Schema


class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testDictField(self):
        df = Schema({u'text': UnicodeField(),
                     u'tag': UnicodeField(optional=True)})
        df.validate({u'text': u'hello world'})
        df.validate({u'text': u'hello world', u'tag': u'greeting'})
        try:
            df.validate({u'tag': u'greeting'})
            self.fail(u'validate should raise a ValidationError')
        except ValidationError:
            pass

        df2 = Schema({u'text': UnicodeField(),
                        u'd': DictField({u'a': UnicodeField()})})
        df2.validate({u'text': u'hello world',
                      u'd': {u'a': u'bye bye world'}})
        try:
            df2.validate({u'text': u'hello world',
                          u'd': {u'a': u'bye bye world',
                                 u'b': u'oops'}})
            self.fail(u'validate should raise a ValidationError')
        except ValidationError:
            pass

        df3 = Schema({u'text': UnicodeField(),
                         unicode: LongField()})
        df3.validate({u'text': u'hello world',
                      u'a': 200L})
        try:
            df3.validate({u'text': u'hello world'})
            self.fail(u'validate should raise a ValidationError')
        except ValidationError:
            pass

        df4 = Schema({u'text': UnicodeField(),
                         unicode: LongField(optional=True)})
        df4.validate({u'text': u'hello world'})

        df5 = Schema({'d': DictField({u'a': LongField()})})
        df5.validate({u'd': {'a': 50L}})
        try:
            df5.validate({u'd': {'a': 50L,
                                 'b': 20}})
            self.fail(u'validate should raise a ValidationError')
        except ValidationError:
            pass
        df5.validate({u'd': {'a': 50L}})

        try:
            df5.validate({u'd': {'a': 50L},
                          u'a': 4})
            self.fail(u'validate should raise a ValidationError')
        except ValidationError:
            pass
        df5.validate({u'd': {'a': 50L}})

        # Check if nested dictionaries are handled correctly
        df6 = Schema({'d': {u'a': LongField()}})
        df6.validate({u'd': {'a': 50L}})

        # double-nested ...
        df6 = Schema({'d': {u'a': {u'b': LongField()}}})
        df6.validate({u'd': {'a': {u'b': 50L}}})

        
        # Try out ListFields ...
        df7 = Schema({'l': ListField(LongField())})
        # Empty lists
        df7.validate({u'l': []})
        # list with one correctly typed element
        df7.validate({u'l': [700L]})
        # list with one incorrectly typed element
        try:
            df7.validate({u'l': [u'hello']})
            self.fail(u'validate should raise a ValidationError')
        except ValidationError:
            pass

    def testSubclass(self):
        class MySchema(Schema):
            schema = {u'a': UnicodeField()}
            
        MySchema().validate({u'a': u'hello mars'})
        MySchema().validate({}, partial=True)
        
    def testCreate(self):
        schema = Schema({u'a': UnicodeField(default=u'hello world')})
        self.assertEquals({u'a': u'hello world'}, schema.create())
        
        schema = Schema({u'a': UnicodeField(default=u'hello world'),
                         u'b': UnicodeField(default=u'hello good bye')})
        self.assertEquals({u'a': u'hello venus',
                           u'b': u'hello good bye'}, schema.create({u'a': u'hello venus'}))
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testDictField']
    unittest.main()