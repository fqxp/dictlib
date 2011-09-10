'''
Created on 07.09.2011

@author: frank
'''
import unittest
from dictlib.schema import UnicodeField, Schema, DatetimeField, IntField
import datetime


class Test(unittest.TestCase):
    def test_instantiation(self):
        s = Schema({u'a': UnicodeField()})
        self.assertEquals(dict, type(s.get_schema()))
        
    def test_create(self):
        schema = Schema({u'a': UnicodeField(default=u'hello world')})
        self.assertEquals({u'a': u'hello world'}, schema.create())
        self.assertEquals({u'a': u'hello world', u'b': u'world'}, 
                          schema.create({u'b': u'world'}))

    def test_create_with_type_key(self):
        schema = Schema({u'a': UnicodeField(default=u'hello world'),
                         unicode: UnicodeField(default=u'aarrgghh')})
        self.assertEquals({u'a': u'hello world'}, schema.create())
        self.assertEquals({u'a': u'hello world', u'b': u'world'}, 
                          schema.create({u'b': u'world'}))
        
    def test_create_with_dict(self):
        schema = Schema({u'a': {u'b': UnicodeField(default=u'hello world')}})
        self.assertEquals({u'a': {u'b': u'hello world'}}, schema.create())

    def test_create_with_callable(self):
        global counter
        counter = 0
        def inc():
            global counter
            counter += 1
            return counter
        schema = Schema({u'counter': IntField(default=inc)})
        self.assertEquals({u'counter': 1}, schema.create())
        self.assertEquals({u'counter': 2}, schema.create())

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test']
    unittest.main()