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

from dictlib.schema import IntField, DatetimeField, DateField, TimeField, Field, \
    NoneField, LongField, FloatField, UnicodeField, UuidField, DictField, ListField
import datetime
import unittest
import uuid

class TestSchemaJson(unittest.TestCase):
    def test_Field_json_methods(self):
        f = Field()
        self.assertEquals(u'hello world', 
                          f.from_json(f.to_json(u'hello world')))
        self.assertEquals(u'hello world', 
                          f.to_json(f.from_json(u'hello world')))

    def test_NoneField_json_methods(self):
        f = NoneField()
        self.assertEquals(None, 
                          f.from_json(f.to_json(None)))
        self.assertEquals(None, 
                          f.to_json(f.from_json(None)))

    def test_IntField_json_methods(self):
        f = IntField()
        self.assertEquals(1234567890, 
                          f.from_json(f.to_json(1234567890)))
        self.assertEquals(1234567890, 
                          f.to_json(f.from_json(1234567890)))

    def test_LongField_json_methods(self):
        f = LongField()
        self.assertEquals(1234567890L, 
                          f.from_json(f.to_json(1234567890L)))
        self.assertEquals(1234567890, 
                          f.to_json(f.from_json(1234567890L)))

    def test_FloatField_json_methods(self):
        f = FloatField()
        self.assertEquals(1.234567890, 
                          f.from_json(f.to_json(1.234567890)))
        self.assertEquals(1.234567890, 
                          f.to_json(f.from_json(1.234567890)))

    def test_UnicodeField_json_methods(self):
        # what's important here is the UTF-8 encoding/decoding
        f = UnicodeField()
        self.assertEquals(u'we are motörhead', 
                          f.from_json(f.to_json(u'we are motörhead')))
        self.assertEquals('we are motörhead', 
                          f.to_json(f.from_json('we are motörhead')))
        self.assertEquals(str, 
                          type(f.to_json(f.from_json('we are motörhead'))))
        self.assertEquals(str, 
                          type(f.to_json(f.from_json(u'we are motörhead'))))
        self.assertEquals(str,
                          type(f.to_json(u'we are motörhead')))

    def test_UuidField_json_methods(self):
        f = UuidField()
        a_uuid = uuid.uuid4().hex
        self.assertEquals(a_uuid, 
                          f.from_json(f.to_json(a_uuid)))
        self.assertEquals(a_uuid, 
                          f.to_json(f.from_json(a_uuid)))
        
    def test_DatetimeField_json_methods(self):
        f = DatetimeField()
        now = datetime.datetime.utcnow().replace(microsecond=0)
        self.assertEquals(now, 
                          f.from_json(f.to_json(now)))
        now_json = '2011-07-10T20:00:00Z'
        self.assertEquals(now_json, 
                          f.to_json(f.from_json(now_json)))
        
    def test_DateField_json_methods(self):
        f = DateField()
        now = datetime.datetime.utcnow().date()
        self.assertEquals(now, 
                          f.from_json(f.to_json(now)))
        now_json = '2011-07-10'
        self.assertEquals(now_json, 
                          f.to_json(f.from_json(now_json)))
        
    def test_TimeField_json_methods(self):
        f = TimeField()
        now = datetime.datetime.utcnow().time().replace(microsecond=0)
        self.assertEquals(now, 
                          f.from_json(f.to_json(now)))
        now_json = '20:00:00'
        self.assertEquals(now_json, 
                          f.to_json(f.from_json(now_json)))
        
    def test_ListField_json_methods(self):
        f = ListField(UnicodeField())
        self.assertEquals([u'hello', u'world'], 
                          f.from_json(f.to_json([u'hello', u'world'])))
        self.assertEquals(['hello', 'world'], 
                          f.from_json(f.to_json(['hello', 'world'])))
        
        f = ListField(DatetimeField(), UnicodeField(), IntField())
        self.assertEquals([u'hello', 42], 
                          f.from_json(f.to_json([u'hello', 42])))
        self.assertEquals(['hello', 42], 
                          f.from_json(f.to_json(['hello', 42])))
        
    def test_DictField_json_methods(self):
        f = DictField({u'a': UnicodeField()})
        self.assertEquals({'a': 'hello world'}, 
                          f.from_json(f.to_json({u'a': u'hello world'})))
        f = DictField({u'a': {u'b': UnicodeField()}})
        self.assertEquals({'a': {'b': 'hello world'}}, 
                          f.from_json(f.to_json({u'a': {u'b': u'hello world'}})))

    def test_field(self):
        # Any object needs these tests ...
        self.assertEquals(unicode,
                          type(unicode(Field())))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()