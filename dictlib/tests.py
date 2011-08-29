'''
Created on 28.08.2011

@author: frank
'''
import unittest
from dictlib.schema import DictField, LongField, UnicodeField, ValidationError,\
    ListField, Schema
from dictlib.utils import update_recursive, walk
from dictlib.mixins import DotNotationAdapter, DotNotationMixin,\
    ObjectMappingAdapter, ObjectMappingMixin


class TestSchema(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass

    def test_validate(self):
        # test required and optional fields
        schema = Schema({u'text': UnicodeField(),
                         u'tag': UnicodeField(optional=True)})
        schema.validate({u'text': u'hello world'})
        schema.validate({u'text': u'hello world', u'tag': u'greeting'})
        try:
            schema.validate({u'tag': u'greeting'})
            self.fail(u'validate should raise a ValidationError')
        except ValidationError:
            pass

        # test nested fields
        schema2 = Schema({u'text': UnicodeField(),
                          u'd': DictField({u'a': UnicodeField()})})
        schema2.validate({u'text': u'hello world',
                          u'd': {u'a': u'bye bye world'}})
        try:
            schema2.validate({u'text': u'hello world',
                              u'd': {u'a': u'bye bye world',
                                     u'b': u'oops'}})
            self.fail(u'validate should raise a ValidationError')
        except ValidationError:
            pass

        # test type as key (arbitrary key constrained to a type)
        schema3 = Schema({u'text': UnicodeField(),
                          unicode: LongField()})
        schema3.validate({u'text': u'hello world',
                          u'a': 200L})
        try:
            schema3.validate({u'text': u'hello world'})
            self.fail(u'validate should raise a ValidationError')
        except ValidationError:
            pass

        # test optional type as key
        schema4 = Schema({u'text': UnicodeField(),
                         unicode: LongField(optional=True)})
        schema4.validate({u'text': u'hello world'})

        # test additional field in nested dictionary
        schema5 = Schema({'d': DictField({u'a': LongField()})})
        schema5.validate({u'd': {'a': 50L}})
        try:
            schema5.validate({u'd': {'a': 50L,
                                     'b': 20}})
            self.fail(u'validate should raise a ValidationError')
        except ValidationError:
            pass
        schema5.validate({u'd': {'a': 50L}})

        try:
            schema5.validate({u'd': {'a': 50L},
                              u'a': 4})
            self.fail(u'validate should raise a ValidationError')
        except ValidationError:
            pass
        schema5.validate({u'd': {'a': 50L}})

        # Check if nested dictionaries are handled correctly
        schema6 = Schema({'d': {u'a': LongField()}})
        schema6.validate({u'd': {'a': 50L}})

        # double-nested ...
        schema6 = Schema({'d': {u'a': {u'b': LongField()}}})
        schema6.validate({u'd': {'a': {u'b': 50L}}})
        
        # Try out ListFields ...
        schema7 = Schema({'l': ListField(LongField())})
        # Empty lists
        schema7.validate({u'l': []})
        # list with one correctly typed element
        schema7.validate({u'l': [700L]})
        # list with one incorrectly typed element
        try:
            schema7.validate({u'l': [u'hello']})
            self.fail(u'validate should raise a ValidationError')
        except ValidationError:
            pass

        # test schema subclassing notation
        class MySchema(Schema):
            schema = {u'a': UnicodeField()}
            
        MySchema().validate({u'a': u'hello mars'})
        MySchema().validate({}, partial=True)
        
    def testCreate(self):
        schema = Schema({u'a': UnicodeField(default=u'hello world')})
        self.assertEquals({u'a': u'hello world'}, schema.create())
        
        # test creating instance with given default value
        schema = Schema({u'a': UnicodeField(default=u'hello world'),
                         u'b': UnicodeField(default=u'hello good bye')})
        self.assertEquals({u'a': u'hello venus',
                           u'b': u'hello good bye'}, schema.create({u'a': u'hello venus'}))
        
        schema = Schema({u'a': {u'b': UnicodeField(default=u'hello world')}})
        self.assertEquals({u'a': {u'b': u'hello world'}}, schema.create())


class TestUtils(unittest.TestCase):
    def test_update_recursive(self):
        self.assertEquals({u'a': 1}, update_recursive({}, {u'a': 1}))
        self.assertEquals({u'a': 1}, update_recursive({u'a': 0}, {u'a': 1}))
        self.assertEquals({u'a': None}, update_recursive({u'a': 0}, {u'a': None}))

        # test nesting
        self.assertEquals({u'a': {u'b': 1}}, update_recursive({}, {u'a': {u'b': 1}}))
        self.assertEquals({u'a': {u'b': 1}}, update_recursive({u'a': 0}, {u'a': {u'b': 1}}))
        self.assertEquals({u'a': {u'b': None}}, update_recursive({u'a': 0}, {u'a': {u'b': None}}))

        # test 'skip_none' parameter
        self.assertEquals({u'a': {}}, update_recursive({}, {u'a': {u'b': None}}, skip_none=True))
        self.assertEquals({u'a': {}}, update_recursive({u'a': 0}, {u'a': {u'b': None}}, skip_none=True))
        self.assertEquals({u'a': 0}, update_recursive({u'a': 0}, {u'a': None}, skip_none=True))
        
    def test_walk(self):
        self.assertEquals([(u'a', 1)], list(walk({'a': 1})))
        self.assertEquals([(u'a.b', 1)], list(walk({u'a': {'b': 1}})))
        result = list(walk({u'a': {'b': 1, u'c': 2}}))
        self.assertTrue((u'a.b', 1) in result)
        self.assertTrue((u'a.c', 2) in result)
        

class TestMixins(unittest.TestCase):
    def test_DotNotationAdapter(self):
        self._run_DotNotation_tests(DotNotationAdapter)
        
    def test_DotNotationMixin(self):
        class MyDotNotationDict(DotNotationMixin, dict):
            pass
        self._run_DotNotation_tests(MyDotNotationDict)

    def _run_DotNotation_tests(self, factory):
        d = factory({u'a': {u'b': 1}})
        self.assertEquals(1, d[u'a.b'])
        d[u'a.b'] = 2
        self.assertEquals(2, d[u'a'][u'b'])
        self.assertEquals(2, d[u'a.b'])
        
        d = factory({})
        try:
            self.assertEquals(1, d[u'a.b'])
            self.fail(u'Should have thrown KeyError')
        except KeyError:
            pass
        d[u'a.b'] = 2
        self.assertEquals(2, d[u'a'][u'b'])
        self.assertEquals(2, d[u'a.b'])
        
    def test_ObjectMappingAdapter(self):
        self._run_ObjectMapping_tests(ObjectMappingAdapter)
        
    def test_ObjectMappingMixin(self):
        class MyObjectMappingDict(ObjectMappingMixin, dict):
            pass
        self._run_ObjectMapping_tests(MyObjectMappingDict)
        
    def _run_ObjectMapping_tests(self, factory):
        d = factory({})
        # test __contains__()
        self.assertFalse(u'a' in d)
        # test keys()
        self.assertEquals([], d.keys())
        try:
            d.a
            self.fail(u'Should have thrown AttributeError')
        except AttributeError:
            pass
        d.a = 2
        self.assertTrue(u'a' in d)
        self.assertEquals([u'a'], d.keys())
        self.assertEquals(2, d.a)
        self.assertEquals(2, d[u'a'])
        
        # test non-nested dictionary
        d = factory({u'a': 1})
        self.assertEquals(1, d.a)
        self.assertEquals(1, d[u'a'])
        d.a = 2
        self.assertEquals(2, d.a)
        self.assertEquals(2, d[u'a'])

        # test nested dictionary
        d = factory({u'a': {u'b': 1}})
        # keys() should only return top-level attributes
        self.assertEquals([u'a'], d.keys())
        self.assertEquals(1, d.a.b)
        self.assertEquals(1, d[u'a'][u'b'])
        d.a.b = 2
        self.assertEquals(2, d.a.b)
        self.assertEquals(2, d[u'a'][u'b'])

        # test erroneous parameters
        d = factory({u'a': 2})
        self.assertEquals(2, d.a)
        self.assertEquals(2, d[u'a'])
        try:
            d.a.b = 2
            self.fail(u'Should have thrown AttributeError')
        except AttributeError:
            pass

    def test_DotNotation_and_ObjectMapping(self):
        # Test combination of ObjectMappingMixin and DotNotationMixin in this order
        class MyPowerfulDict1(ObjectMappingMixin, DotNotationMixin, dict):
            pass
        self._run_DotNotation_and_ObjectMapping_tests(MyPowerfulDict1)

        dict_cls = type('anonymous dict', (ObjectMappingMixin, DotNotationMixin, dict), {})
        self._run_DotNotation_and_ObjectMapping_tests(dict_cls)
        
    def test_ObjectMapping_and_DotNotation(self):        
        # Test combination of DotNotationMixin and ObjectMappingMixin in this order
        class MyPowerfulDict2(DotNotationMixin, ObjectMappingMixin, dict):
            pass
        self._run_DotNotation_and_ObjectMapping_tests(MyPowerfulDict2)
        
        dict_cls = type('anonymous dict', (DotNotationMixin, ObjectMappingMixin, dict), {})
        self._run_DotNotation_and_ObjectMapping_tests(dict_cls)
        
        dict_cls = lambda d: ObjectMappingAdapter(DotNotationAdapter(d))
        self._run_DotNotation_and_ObjectMapping_tests(dict_cls)
        
    def _run_DotNotation_and_ObjectMapping_tests(self, factory):
        d = factory({})
        try:
            d.a.b = 42
            self.fail(u'Should have thrown AttributeError')
        except AttributeError:
            pass
        d.a = {}
        d.a.b = 42
        self.assertTrue(u'a' in d)
        self.assertTrue(u'a.b' in d)
        self.assertEquals(42, d.a.b)
        self.assertEquals(42, d[u'a.b'])
        self.assertEquals(42, d[u'a'][u'b'])
        d[u'a.c'] = 666
        self.assertTrue(u'a.c' in d)
        self.assertEquals(666, d.a.c)
        self.assertEquals(666, d[u'a.c'])
        self.assertEquals(666, d[u'a'][u'c'])
        d[u'a'][u'd'] = 667
        self.assertTrue(u'a.d' in d)
        self.assertEquals(667, d.a.d)
        self.assertEquals(667, d[u'a.d'])
        self.assertEquals(667, d[u'a'][u'd'])
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testDictField']
    unittest.main()