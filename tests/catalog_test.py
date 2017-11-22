import unittest
import httpretty

from odm.catalogs.portals.ckanApiV3 import CkanReader

class TestCKANAPIV3(object):
    @httpretty.activate
    def test_meerbusch(self):
        httpretty.register_uri(httpretty.GET, "https://opendata.meerbusch.de/api/3/action/package_list",
            body='{"result": []}',
            content_type="application/json")
        reader = CkanReader('meerbusch')
        reader.gather()
        assert (httpretty.has_request())

    @httpretty.activate
    def test_hamburg(self):
        httpretty.register_uri(httpretty.GET, "http://suche.transparenz.hamburg.de/api/3/action/package_list",
            body='{"result": []}',
            content_type="application/json")
        reader = CkanReader('hamburg')
        reader.gather()
        assert (httpretty.has_request())

    @httpretty.activate
    def test_muenchen(self):
        httpretty.register_uri(httpretty.GET, "http://www.opengov-muenchen.de/api/3/action/package_list",
            body='{"result": []}',
            content_type="application/json")
        reader = CkanReader('muenchen')
        reader.gather()
        assert (httpretty.has_request())

    @httpretty.activate
    def test_rostock(self):
        httpretty.register_uri(httpretty.GET, "http://opendata-hro.de/api/3/action/package_list",
            body='{"result": []}',
            content_type="application/json")
        reader = CkanReader('rostock')
        reader.gather()
        assert (httpretty.has_request())
