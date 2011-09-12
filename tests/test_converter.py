import unittest
from dictlib.convert import Converter, JsonConverter
from dictlib.schema import Schema, UnicodeField, DatetimeField
import datetime

class Test(unittest.TestCase):
    def test_from_schema_exclude(self):
        # test if fields are excluded correctly
        converter = Converter(exclude=[u'x', u'y'])
        self.assertEquals({u'z': u'c'}, converter.from_schema({u'x': u'a',
                                                               u'y': u'b',
                                                               u'z': u'c'}))
    
    def test_to_schema_exclude(self):
        # nothing should happen when converting to the schema
        converter = Converter(exclude=[u'x', u'y'])
        self.assertEquals({u'x': u'a', u'y': u'b', u'z': u'c'}, 
                          converter.to_schema({u'x': u'a', u'y': u'b', u'z': u'c'}))
    
    def test_schema_exclude_recursive(self):
        converter = Converter(exclude=[u'a.b'])
        self.assertEquals({u'a': {}, u'x': u'y'}, 
                           converter.from_schema({u'a': {u'b': 666},
                                                  u'x': u'y'}))
    
    def test_from_schema_rename(self):
        # test if fields are renamed correctly
        converter = Converter(rename=[(u'x', u'g'), (u'y', u'h')])
        self.assertEquals({u'g': u'a', u'h': u'b', u'z': u'c'}, 
                          converter.from_schema({u'x': u'a',
                                                 u'y': u'b',
                                                 u'z': u'c'}))

    def test_to_schema_rename(self):
        # test if fields are reverse-renamed correctly
        converter = Converter(rename=[(u'x', u'g'), (u'y', u'h')])
        self.assertEquals({u'x': u'a', u'y': u'b', u'z': u'c'}, 
                          converter.to_schema({u'g': u'a',
                                               u'h': u'b',
                                               u'z': u'c'}))
    def test_rename_inverse(self):
        converter = Converter(rename=[(u'x', u'g'), (u'y', u'h')])
        doc = {u'x': u'a', u'y': u'b', u'z': u'c'}
        self.assertEquals(doc, converter.to_schema(converter.from_schema(doc)))
        
        doc = {u'g': u'a', u'h': u'b', u'z': u'c'}
        self.assertEquals(doc, 
                          converter.from_schema(converter.to_schema(doc)))

    def test_converter_rename_and_exclude(self):
        # test if fields are reverse-renamed correctly
        converter = Converter(exclude=[u'x'], 
                              rename=[(u'z', u'i')])
        self.assertEquals({u'y': u'b', u'i': u'c'},
                converter.from_schema({u'x': u'a', u'y': u'b', u'z': u'c'}))
        self.assertEquals({u'y': u'b', u'z': u'c'},
                converter.to_schema({u'y': u'b', u'i': u'c'}))
        
        # test Converter where order of exclude and rename is important
        # (here, 'x' is excluded first, and then *not* renamed because)
        converter = Converter(exclude=[u'x'],
                              rename=[(u'x', u'a')])
        self.assertEquals({u'y': u'b'}, converter.from_schema({u'x': u'a', u'y': u'b'}))
        
    def test_map_from(self):
        class MyConverter(Converter):
            def map_from(self, key, value):
                if isinstance(value, unicode):
                    value = u'YYY%s' % value
                return key, value

            def map_to(self, key, value):
                if isinstance(value, unicode) and value.startswith(u'YYY'):
                    value = value[3:]
                return key, value
        
        converter = MyConverter()
        self.assertEquals({u'x': u'YYYa'},
                          converter.from_schema({u'x': u'a'}))
        
    def test_json_converter(self):
        schema = Schema({u'a': UnicodeField(),
                         u'b': DatetimeField()})
        json_converter = JsonConverter(schema)
        result_doc = json_converter.from_schema({u'a': u'x',
                                                 u'b': datetime.datetime(2011, 9, 11, 17, 29, 0)})
        self.assertEquals({'a': 'x', 'b': '2011-09-11T17:29:00Z'}, result_doc)
        self.assertEquals({'a': 'x', 
                           'b': '2011-09-11T17:29:00Z'},
                          json_converter.from_schema({u'a': u'x',
                                                      u'b': datetime.datetime(2011, 9, 11, 17, 29, 0)}))
        self.assertTrue(isinstance(result_doc.keys()[0], str))
        self.assertTrue(isinstance(result_doc.keys()[1], str))
        self.assertTrue(isinstance(result_doc['a'], str))
        self.assertEquals({u'a': u'x', 
                           u'b': datetime.datetime(2011, 9, 11, 17, 29, 0)},
                          json_converter.to_schema({'a': u'x',
                                                    'b': '2011-09-11T17:29:00Z'}))
            
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()