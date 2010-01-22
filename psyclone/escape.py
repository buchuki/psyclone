#!/usr/bin/env python
#
# Copyright 2009 Facebook
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

"""Escaping/unescaping methods for HTML, JSON, URLs, and others."""

import html.entities
import re
import xml.sax.saxutils
import urllib.request, urllib.parse, urllib.error

import json
_json_decode = lambda s: json.loads(s)
_json_encode = lambda v: json.dumps(v)


def xhtml_escape(value):
    """Escapes a string so it is valid within XML or XHTML."""
    return xml.sax.saxutils.escape(_str(value))


def xhtml_unescape(value):
    """Un-escapes an XML-escaped string."""
    return re.sub(r"&(#?)(\w+?);", _convert_entity, _unicode(value))


def json_encode(value):
    """JSON-encodes the given Python object."""
    return _json_encode(value)


def json_decode(value):
    """Returns Python objects for the given JSON string."""
    return _json_decode(value)


def squeeze(value):
    """Replace all sequences of whitespace chars with a single space."""
    return re.sub(r"[\x00-\x20]+", " ", value).strip()


def url_escape(value):
    """Returns a valid URL-encoded version of the given value."""
    return urllib.parse.quote_plus(utf8(value))


def url_unescape(value):
    """Decodes the given value from a URL."""
    return _unicode(urllib.parse.unquote_plus(value))


def _bytes(value):
    if isinstance(value, str):
        return bytes(value, 'utf8')
    assert isinstance(value, bytes)
    return value

def _str(value):
    if isinstance(value, bytes):
        return str(value, 'utf8')
    assert isinstance(value, str)
    return value

def utf8(value):
    if isinstance(value, str):
        return value.encode("utf-8")
    assert isinstance(value, str)
    return value


def _unicode(value):
    if isinstance(value, str):
        return value.decode("utf-8")
    assert isinstance(value, str)
    return value


def _convert_entity(m):
    if m.group(1) == "#":
        try:
            return chr(int(m.group(2)))
        except ValueError:
            return "&#%s;" % m.group(2)
    try:
        return _HTML_UNICODE_MAP[m.group(2)]
    except KeyError:
        return "&%s;" % m.group(2)


def _build_unicode_map():
    unicode_map = {}
    for name, value in html.entities.name2codepoint.items():
        unicode_map[name] = chr(value)
    return unicode_map

_HTML_UNICODE_MAP = _build_unicode_map()
