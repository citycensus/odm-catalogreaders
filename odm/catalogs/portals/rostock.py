# -*- coding: utf-8 -*-
import urllib
import json

from odm.catalogs.utils import metautils
from odm.catalogs.CatalogReader import CatalogReader


city = 'rostock'
portalname = 'opendata-hro.de'
jsonurl = "http://www.opendata-hro.de/api/2/search/dataset?q=&limit=1000&all_fields=1"


def mapData(package):
    files = []
    resources = []
    row = {}

    if ('res_url' in package):
        resources = package['res_url']

    for file in resources:
        files.append(file)

    row[u'filelist'] = files
    row[u'Stadt'] = city
    row[u'url'] = 'http://www.opendata-hro.de/dataset/' + package['id']

    if ('res_format' in package):
        row[u'Format'] = list(set(package['res_format']))
        row[u'geo'] = metautils.isgeo(row[u'Format'])

    row[u'Dateibezeichnung'] = package['title']
    if 'notes' in package:
        row[u'Beschreibung'] = package['notes']
    if 'license_id' in package:
        row[u'Lizenz'] = package['license_id']
    if 'maintainer' in package:
        row[u'Veröffentlichende Stelle'] = package['maintainer']

    row['categories'] = map(lambda x: metautils.govDataShortToODM(x)[0], package.get('groups', []))
    row['metadata'] = package

    return row


class RostockReader(CatalogReader):
    def info(self):
        return {
            'name': 'rostock_harvester',
            'title': u'opendata-hro.de',
            'description': ''
        }

    def gather(self):
        data = urllib.urlopen("http://www.opendata-hro.de/api/2/search/dataset?q=&limit=1000&all_fields=1")
        data = json.loads(data.read())
        data = data[u'results']
        data = map(mapData, data)
        return data

    def fetch(self, d):
        return d

    def import_data(self, d):
        d = metautils.gerToEngKeys(d)
        d['accepted'] = True
        d['source'] = 'd'
        d['metadata_xml'] = None
        d['costs'] = None
        d['spatial'] = None
        d['open'] = metautils.isopen(d.get('licenseshort', '').strip())
        d['temporalextent'] = ''  # have a look if its there
        return d
