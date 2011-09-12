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

from dictlib.utils import update_recursive, walk, map_dict, throws
import unittest

class TestUtils(unittest.TestCase):
    def test_update_recursive_simple(self):
        self.assertEquals({u'a': 1}, update_recursive({}, {u'a': 1}))
        self.assertEquals({u'a': 1}, update_recursive({u'a': 0}, {u'a': 1}))
        self.assertEquals({u'a': None}, update_recursive({u'a': 0}, {u'a': None}))

    def test_update_recursive_nested(self):
        self.assertEquals({u'a': {u'b': 1}}, update_recursive({}, {u'a': {u'b': 1}}))
        self.assertEquals({u'a': {u'b': 1}}, update_recursive({u'a': 0}, {u'a': {u'b': 1}}))
        self.assertEquals({u'a': {u'b': None}}, update_recursive({u'a': 0}, {u'a': {u'b': None}}))

    def test_update_recursive_skip_none(self):
        """ Test 'skip_none' parameter. """
        self.assertEquals({u'a': {}}, update_recursive({}, {u'a': {u'b': None}}, skip_none=True))
        self.assertEquals({u'a': {}}, update_recursive({u'a': 0}, {u'a': {u'b': None}}, skip_none=True))
        self.assertEquals({u'a': 0}, update_recursive({u'a': 0}, {u'a': None}, skip_none=True))
        
    def test_walk(self):
        self.assertEquals([(u'a', 1)], list(walk({'a': 1})))
        # test if keys are yielded
        self.assertEquals([(u'a', {u'b': 1}), (u'a.b', 1)], 
                          list(walk({u'a': {'b': 1}})))
        result = list(walk({u'a': {'b': 1, u'c': 2}}))
        self.assertTrue((u'a.b', 1) in result)
        self.assertTrue((u'a.c', 2) in result)
        
    def test_map_dict(self):
        # simple
        d = {u'a': u'b'}
        self.assertEquals({'a': 'b'}, map_dict(d, lambda k,v: (str(k), str(v))))

        # recursive
        d = {u'a': {u'b': u'c'}}
        self.assertEquals({'a': {'b': 'c'}}, map_dict(d, lambda k,v: (str(k), str(v))))
        
    def test_throws(self):
        def f(x):
            if x != 666:
                raise IndexError()
        self.assertFalse(throws(IndexError, f, 666))
        self.assertTrue(throws(IndexError, f, 667))
        self.assertFalse(throws([IndexError, KeyError], f, 666))
        self.assertTrue(throws([IndexError, KeyError], f, 667))

        # test if exceptions not mentioned are re-raised
        self.assertRaises(IndexError, throws, KeyError, f, 667)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()