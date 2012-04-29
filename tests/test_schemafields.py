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

from dictlib.exceptions import ValidationError
from dictlib.schema import Field, TypeField, UnicodeField, FieldField, NoneField, \
    IntField, LongField, UuidField, FloatField, ListField, Schema, DictField
import re
import unittest
import uuid

class TestSchemaFields(unittest.TestCase):
    def test_Field_validates_any_value(self):
        field = Field(can_be_none=True)

        try:
            field.validate(u'hello')
            field.validate(666)
            field.validate(None)
        except ValidationError:
            self.fail('Field.validate() raised ValidationError unexpectedly')

    def test_Field_raises_ValidationError_when_value_cannot_be_None(self):
        field = Field(can_be_none=False)

        self.assertRaises(ValidationError, field.validate, None)

    def test_TypeField_validates_correct_type(self):
        field = TypeField()
        field.type = unicode

        try:
            field.validate(u'hello world')
        except ValidationError:
            self.fail('TypeField.validate() raised ValidationError unexpectedly')

    def test_TypeField_raises_ValidationError_on_incorrect_type(self):
        field = TypeField()
        field.type = unicode

        self.assertRaises(ValidationError, field.validate, 42)

    def test_FieldField_validates_Field_type(self):
        field = FieldField()
        field.validate(UnicodeField())

    def test_NoneField_validates_None_value(self):
        field = NoneField()
        field.validate(None)

    def test_NoneField_raises_ValidationError_on_incorrect_types(self):
        field = NoneField()

        self.assertRaises(ValidationError, field.validate, {})
        self.assertRaises(ValidationError, field.validate, u'')

    def test_IntField_validates_integer_values(self):
        field = IntField()

        try:
            field.validate(42)
        except ValidationError:
            self.fail('IntField.validate() raised ValidationError unexpectedly')

    def test_IntField_raises_ValidationError_on_incorrect_type(self):
        field = IntField()

        self.assertRaises(ValidationError, field.validate, 100000000000000L)
        self.assertRaises(ValidationError, field.validate, None)

    def test_IntField_validates_None_if_value_can_be_None(self):
        field = IntField(can_be_none=True)
        field.validate(None)

    def test_IntField_validates_with_min_and_max_values(self):
        field = IntField(min=41, max=43)

        try:
            field.validate(41)
            field.validate(43)
        except ValidationError:
            self.fail('IntField.validate() raised ValidationError unexpectedly')

        self.assertRaises(ValidationError, field.validate, 40)
        self.assertRaises(ValidationError, field.validate, 44)

    def test_LongField_validates_long_values_correctly(self):
        field = LongField()

        try:
            field.validate(100000000000L)
        except ValidationError:
            self.fail('LongField.validate() raised ValidationError unexpectedly')

    def test_LongField_raises_ValidationError_on_incorrect_types(self):
        field = LongField()

        self.assertRaises(ValidationError, field.validate, 42)
        self.assertRaises(ValidationError, field.validate, None)

    def test_LongField_validates_None_if_value_can_be_None(self):
        field = LongField(can_be_none=True)
        field.validate(None)

    def test_LongField_validates_with_min_and_max_values(self):
        field = LongField(min=41L, max=43L)

        try:
            field.validate(41L)
            field.validate(43L)
        except ValidationError:
            self.fail('LongField.validate() raised ValidationError unexpectedly')

        self.assertRaises(ValidationError, field.validate, 40L)
        self.assertRaises(ValidationError, field.validate, 44L)

    def test_FloatField_validates_float_values_correctly(self):
        field = FloatField()

        try:
            field.validate(3.1415927)
        except ValidationError:
            self.fail('FloatField.validate() raised ValidationError unexpectedly')

    def test_FloatField_raises_ValidationError_on_incorrect_type(self):
        field = FloatField()

        self.assertRaises(ValidationError, field.validate, 42)
        self.assertRaises(ValidationError, field.validate, None)

    def test_FloatField_validates_None_if_value_can_be_None(self):
        field = FloatField(can_be_none=True)

        try:
            field.validate(None)
        except ValidationError:
            self.fail('FloatField.validate() raised ValidationError unexpectedly')

    def test_FloatField_validates_with_min_and_max_values(self):
        field = FloatField(min=41.5, max=42.5)
        field.validate(41.5)
        field.validate(42.5)
        self.assertRaises(ValidationError, field.validate, 41.0)
        self.assertRaises(ValidationError, field.validate, 43.0)

    def test_UnicodeField_validates_unicode_values_correctly(self):
        field = UnicodeField()

        try:
            field.validate(u'')
            field.validate(u'hello world')
        except ValidationError:
            self.fail('UnicodeField.validate() raised ValidationError unexpectedly')

    def test_UnicodeField_raises_ValidationError_on_incorrect_type(self):
        field = UnicodeField()
        self.assertRaises(ValidationError, field.validate, 'hello world') # n.b.: byte string
        self.assertRaises(ValidationError, field.validate, 42)

    def test_UnicodeField_validates_when_length_is_equal_length(self):
        field = UnicodeField(length=11)

        try:
            field.validate(u'hello world')
        except ValidationError:
            self.fail('UnicodeField.validate raised ValidationError unexpectedly')

    def test_UnicodeField_validates_when_length_is_unequal_length(self):
        field = UnicodeField(length=11)
        self.assertRaises(ValidationError, field.validate, u'bye')

    def test_UnicodeField_validates_when_value_length_is_between_min_and_max_length(self):
        field = UnicodeField(min_len=5, max_len=8)

        try:
            field.validate(u'hello')
            field.validate(u'12345678')
        except ValidationError:
            self.fail('UnicodeField.validate() raised ValidationError unexpectedly')

    def test_UnicodeField_raises_ValidationError_when_length_is_outside_allowed_range(self):
        field = UnicodeField(min_len=5, max_len=8)

        self.assertRaises(ValidationError, field.validate, u'1234')
        self.assertRaises(ValidationError, field.validate, u'123456789')

    def test_UnicodeField_validates_when_value_matches_pattern(self):
        field = UnicodeField(match=re.compile(ur'hello .+'))

        try:
            field.validate(u'hello world')
        except ValidationError:
            self.fail('UnicodeField.validate raised ValidationError unexpectedly')

    def test_UnicodeField_raises_ValidationError_when_value_does_not_match_pattern(self):
        field = UnicodeField(match=re.compile(ur'hello .+'))

        self.assertRaises(ValidationError, field.validate, u'bye world')

    def test_UnicodeField_validates_None_if_value_can_be_None(self):
        field = UnicodeField(can_be_none=True)

        try:
            field.validate(u'hello world')
            field.validate(None)
        except ValidationError:
            self.fail('UnicodeField.validate raised ValidationError unexpectedly')

    def test_UuidField_validates_Uuid_value(self):
        field = UuidField()

        try:
            field.validate(unicode(uuid.uuid4().hex))
        except ValidationError:
            self.fail('UuidField.validate raised ValidationError unexpectedly')

    def test_UuidField_raises_ValidationError_on_incorrect_type(self):
        field = UuidField()

        self.assertRaises(ValidationError, field.validate, u'hello world')

    def test_ListField_validates_list_values(self):
        field = ListField()

        try:
            field.validate([1, u'hello world']) 
        except ValidationError:
            self.fail('ListField.validate() raised ValidationError unexpectedly')

    def test_ListField_validates_list_values_with_given_type(self):
        field = ListField(UnicodeField())

        try:
            field.validate([])
            field.validate([u'hello moon', u'hello world'])
        except ValidationError:
            self.fail('ListField raised ValidationError unexpectedly')

    def test_ListField_raises_ValidationError_on_incorrect_list_element_type(self):
        field = ListField(UnicodeField())

        self.assertRaises(ValidationError, field.validate, u'just a string')
        self.assertRaises(ValidationError, field.validate, [u'hello', 42])

    def test_ListField_validates_with_min_and_max_length(self):
        field = ListField(IntField(), min_len=3, max_len=5)

        try:
            field.validate([1, 2, 3])
            field.validate([1, 2, 3, 4, 5])
        except ValidationError:
            self.fail('ListField.validate() raised ValidationError unexpectedly')

    def test_ListField_raises_ValidationError_with_length_outside_range(self):
        field = ListField(IntField(), min_len=3, max_len=5)

        self.assertRaises(ValidationError, field.validate, [])
        self.assertRaises(ValidationError, field.validate, [1, 2])
        self.assertRaises(ValidationError, field.validate, [1, 2, 3, 4, 5, 6])
        self.assertRaises(ValidationError, field.validate, None)

    def test_DictField_validates_value_matching_pattern(self):
        field = DictField({u'a': DictField({u'b': UnicodeField()})})

        try:
            field.validate({u'a': {u'b': u'hello world'}})
        except ValidationError:
            self.fail('DictField.validate raised ValidationError unexpectedly')

    def test_DictField_raises_ValidationError_on_incorrect_type(self):
        field = DictField({u'a': DictField({u'b': UnicodeField()})})

        self.assertRaises(ValidationError, field.validate, None)

    def test_DictField_validates_None_value_if_value_can_be_None(self):
        field = DictField({u'a': DictField({u'b': UnicodeField()}, can_be_none=True)})

        try:
            field.validate({u'a': None})
        except ValidationError:
            self.fail('DictField.validate() raised ValidationError unexpectedly')

    def test_Schema_validates_value_matching_pattern(self):
        schema = Schema({u'a': {u'b': UnicodeField()}})
        schema.validate({u'a': {u'b': u'hello world'}})

    def test_Schema_is_valid_returns_whether_value_is_valid(self):
        schema = Schema({u'a': {u'b': UnicodeField()}})

        self.assertTrue(schema.is_valid({u'a': {u'b': u'hello world'}}))
        self.assertFalse(schema.is_valid({u'a': {u'b': 42}}))
        self.assertFalse(schema.is_valid({u'a': {u'c': 42}}))

    def test_Schema_is_partially_valid_returns_whether_value_is_partially_valid(self):
        schema = Schema({u'a': {u'b': UnicodeField()}})

        self.assertFalse(schema.is_partially_valid({u'a': {u'c': 42}}))
        self.assertTrue(schema.is_partially_valid({u'a': {}}))
        self.assertFalse(schema.is_partially_valid({u'a': {u'b': 42}}))

    def test_Schema_with_type_key_validates_value_matching_pattern(self):
        schema = Schema({unicode: UnicodeField()})

        try:
            schema.validate({u'a': u'hello world'})
        except ValidationError:
            self.fail('Schema.validate() raised ValidationError unexpectedly')

    def test_Schema_with_type_key_raises_ValidationError_on_non_matching_key(self):
        schema = Schema({unicode: UnicodeField()})

        self.assertRaises(ValidationError, schema.validate, {42: 'foobar'})
