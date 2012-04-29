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
from dictlib.schema import Schema, UnicodeField, DictField, LongField, ListField
import unittest

class TestValidation(unittest.TestCase):
    def test_field_type_check(self):
        schema = Schema({u'text': UnicodeField()})
        self.assertRaises(ValidationError, schema.validate, {u'tag': 666})

    def test_required_fields(self):
        schema = Schema({u'text': UnicodeField()})
        schema.validate({u'text': u'hello world'})
        self.assertRaises(ValidationError, schema.validate, {u'tag': u'greeting'})

    def test_optional_field(self):
        schema = Schema({u'text': UnicodeField(), u'tag': UnicodeField(optional=True)})

        schema.validate({u'text': u'hello world'})
        schema.validate({u'text': u'hello world', u'tag': u'greeting'})

    def test_empty_doc(self):
        schema = Schema({u'tag': UnicodeField(optional=True)})
        schema.validate({})

    def test_nested_fields(self):
        schema = Schema({u'text': UnicodeField(), u'd': DictField({u'a': UnicodeField()})})

        schema.validate({u'text': u'hello world', u'd': {u'a': u'bye bye world'}})
        self.assertRaises(ValidationError,schema.validate,
                {u'text': u'hello world', u'd': {u'a': u'bye bye world', u'b': u'oops'}})

    def test_type_as_key(self):
        schema = Schema({u'text': UnicodeField(), unicode: LongField()})

        schema.validate({u'text': u'hello world', u'a': 200L})
        self.assertRaises(ValidationError, schema.validate, {u'text': u'hello world'})

    def test_optional_type_as_key(self):
        schema = Schema({u'text': UnicodeField(), unicode: LongField(optional=True)})

        schema.validate({u'text': u'hello world'})

    def test_nested_dictionaries(self):
        # Check if nested dictionaries are handled correctly
        schema = Schema({'d': {u'a': LongField()}})
        schema.validate({u'd': {'a': 50L}})

        # double-nested ...
        schema = Schema({'d': {u'a': {u'b': LongField()}}})
        schema.validate({u'd': {'a': {u'b': 50L}}})

    def test_additional_fields_in_nested_dictionary(self):
        # test whether a key in a nested dictionary not defined in the schema
        # causes a validation error. For testing whether recursion in schema
        # field access works properly.
        schema = Schema({'d': DictField({u'a': LongField()})})

        schema.validate({u'd': {'a': 50L}})
        self.assertRaises(ValidationError, schema.validate, {u'd': {'a': 50L, 'b': 20}})
        schema.validate({u'd': {'a': 50L}})

        self.assertRaises(ValidationError, schema.validate, {u'd': {'a': 50L}, u'a': 4})
        schema.validate({u'd': {'a': 50L}})

    def test_list_fields(self):
        schema = Schema({'l': ListField(LongField())})
        # Empty lists
        schema.validate({u'l': []})
        # list with one correctly typed element
        schema.validate({u'l': [700L]})
        # list with one incorrectly typed element
        self.assertRaises(ValidationError, schema.validate, {u'l': [u'hello']})

    def test_schema_subclassing(self):
        class MySchema(Schema): schema = {u'a': UnicodeField()}

        MySchema().validate({u'a': u'hello mars'})
        MySchema().validate({}, partial=True)
