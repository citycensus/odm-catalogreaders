#!/usr/bin/python
# -*- coding: utf-8 -*-
import unittest
import httpretty
import pytest
import json

from odm.catalogs.portals.ckanApiV3 import CkanReader

package_list_result = '{"help":"","success":true,"result":["haushaltsplan-entwurf-koeln-2018"]}'
package_show_result_dkan = u'{ "help": "", "success": true, "result": [ { "id": "1", "name": "name", "title": "title", "author": "Stadt Bonn", "author_email": "opendata@bonn.de", "maintainer": "Offene Daten Bonn", "maintainer_email": "opendata@bonn.de", "license_title": "cc-zero", "notes": "...", "url": "", "state": "Active", "log_message": "...", "private": "Veroffentlicht", "revision_timestamp": "2017-10-18T14:26:43+02:00", "metadata_created": "2017-09-26T12:20:07+02:00", "metadata_modified": "2017-10-18T14:26:43+02:00", "creator_user_id": "1", "type": "Dataset", "resources": [ { "id": "1", "revision_id": "", "url": "", "description": "...", "format": "csv", "state": "Active", "revision_timestamp": "2017-10-18T12:04:45+02:00", "name": "1", "mimetype": "csv", "size": "", "created": "2017-09-26T12:21:34+02:00", "resource_group_id": "1", "last_modified": "Date changed 2017-10-18T12:04:45+02:00" } ], "tags": [ { "id": "1", "vocabulary_id": "2", "name": "Bevölkerung" } ], "groups": [ { "description": "...", "id": "2", "image_display_url": "https://opendata.bonn.de/sites/default/files/Bonn_Group_2.jpg", "title": "Stadt Bonn", "name": "group/stadt-bonn" } ] } ] }'

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
        httpretty.register_uri(httpretty.GET, "https://offenedaten-koeln.de/api/3/action/package_list",
            body='{"result": []}',
            content_type="application/json")
        reader = CkanReader('koeln')
        reader.gather()
        assert (httpretty.has_request())
    @httpretty.activate
    def test_koeln_detail(self):
        httpretty.register_uri(httpretty.GET, "https://offenedaten-koeln.de/api/3/action/package_list",
            body=package_list_result,
            content_type="application/json")
        httpretty.register_uri(httpretty.GET, "https://offenedaten-koeln.de/api/3/action/package_show?id=haushaltsplan-entwurf-koeln-2018",
            body="{}",
            content_type="application/json")
        reader = CkanReader('koeln')
        reader.gather()
        assert (httpretty.has_request())

    @httpretty.activate
    def test_bonn(self):
        httpretty.register_uri(httpretty.GET, "https://opendata.bonn.de/api/3/action/package_list",
            body='{"result": []}',
            content_type="application/json")
        reader = CkanReader('bonn')
        reader.gather()
        assert (httpretty.has_request())
    @httpretty.activate
    def test_bonn_detail(self):
        httpretty.register_uri(httpretty.GET, "https://opendata.bonn.de/api/3/action/package_list",
            body=package_list_result,
            content_type="application/json")
        httpretty.register_uri(httpretty.GET, "https://opendata.bonn.de/api/3/action/package_show?id=haushaltsplan-entwurf-koeln-2018",
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
    def test_gelsenkirchen_import(self):
        data = { "name": "name", "title": "title", "maintainer": "Offene Daten Gelsenkirchen", "license_title": "cc-zero", "private": "Veroffentlicht", "resources": [ { "url": ""} ], "tags": [ { "name": "Bevolkerung" } ] }
        reader = CkanReader('gelsenkirchen')
        d = reader.import_data(data)
        assert d['publisher'] == 'Offene Daten Gelsenkirchen'


    def test_meerbusch_import(self):
        data = { "private": False, "resources": [], "title": "Meerbusch", "name": "meerbusch", "groups": "", "notes": "" }
        reader = CkanReader('meerbusch')
        d = reader.import_data(data)
        assert d['city'] == 'meerbusch'

    def test_bonn_import(self):
        data = { "name": "name", "title": "title", "maintainer": "Offene Daten Bonn", "license_title": "cc-zero", "private": "Veroffentlicht", "resources": [ { "url": ""} ], "tags": [ { "name": "Bevolkerung" } ] }
        reader = CkanReader('bonn')
        d = reader.import_data(data)
        print(d)
        assert d['publisher'] == 'Offene Daten Bonn'

    def test_info(self):
        reader = CkanReader('bonn')
        info = { 'name': 'bonn_harvester',
            'title': 'opendata.bonn.de',
            'description': ''
            }
        assert reader.info() == info

    def test_fetch(self):
        reader = CkanReader('bonn')
        assert reader.fetch('test') == 'test'

    @httpretty.activate
    def test_german_codes(self):
        datasetId = u'bürgeranträge-gem-§-24-go-nrw'
        httpretty.register_uri(httpretty.GET, "https://opendata.bonn.de/api/3/action/package_list",
            body='{"result": ["bürgeranträge-gem-§-24-go-nrw"]}',
            content_type="application/json")
        httpretty.register_uri(httpretty.GET, "https://opendata.bonn.de/api/3/action/package_show?id="+datasetId,
            body='{"result": []}',
            content_type="application/json")
        reader = CkanReader('bonn')
        result = reader.gather()
        assert (httpretty.has_request())
        assert len(result) == 0


    def test_bonn_special(self):
        data = {"id":"42db3b50-1904-4123-98a3-6e71d381362a","name":"stellenangebote-der-stadtwerke-bonn","title":"Stellenangebote der Stadtwerke Bonn","author":"Stadtwerke Bonn","author_email":"opendata@bonn.de","maintainer":"Offene Daten Bonn","maintainer_email":"opendata@bonn.de","license_title":"cc-by","notes":"Stellenangebote der Stadtwerke Bonn","url":"https:\/\/opendata.bonn.de\/dataset\/stellenangebote-der-stadtwerke-bonn","state":"Active","log_message":"Update to resource \u0027Stellenangebote\u0027","private":"Ver\u00f6ffentlicht","revision_timestamp":"2016-03-02T17:34:05+01:00","metadata_created":"2014-09-11T11:04:12+02:00","metadata_modified":"2016-03-02T17:34:05+01:00","creator_user_id":"4b64ff5b-02cf-45e6-afc4-3c2d01e8dad0","type":"Dataset","resources":[{"id":"4377bb9d-ae1f-4acb-955a-399487fdff6e","revision_id":"","url":"https:\/\/opendata.bonn.de\/dataset\/4377bb9d-ae1f-4acb-955a-399487fdff6e\/resource\/4377bb9d-ae1f-4acb-955a-399487fdff6e","description":"Die Stadtwerke Bonn sind t\u00e4tig im \u00f6ffentlichen Nahverkehr, in der Energie- und Wasserversorgung sowie der Abfallwirtschaft und bieten engagierten Mitarbeiterinnen und Mitarbeitern attraktive Arbeitspl\u00e4tze und Karrierem\u00f6glichkeiten.\n\nLizenz: Zu verwenden ist \u0022Stadtwerke Bonn\u0022 in der Namensnennung. \n","format":"html","state":"Active","revision_timestamp":"2016-03-02T15:08:35+01:00","name":"dataset\/4377bb9d-ae1f-4acb-955a-399487fdff6e\/resource\/4377bb9d-ae1f-4acb-955a-399487fdff6e","mimetype":"html","size":"","created":"2014-09-11T11:05:11+02:00","resource_group_id":"4174726c-a3d5-4fc9-acb2-f5dde64c2ec0","last_modified":"Date changed\t2016-03-02T15:08:35+01:00"}],"tags":[{"id":"ef69c05c-8275-4f07-8706-b6ef46fc2d98","vocabulary_id":"2","name":"Transport und Verkehr"},{"id":"8d2f0d7b-1f4c-45f5-a9d0-260501f66378","vocabulary_id":"2","name":"Umwelt und Klima"},{"id":"041068fd-b8d6-4a81-820b-4756d893b550","vocabulary_id":"2","name":"Wirtschaft und Arbeit"}],"groups":[{"description":"Stadtwerke Bonn\u003Cbr \/\u003E\nTheaterstra\u00dfe 24\u003Cbr \/\u003E\n53111 Bonn\u003Cbr \/\u003E\u003Ca href=\u0022http:\/\/www.stadtwerke-bonn.de \u0022 title=\u0022http:\/\/www.stadtwerke-bonn.de \u0022\u003Ehttp:\/\/www.stadtwerke-bonn.de \u003C\/a\u003E","id":"4174726c-a3d5-4fc9-acb2-f5dde64c2ec0","image_display_url":"https:\/\/opendata.bonn.de\/sites\/default\/files\/swb-logo.png","title":"Stadtwerke Bonn","name":"group\/stadtwerke-bonn"}]}

        reader = CkanReader('bonn')
        d = reader.import_data(data)

    def test_is_open_import(self):
        ckan_result = { "name": "test", "license_id": "dl-de-zero-2.0", "private": "", "title": "Test", "groups": [] }
        reader = CkanReader('moers')
        d = reader.import_data(ckan_result)
        print(d)
        assert d['open'] == 'Offen'

