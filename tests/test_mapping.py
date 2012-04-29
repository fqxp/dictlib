# -*- coding: utf-8 -*-
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

from dictlib.mapping import DotNotationAdapter, DotNotationMixin, \
    ObjectMappingAdapter, ObjectMappingMixin, BaseDictAdapter
import unittest

class TestMapping(unittest.TestCase):
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

        # test in and del
        self.assertTrue(u'a.b' in d)
        del d[u'a.b']
        self.assertTrue(u'a.b' not in d)

        # test keys()
        self.assertEquals([u'a'], d.keys())

        d = factory({u'a': [1, 2, 3]})
        self.assertEquals(2, d[u'a.1'])

        d[u'a.3'] = 4
        self.assertEquals(4, d[u'a.3'])

        # test various exceptions
        def get_item(doc, key):
            return doc[key]
        def set_item(doc, key, value):
            doc[key] = value
        def del_item(doc, key):
            del doc[key]
        self.assertRaises(KeyError, get_item, d, u'a.6')
        self.assertRaises(KeyError, set_item, d, u'a.6', 6)
        self.assertRaises(KeyError, del_item, d, u'a.6')

        # test lists with dictionaries as elements
        d = factory({u'a': [{u'b': u'x'},
                            {u'c': u'y'}]})
        self.assertEquals(u'x', d[u'a.0.b'])
        # test non-existing key (z)
        self.assertRaises(KeyError, get_item, d, u'a.0.z')
        # test non-existing index (2)
        self.assertRaises(KeyError, get_item, d, u'a.2.z')

        # test non-existing sub-dict
        d[u'b.d'] = 42
        self.assertEquals(42, d[u'b.d'])
        # test non-existing sub-dict with two recursions
        d[u'b.e.f'] = 666
        self.assertEquals(666, d[u'b.e.f'])

        # test non-existing sub-list
        d[u'b.g.0'] = 10
        d[u'b.g.1'] = 11
        self.assertEquals(10, d[u'b.g.0'])
        self.assertEquals(11, d[u'b.g.1'])

        # test non-existing sub-list
        d[u'c.0.a'] = 20
        d[u'c.1.a'] = 21
        self.assertEquals(20, d[u'c.0.a'])
        self.assertEquals(21, d[u'c.1.a'])

        # test non-existing sub-list with two recursions
        d[u'b.h.i'] = 20
        self.assertEquals(20, d[u'b.h.i'])

    def test_ObjectMappingAdapter(self):
        self._run_ObjectMapping_tests(ObjectMappingAdapter)

    def test_ObjectMappingMixin(self):
        class MyObjectMappingDict(ObjectMappingMixin, dict):
            pass
        self._run_ObjectMapping_tests(MyObjectMappingDict)

    def _run_ObjectMapping_tests(self, factory):
        d = factory({})
        # test doc property
        if isinstance(d, BaseDictAdapter):
            self.assertEquals({}, d.doc)
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

        # test in and del
        d = factory({u'a': {u'b': 42}})
        self.assertTrue(u'a' in d)
        self.assertTrue(u'b' in d.a)
        del d.a[u'b']
        self.assertTrue(u'b' not in d.a)

        # test keys()
        self.assertEquals([u'a'], d.keys())

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
        d.a = {u'c': 0}
        self.assertEquals(d[u'a'], d.a)

        d.a.b = 42
        self.assertEquals(42, d[u'a'][u'b'])
        self.assertEquals(42, d[u'a.b'])
        self.assertEquals(42, d.a.b)
        self.assertTrue(u'a' in d)
        self.assertTrue(u'a.b' in d)
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
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
