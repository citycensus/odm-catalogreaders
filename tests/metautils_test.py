#!/usr/bin/python
# -*- coding: utf-8 -*-
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

    def test_match_category(self):
        assert metautils.matchCategory('Wahlen') == 'Politik und Wahlen'

    def test_match_category_short(self):
        assert metautils.matchCategory('Haushalt und Steuern') == u'Öffentliche Verwaltung, Haushalt und Steuern'

    def test_categories(self):
        categories = (u'Bildung und Wissenschaft', 'Wahlen')
        assert metautils.matchCategories(categories) == ['Bildung und Wissenschaft', 'Politik und Wahlen']

