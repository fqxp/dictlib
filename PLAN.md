dictlib plan
============

Requirements
------------
dictlib will be used to provide anything suitable for complex dictionary 
handling in Python.

It can be used to easily build the model layer for any databases that can be
accessed using the JSON format.

 * should be usable for anything that provides a dict-like interface, i. e. 
   no tests for subclasses of dict will be made
 * mappings should be dictionaries with extra functionality

Components
----------
 * [done] schema: Definition of the structure of arbitrary dictionaries; later: should
   be convertible to external schema description formats (e. g. JSON Schema)
 * [done] validator: Validate dict objects againsts a schema
 * converter: Convert a dict to another format using a schema and a converter
   describing the transformations made (rename, convert by function ...)
 * [done] creator: Create objects matching a schema, using default values, optionality
   etc., provide initial values
 * object mapping: Map dictionary to python object, create database models by
   subclassing and adding functions like save/load, validate/create functions
 * [done] utilities: recursive update etc.