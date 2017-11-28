import unittest
import httpretty
import pytest

from odm.catalogs.portals.ckanApiV3 import CkanReader

package_list_result = '{"help":"","success":true,"result":["haushaltsplan-entwurf-koeln-2018"]}'
package_show_result_dkan = '{ "help": "", "success": true, "result": [ { "id": "1", "name": "name", "title": "title", "author": "Stadt Bonn", "author_email": "opendata@bonn.de", "maintainer": "Offene Daten Bonn", "maintainer_email": "opendata@bonn.de", "license_title": "cc-zero", "notes": "...", "url": "", "state": "Active", "log_message": "...", "private": "Veroffentlicht", "revision_timestamp": "2017-10-18T14:26:43+02:00", "metadata_created": "2017-09-26T12:20:07+02:00", "metadata_modified": "2017-10-18T14:26:43+02:00", "creator_user_id": "1", "type": "Dataset", "resources": [ { "id": "1", "revision_id": "", "url": "", "description": "...", "format": "csv", "state": "Active", "revision_timestamp": "2017-10-18T12:04:45+02:00", "name": "1", "mimetype": "csv", "size": "", "created": "2017-09-26T12:21:34+02:00", "resource_group_id": "1", "last_modified": "Date changed 2017-10-18T12:04:45+02:00" } ], "tags": [ { "id": "1", "vocabulary_id": "2", "name": "Bevolkerung" } ], "groups": [ { "description": "...", "id": "2", "image_display_url": "https://opendata.bonn.de/sites/default/files/Bonn_Group_2.jpg", "title": "Stadt Bonn", "name": "group/stadt-bonn" } ] } ] }'

class TestCKANAPIV3(object):
    def test_failure(self):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            reader = CkanReader('non included')
        assert pytest_wrapped_e.type == SystemExit

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

    @httpretty.activate
    def test_moers(self):
        httpretty.register_uri(httpretty.GET, "https://www.offenesdatenportal.de/api/action/organization_show?include_datasets=true&id=moers",
            body='{"result": {"packages": []}}',
            content_type="application/json")
        reader = CkanReader('moers')
        reader.gather()
        assert (httpretty.has_request())

    @httpretty.activate
    def test_moers_detail(self):
        httpretty.register_uri(httpretty.GET, "https://www.offenesdatenportal.de/api/action/organization_show?include_datasets=true&id=moers",
            body='{"result": {"packages": [{"name": "test"}]}}',
            content_type="application/json")
        httpretty.register_uri(httpretty.GET, "https://www.offenesdatenportal.de/api/action/package_show?id=test",
            body='{"success": true, "result": []}',
            content_type="application/json")
        reader = CkanReader('moers')
        reader.gather()
        assert (httpretty.has_request())

    @httpretty.activate
    def test_koeln(self):
        httpretty.register_uri(httpretty.GET, "http://offenedaten-koeln.de/api/3/action/package_list",
            body='{"result": []}',
            content_type="application/json")
        reader = CkanReader('koeln')
        reader.gather()
        assert (httpretty.has_request())
    @httpretty.activate
    def test_koeln_detail(self):
        httpretty.register_uri(httpretty.GET, "http://offenedaten-koeln.de/api/3/action/package_list",
            body=package_list_result,
            content_type="application/json")
        httpretty.register_uri(httpretty.GET, "http://offenedaten-koeln.de/api/3/action/package_show?id=haushaltsplan-entwurf-koeln-2018",
            body="{}",
            content_type="application/json")
        reader = CkanReader('koeln')
        reader.gather()
        assert (httpretty.has_request())

    @httpretty.activate
    def test_bonn(self):
        httpretty.register_uri(httpretty.GET, "http://opendata.bonn.de/api/3/action/package_list",
            body='{"result": []}',
            content_type="application/json")
        reader = CkanReader('bonn')
        reader.gather()
        assert (httpretty.has_request())
    @httpretty.activate
    def test_bonn_detail(self):
        httpretty.register_uri(httpretty.GET, "http://opendata.bonn.de/api/3/action/package_list",
            body=package_list_result,
            content_type="application/json")
        httpretty.register_uri(httpretty.GET, "http://opendata.bonn.de/api/3/action/package_show?id=haushaltsplan-entwurf-koeln-2018",
            body=package_show_result_dkan,
            content_type="application/json")
        reader = CkanReader('bonn')
        data = reader.gather()
        assert len(data) == 1
        assert (httpretty.has_request())

    @httpretty.activate
    def test_berlin(self):
        httpretty.register_uri(httpretty.POST, "http://datenregister.berlin.de/api/3/action/current_package_list_with_resources",
            body='{"result": []}',
            content_type="application/json")
        reader = CkanReader('berlin')
        reader.gather('1234')
        assert (httpretty.has_request())

    @httpretty.activate
    def test_gelsenkirchen(self):
        httpretty.register_uri(httpretty.GET, "https://opendata.gelsenkirchen.de/api/3/action/package_list",
            body='{"result": []}',
            content_type="application/json")
        reader = CkanReader('gelsenkirchen')
        reader.gather()
        assert (httpretty.has_request())

    def test_meerbusch_import(self):
        data = { "private": False, "resources": [], "title": "Meerbusch", "name": "meerbusch", "groups": "", "notes": "" }
        reader = CkanReader('meerbusch')
        d = reader.import_data(data)
        assert d['city'] == 'meerbusch'

    def test_bonn_import(self):
        data = { "name": "name", "title": "title", "maintainer": "Offene Daten Bonn", "license_title": "cc-zero", "private": "Veroffentlicht", "resources": [ { "url": ""} ], "tags": [ { "name": "Bevolkerung" } ] }
        reader = CkanReader('bonn')
        d = reader.import_data(data)
        assert d['publisher'] == 'Offene Daten Bonn'
