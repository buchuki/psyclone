#!/usr/bin/env python
#
# Copyright 2010 Dusty Phillips
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

def force_str(value):
    '''Ensure the result is a str.
    
    If value is bytes, convert it to a utf8 string. If None or a string, return
    it unchanged. Otherwise, raise an AssertionError.'''
    if value is None:
        return value
    if isinstance(value, bytes):
        return str(value, 'utf8')
    assert isinstance(value, str)
    return value

def force_bytes(value):
    '''Ensure the result is a bytes.

    if value is str, decode it as a utf8 string. If None or a bytes, return it
    unchanged. Otherwise, raise an AssertionError.'''
    if value is None:
        return value
    if isinstance(value, str):
        return bytes(value, 'utf8')
    assert isinstance(value, bytes)
    return value
