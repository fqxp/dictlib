# -*- coding: utf-8 -*-
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

"""
`dictlib` is a library for easy complex handling of dictionaries in Python.

It currently has the following features:
 - schema definition
 - validating a dictionary against a schema
 - creating a dictionary by schema rules
 - mapping dictionaries to Python objects (adapter or mixin)
 - dot notation for nested dictionaries (adapter or mixin)

`dictlib` has many possible uses, including the painless development of 
interfaces to JSON APIs. See `couchlib` for an example.

G{importgraph dictlib}
"""