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

from dictlib.schema import Schema, UnicodeField
import unittest

class TestSchemaCreate(unittest.TestCase):
    def test_create_empty_doc(self):
        # Empty schema
        schema = Schema({})
        self.assertEquals({}, schema.create())

        # Schema with only optional fields
        schema = Schema({u'a': UnicodeField(optional=True)})
        self.assertEquals({}, schema.create())
        
    def test_create_with_defaults(self):
        schema = Schema({u'a': UnicodeField(default=u'hello world')})
        self.assertEquals({u'a': u'hello world'}, schema.create())
        
        # test creating instance with given default value
        schema = Schema({u'a': UnicodeField(default=u'hello world'),
                         u'b': UnicodeField(default=u'hello good bye')})
        self.assertEquals({u'a': u'hello venus', u'b': u'hello good bye'}, 
                          schema.create({u'a': u'hello venus'}))

    def create_nested(self):
        schema = Schema({u'a': {u'b': UnicodeField(default=u'hello world')}})
        self.assertEquals({u'a': {u'b': u'hello world'}}, schema.create())        
