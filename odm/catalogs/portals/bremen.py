# -*- coding: utf-8 -*-
import urllib
import json

from odm.catalogs.utils import metautils
from odm.catalogs.CatalogReader import CatalogReader

portalname = 'daten.bremen.de'
city = 'bremen'
jsonurl = 'http://daten.bremen.de/sixcms/detail.php?template=export_daten_json_d'


def import_package(package):
    row = {}
    #Store a copy of the metadata
    row['metadata'] = package

    row[u'Stadt'] = city
    row[u'Dateibezeichnung'] = package['title']
    row[u'Beschreibung'] = package['notes']
    row[u'url'] = package['url']

    #Get resources and formats
    if ('resources' in package and len(package['resources']) > 0):
        formats = []
        files = []
        for resource in package['resources']:
            files.append(resource['url'])
            formats.append(resource['format'])
        row[u'Format'] = formats
        row[u'geo'] = metautils.isgeo(formats)
        row[u'files'] = files

    if 'temporal_coverage_from' in package['extras'] and len(package['extras']['temporal_coverage_from']) > 3:
        row[u'Zeitlicher Bezug'] = package['extras']['temporal_coverage_from'][0:4]

    if ('terms_of_use' in package['extras'] and len(package['extras']['terms_of_use']) > 0):
        row[u'Lizenz'] = package['extras']['terms_of_use']['licence_id']

    if ('dates' in package['extras'] and len(package['extras']['dates']) > 0):
        row[u'original_metadata'] = {}
        for dates in package['extras']['dates']:
            if dates['role'] == 'erstellt':
                row[u'original_metadata'][u'metadata_created'] = dates['date']
            if dates['role'] == 'aktualisiert':
                row[u'original_metadata'][u'metadata_modified'] = dates['date']

    row['categories'] = map(lambda x: metautils.govDataShortToODM(x)[0], package.get('groups', []))
    return row


class BremenReader(CatalogReader):
    def info(self):
        return {
            'name': 'bremen_harvester',
            'title': u'daten.bremen.de',
            'description': ''
        }

    def gather(self):
        jsonReq = urllib.urlopen(jsonurl)
        packages = json.loads(jsonReq.read())
        return packages

    def fetch(self, d):
        return d

    def import_data(self, d):
        d = import_package(d)
        d = metautils.gerToEngKeys(d)
        d = dict(d)
        d['originating_portal'] = portalname
        d['accepted'] = True
        d['source'] = 'd'
        d['metadata_xml'] = None
        d['costs'] = None
        d['spatial'] = None
        d['open'] = metautils.isopen(d['licenseshort'].strip())
        d['publisher'] = ''  # actually its in the data
        d['filelist'] = d['files']
        return d
