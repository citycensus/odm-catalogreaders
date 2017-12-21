#!/usr/bin/python
# -*- coding: latin-1 -*-
import unittest
import httpretty
import pytest
import json

import odm.catalogs.utils.metautils as metautils

class TestMetaUtils(object):
    def test_isopen(self):
        assert metautils.isopen('dl-de-by-2.0') == 'Offen'
    def test_is_open_uppercase(self):
        assert metautils.isopen('CC BY 3.0 DE') == 'Offen'
