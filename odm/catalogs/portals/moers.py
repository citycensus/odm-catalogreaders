# -*- coding: utf-8 -*-
import urllib
import json

from odm.catalogs.utils import metautils
from odm.catalogs.CatalogReader import CatalogReader

city = 'moers'
portalname = 'offenedaten.moers.de'
jsonurl = 'http://download.moers.de/Open_Data/Gesamtdatei/Moers_alles.json'


def import_package(part):
    row = {}
    package = {}

    # Simplify JSON
    package['title'] = part['title']['description']
    package['notes'] = part['notes']['description']
    package['author'] = part['author']['description']
    package['url'] = part['url']
    package['groups'] = [part['subgroups']['items']['description']]
    if 'resources' in part:
        package['resources'] = []
        for theresource in part['resources']['items']:
            resource = {}
            resource['url'] = theresource['properties']['url']['description']
            resource['format'] = theresource['properties']['format']['description'].split('/')[1].upper()
            if 'moers.de' not in resource['url']:
                resource['url'] = 'http://www.moers.de' + package['url']
            if resource['format'] == 'NSF': resource['format'] = 'XML'
            package['resources'].append(resource)
    package['extras'] = {}
    package['extras']['temporal_coverage_from'] = part['extras']['properties']['dates']['items']['properties']['date']['description'][6:10]
    package['extras']['terms_of_use'] = {}
    package['extras']['terms_of_use']['licence_id'] = part['license_id']['description']
    # Store a copy of the metadata
    row['metadata'] = part

    row[u'Stadt'] = city
    row[u'Dateibezeichnung'] = package['title']
    row[u'Beschreibung'] = package['notes']
    row[u'URL PARENT'] = package['url']

    # Get resources and formats
    if ('resources' in package and len(package['resources']) > 0):
        formats = []
        files = []
        for resource in package['resources']:
            files.append(resource['url'])
            formats.append(resource['format'])

        row[u'Format'] = list(set(formats))
        row[u'geo'] = metautils.isgeo(row[u'Format'])
        row[u'files'] = files

    if 'temporal_coverage_from' in package['extras'] and len(package['extras']['temporal_coverage_from']) > 3:
        row[u'Zeitlicher Bezug'] = package['extras']['temporal_coverage_from'][0:4]

    if ('terms_of_use' in package['extras'] and len(package['extras']['terms_of_use']) > 0):
        row[u'Lizenz'] = package['extras']['terms_of_use']['licence_id']

    row['categories'] = map(lambda x: metautils.govDataLongToODM(x)[0], package.get('groups', []))

    return row


class MoersReader(CatalogReader):
    def info(self):
        return {
            'name': 'moers_harvester',
            'title': u'offenedaten.moers.de',
            'description': ''
        }

    def gather(self):
        # The JSON file is very broken, and this is probably not the best way to fix it, but it might change tomorrow, so...
        jsonReq = urllib.urlopen(jsonurl)
        jtexts = jsonReq.read().split('\"name\"')
        jtexts[len(jtexts) - 1] = jtexts[len(jtexts) - 1] + ' '
        del jtexts[0]
        packages = []
        for text in jtexts:
            jtext = ('[{\"name\"' + text[0:len(text)-7] + ']').replace('application\\', 'application/').replace('\r', '').replace('\n', '').replace('},"license_id"', ']},"license_id"').replace('"description": "Ressourcen: Folgende Felder können für jede Ressource individuell angegeben werden.","type": "array","items": {','"description": "Ressourcen: Folgende Felder können für jede Ressource individuell angegeben werden.","type": "array","items": [{') 
            package = json.loads(jtext)
            packages.append(package[0])
        for p in packages:
            p['url'] = p['url']['description']

        return packages

    def fetch(self, d):
        return d

    def import_data(self, d):
        d = import_package(d)
        d = metautils.gerToEngKeys(d)
        d['originating_portal'] = portalname
        d['accepted'] = True
        d['costs'] = None
        d['open'] = metautils.isopen(d['licenseshort'])
        d['publisher'] = None
        d['spatial'] = None
        d['source'] = 'd'
        d['metadata_xml'] = None
        d['filelist'] = d['files']

        return d
