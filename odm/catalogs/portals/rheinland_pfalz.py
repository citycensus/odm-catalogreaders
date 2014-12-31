# -*- coding: utf-8 -*-
import urllib
import json

from odm.catalogs.utils import datautils
from odm.catalogs.utils import metautils
from odm.catalogs.CatalogReader import CatalogReader
import os.path

dir = os.path.dirname(__file__)


portalname = 'daten.rlp.de'


def mapData(data, city=True):
    returndata = []
    for result in data:
        files = []
        resources = []
        package = result['item']
        row = {}

        if ('res_url' in package):
            resources = package['res_url']

        for file in resources:
            files.append(file)
        row[u'filelist'] = files
        if city:
            row[u'Stadt'] = metautils.getShortCityName(result['city']['originalname'])
        else:
            row[u'Stadt'] = 'rheinlandpfalz'

        row[u'url'] = 'http://www.daten.rlp.de/dataset/' + package['id']
        if ('res_format' in package):
            row[u'Format'] = list(set(package['res_format']))
            row[u'geo'] = metautils.isgeo(row[u'Format'])
        else:
            row[u'Format'] = None
            row[u'geo'] = None

        row[u'Dateibezeichnung'] = package['title']
        if 'notes' in package:
            row[u'Beschreibung'] = package['notes']
        else:
            row[u'Beschreibung'] = ''
        if 'license_id' in package:
            row[u'Lizenz'] = package['license_id']
        else:
            row[u'Lizenz'] = ''
        if 'maintainer' in package:
            row[u'Veröffentlichende Stelle'] = package['maintainer']
        else:
            row[u'Veröffentlichende Stelle'] = ''
        row['categories'] = map(lambda x: metautils.govDataShortToODM(x)[0], package.get('groups', []))
        row['metadata'] = package
        returndata.append(row)

    return returndata


def seperate_communal(data):
    # Separate out communal data
    allcities = datautils.getCities()
    # First take the Verbandsgemeinde
    cities = datautils.getCities(alternativeFile=os.path.join(dir, '../data/verbandsgemeinderlp.csv'))
    # Then all settlements in RLP
    cities.extend(datautils.filterCitiesByLand(allcities, 'Rheinland-Pfalz'))
    beforefilter = len(data['results'])
    [data, notcitydata] = datautils.findOnlyCityData(data['results'], cities)
    afterfilter = len(data)
    print 'Of the total ' + str(beforefilter) + ' records, ' + str(afterfilter) + ' appear to be related to a city'
    print 'The rest (' + str(len(notcitydata)) + ') will be assigned to Rheinland-Pfalz as a Land'
    return [data, notcitydata]


class RlpReader(CatalogReader):
    def info(self):
        return {
            'name': 'rlp_harvester',
            'title': u'daten.rlp.de',
            'description': ''
        }

    def gather(self):
        limit = 1000  # N.B. max limit is 1000
        urlbase = "http://www.daten.rlp.de/api/2/search/dataset?q=&limit=" + str(limit) + "&all_fields=1"
        jsonurl = urllib.urlopen(urlbase)
        data = json.loads(jsonurl.read())
        gotdata = data
        while len(gotdata['results']) > 0:
            gotdata = json.loads(urllib.urlopen(urlbase + "&offset=" + str(limit)).read())
            data['results'].extend(gotdata['results'])
            limit += 1000
        [communal, land] = seperate_communal(data)
        data = mapData(communal)
        data = data + mapData(land, False)
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
        d['accepted'] = True
        return d


#r = RlpReader()
#d = r.read_data()
# #import pprint
# #pprint.pprint(d)

# from odm.catalogs.utils import dbsettings
# dbsettings.addSimpleDataToDB(d,
#                              portalname,
#                              checked=True,
#                              accepted=True,
#                              remove_data=True)
