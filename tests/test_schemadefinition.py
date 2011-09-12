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

from dictlib.schema import UnicodeField, Schema, IntField
import unittest

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