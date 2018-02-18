import unittest
import httpretty
import pytest
import json

from odm.catalogs.portals.opendatasoft import ODSReader

class TestODS(object):
    def test_failure(self):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            reader = ODSReader('non included')
        assert pytest_wrapped_e.type == SystemExit

    @httpretty.activate
    def test_potsdam(self):
        httpretty.register_uri(httpretty.GET, "https://opendata.potsdam.de/api/v2/catalog/datasets",
            body='{"links": [], "datasets": []}',
            content_type="application/json")
        reader = ODSReader('potsdam')
        reader.gather()
        assert (httpretty.has_request())

    @httpretty.activate
    def test_files(self):
        httpretty.register_uri(httpretty.GET, "https://opendata.potsdam.de/api/v2/catalog/datasets",
            body='{"links": [], "datasets": [{"links": [{ "rel": "exports", "href": "https://opendata.potsdam.de/api/v2/catalog/datasets/wahlkreise/exports"}], "dataset": { "dataset_id": "wahlkreise"}}]}',
            content_type="application/json")
        httpretty.register_uri(httpretty.GET, "https://opendata.potsdam.de/api/v2/catalog/datasets/wahlkreise/exports",
            body='{"links": [{"href": "", "rel": "csv"}] }',
            content_type="application/json")
        reader = ODSReader('potsdam')
        data = reader.gather()
        assert (httpretty.has_request())
        assert (httpretty.has_request())
        assert len(data) == 1
        assert len(data[0]["files"]) == 1

