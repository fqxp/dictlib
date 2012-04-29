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

        self.assertEquals(u'hello world', f.from_json(f.to_json(u'hello world')))
        self.assertEquals(u'hello world', f.to_json(f.from_json(u'hello world')))

    def test_NoneField_json_methods(self):
        f = NoneField()

        self.assertEquals(None, f.from_json(f.to_json(None)))
        self.assertEquals(None, f.to_json(f.from_json(None)))

    def test_IntField_json_methods(self):
        f = IntField()

        self.assertEquals(1234567890, f.from_json(f.to_json(1234567890)))
        self.assertEquals(1234567890, f.to_json(f.from_json(1234567890)))

    def test_LongField_json_methods(self):
        f = LongField()

        self.assertEquals(1234567890L, f.from_json(f.to_json(1234567890L)))
        self.assertEquals(1234567890, f.to_json(f.from_json(1234567890L)))

    def test_FloatField_from_json_converts_byte_string_to_float(self):
        f = FloatField()

        self.assertEquals('1.234567890', f.from_json('1.234567890'))

    def test_FloatField_to_json_does_not_change_value(self):
        f = FloatField()

        self.assertEquals(1.234567890, f.to_json(1.234567890))

    def test_UnicodeField_from_json_converts_byte_string_to_unicode_string(self):
        f = UnicodeField()

        self.assertEquals(u'we are motörhead', f.from_json('we are motörhead'))

    def test_UnicodeField_to_json_converts_unicode_string_to_byte_string(self):
        f = UnicodeField()

        self.assertEquals('we are motörhead', f.to_json(u'we are motörhead'))
        self.assertEquals(str, type(f.to_json(u'we are motörhead')))

    def test_UuidField_from_json_converts_uuid_to_unicode_string(self):
        f = UuidField()

        self.assertEquals(u'3a752ef0439f4f74a283baf359dd7e7b', f.from_json('3a752ef0439f4f74a283baf359dd7e7b'))

    def test_UuidField_to_json_converts_uuid_to_unicode_string(self):
        f = UuidField()

        self.assertEquals('3a752ef0439f4f74a283baf359dd7e7b', f.to_json(u'3a752ef0439f4f74a283baf359dd7e7b'))

    def test_DatetimeField_to_json_converts_isocoded_datetime_to_datetime_object(self):
        f = DatetimeField()

        dt = datetime.datetime(2012, 4, 29, 12, 24, 36)
        self.assertEquals(dt, f.from_json('2012-04-29T12:24:36Z'))

    def test_DatetimeField_from_json_converts_datetime_object_to_isocoded_datetime_object(self):
        f = DatetimeField()

        dt = datetime.datetime(2012, 4, 29, 12, 24, 36)
        self.assertEquals('2012-04-29T12:24:36Z', f.to_json(dt))

    def test_DateField_to_json_converts_isocoded_date_to_date_object(self):
        f = DateField()

        self.assertEquals(datetime.date(1975, 7, 10), f.from_json('1975-07-10'))

    def test_DateField_from_json_converts_date_object_to_isocoded_date(self):
        f = DateField()

        self.assertEquals('1975-07-10', f.to_json(datetime.datetime(1975, 7, 10)))

    def test_TimeField_to_json_converts_time_object_to_isocoded_time(self):
        f = TimeField()

        self.assertEquals('12:24:36', f.to_json(datetime.time(12, 24, 36)))

    def test_TimeField_from_json_converts_isocoded_time_to_time_object(self):
        f = TimeField()

        self.assertEquals(datetime.time(12, 24, 36), f.from_json('12:24:36'))

    def test_ListField_to_json_converts_list_with_unicode_strings_to_byte_strings(self):
        f = ListField(DatetimeField(), UnicodeField(), IntField())

        self.assertEquals(['foo', 'bar'], f.to_json([u'foo', u'bar']))

    def test_ListField_from_json_converts_list_with_byte_strings_to_list(self):
        f = ListField(UnicodeField())

        self.assertEquals([u'hello', u'world'], f.from_json(['hello', 'world']))

    def test_DictField_to_json_converts_unicode_keys_and_values_to_byte_strings(self):
        f = DictField({u'a': UnicodeField()})

        self.assertEquals({'a': 'hello world'}, f.to_json({u'a': u'hello world'}))

    def test_DictField_from_json_converts_byte_string_keys_and_values_to_unicode_strings(self):
        f = DictField({u'a': UnicodeField()})

        self.assertEquals({u'a': u'foobar'}, f.from_json({'a': 'foobar'}))
