# -*- coding: utf-8 -*-
import urllib
import urllib2
import requests
import json
from BeautifulSoup import BeautifulSoup
from odm.catalogs.utils import metautils
from odm.catalogs.CatalogReader import CatalogReader

cities = {
        "koeln": {
            "url": "https://offenedaten-koeln.de",
            "portalname": "offenedaten-koeln.de"
        },
        "hamburg": {
            "url": "http://suche.transparenz.hamburg.de",
            "portalname": "transparenz.hamburg.de"
        },
        "frankfurt": {
            "url": "http://www.offenedaten.frankfurt.de",
            "portalname": "offenedaten.frankfurt.de"
        },
        "aachen": {
            "url": "http://daten.aachen.de",
            "portalname": "daten.aachen.de"
        },
        "berlin": {
            "url": "http://datenregister.berlin.de",
            "portalname": "datenregister.berlin.de"
        },
        "muenchen": {
            "url": "http://www.opengov-muenchen.de",
            "portalname": "opengov-muenchen.de"
        },
        "rostock": {
            "url": "http://opendata-hro.de",
            "portalname": "opendata-hro.de"
        },
        "meerbusch": {
            "url": "https://opendata.meerbusch.de",
            "portalname": "opendata.meerbusch.de"
        },
        "gelsenkirchen": {
            "url": "https://opendata.gelsenkirchen.de",
            "portalname": "opendata.gelsenkirchen.de"
        },
        "duesseldorf": {
            "url": "https://opendata.duesseldorf.de",
            "portalname": "opendata.duesseldorf.de"
        },
        "wuppertal": {
            "url": "https://offenedaten-wuppertal.de",
            "portalname": "offenedaten-wuppertal.de"
        },
        "muelheim-ruhr": {
            "url": "https://geo.muelheim-ruhr.de",
            "portalname": "geo.muelheim-ruhr.de"
        },
        "leipzig": {
            "url": "https://opendata.leipzig.de",
            "portalname": "opendata.leipzig.de"
        },
        "bonn": {
            "url": "https://opendata.bonn.de",
            "portalname": "opendata.bonn.de"
        }
    }

dkan_uuid = {
        "kerpen": "1fa89497-b1cd-4285-9b40-b5e8633eaa94",
        "bergheim": "c1679a1b-79bf-400f-8d8a-0cce2159846d",
        "bruehl": "bd4db65f-7e88-42be-a64f-57fb3f2572a5",
        "kall": "35fd9533-46f1-4c2a-a693-aea284c91fea",
        "elsdorf": "d9671f9a-66bc-4e30-b31f-31c754d6a156",
        "kreis-euskirchen": "e3249a69-3d2c-4820-9dcd-eb99b1bda0a0",
        "merzenich": "5f0bcd2a-b168-4246-9f2d-cd9f6aebafb3",
        "juelich": "2b036b3b-78f3-421d-a41b-28bd7e8ef23f",
        "huertgenwald": "5ea20e3b-1a82-4ba4-972d-8c4b6edac6f2",
        "langerwehe": "c8dfbe8d-e4be-42b4-ab0b-bb5fa4dc852d",
        "wesseling": "60a6b396-b6c3-4249-9d4a-be5d3a7db974",
        "vettweiss": "9d49d1bc-c848-4f3d-b2d8-4ca512a2bdbd",
        "heimbach": "f912b0c0-e177-4941-a16f-85fd47352fe6",
        "kreuzau": "ccd1e8f1-2377-415d-ad53-18020836f837",
        "linnich": "20395c82-822c-4b7a-99ea-979c30c150a0",
        "bad-muenstereifel": "bd8907bf-5320-415c-8d88-6c4b7bf1e264",
        "titz": "dde71ddf-4268-4e24-9137-a9d0bb1a7119",
        "bedburg": "52043d9c-5bfa-4c91-be58-522d96813ca2",
        "noervenich": "9e733787-ee58-4df5-bc9f-09bdafd90702",
        "niederzier": "ad9e9bfd-33be-4213-b846-ec28a33ffb3b"
        }

kdvz = ("kerpen", "bergheim", "bruehl", "kall", "elsdorf", "kreis-euskirchen", "merzenich", "juelich", "huertgenwald", "langerwehe", "wesseling", "vettweiss", "heimbach", "kreuzau", "linnich", "bad-muenstereifel", "titz", "bedburg", "noervenich", "niederzier")
offenesdatenportal = ("moers", "krefeld", "stadt-bottrop", "stadt-geldern", "stadt-kleve", "stadt-wesel", "kreis-wesel", "kreis-viersen", "kreis-kleve", "gemeinde-wachtendonk")

dkanCities = ("bonn", "koeln", "gelsenkirchen", "duesseldorf", "wuppertal", "muelheim-ruhr") + kdvz

datenportalWithOrganisations = offenesdatenportal

v3cities = offenesdatenportal + ("hamburg", "aachen", "frankfurt", "rostock", "meerbusch", "leipzig")
weiredCities = dkanCities + ("muenchen", )
v3AndSlightlyWeiredCities = v3cities + weiredCities
allCities = v3AndSlightlyWeiredCities


for city in offenesdatenportal:
    cities[city] = {
            "url": "https://www.offenesdatenportal.de",
            "portalname": "www.offenesdatenportal.de/organization/" + city
            }

for city in kdvz :
    cities[city] = {
            "url": "http://offenedaten.kdvz-frechen.de",
            "portalname": "http://offenedaten.kdvz-frechen.de/group/" + city
            }

def berlin_to_odm(group):
    # One dataset about WLAN locations...
    if group == 'oeffentlich':
        return [u'Infrastruktur, Bauen und Wohnen']
    if group in (u'demographie', u'jugend'):
        return [u'Bevölkerung']
    if group == u'bildung':
        return [u'Bildung und Wissenschaft']
    if group == u'gesundheit':
        return [u'Gesundheit']
    if group in (u'transport', u'verkehr'):
        return [u'Transport und Verkehr']
    if group == u'wahl':
        return [u'Politik und Wahlen']
    if group == u'justiz':
        return [u'Gesetze und Justiz']
    if group == u'geo':
        return [u'Infrastruktur, Bauen und Wohnen', u'Geographie, Geologie und Geobasisdaten']
    if group in (u'wohnen', u'verentsorgung'):
        return [u'Infrastruktur, Bauen und Wohnen']
    if group in (u'kultur', u'tourismus', u'erholung'):
        return [u'Kultur, Freizeit, Sport, Tourismus']
    if group == u'sozial':
        return [u'Soziales']
    if group == u'umwelt':
        return [u'Umwelt und Klima']
    if group == u'verbraucher':
        return [u'Verbraucherschutz']
    if group in (u'verwaltung', u'sicherheit'):
        return [u'Öffentliche Verwaltung, Haushalt und Steuern']
    if group in (u'wirtschaft', u'arbeit'):
        return [u'Wirtschaft und Arbeit']
    if group in (u'sonstiges', u'protokolle'):
        return [u'Sonstiges']
    else:
        print 'WARNING: Found no category or categories for ' + group
        return []


def gatherCity(cityname, url, apikey):
    if cityname in allCities:
        if cityname in datenportalWithOrganisations:
            r = requests.get(url + "/api/action/organization_show?include_datasets=true&id=" + cityname)
        elif cityname in kdvz:
            r = requests.get(url + "/api/3/action/group_package_show?id=" + dkan_uuid[cityname])
        else:
            r = requests.get(url + "/api/3/action/package_list")
        r.encoding = 'utf-8'
        listpackages = json.loads(r.text)

        if cityname in datenportalWithOrganisations:
            listpackages = listpackages['result']['packages']
        else:
            listpackages = listpackages['result']

        groups = []

        print 'INFO: the names that follow have had special characters removed'
        for item in listpackages:
            if cityname in datenportalWithOrganisations:
                urltoread = url + "/api/action/package_show?id=" + item['name']
            elif cityname in kdvz:
                urltoread = url + "/api/3/action/package_show?id=" + item['id']
            else:
                urltoread = url + "/api/3/action/package_show?id=" + item

            trycount = 0
            r = requests.get(urltoread)
            urldata = r.text
            pdata = json.loads(urldata)
            if 'success' in pdata and pdata['success']:
                if cityname in dkanCities:
                    # koeln has an empty dataset
                    if len(pdata['result']) > 0:
                        groups.append(pdata['result'][0])
                else:
                    groups.append(pdata['result'])
            else:
                print 'WARNING: No result - access denied?\n' + metautils.findLcGermanCharsAndReplace(item)
    else:
        print 'Downloading ' + url + "/api/3/action/current_package_list_with_resources..."
        if cityname == "berlin":
            # Berlin is special, it is CKAN 1.8 with V3 API in beta. We have to *post* with an empty dict. And we have to authenticate!
            request = urllib2.Request(url + '/api/3/action/current_package_list_with_resources')
            request.add_header('Authorization', apikey)
            jsonurl = urllib2.urlopen(request, "{}")
        else:
            jsonurl = urllib.urlopen(url + "/api/3/action/current_package_list_with_resources")
        groups = json.loads(jsonurl.read())
        groups = groups['result']
        #Our CKAN doesn't like owner_org=null even though this occasionally happens. Its also confusing as we use owner_org for our own purposes later.
        for group in groups:
            group.pop('owner_org', None)
    return groups


def importCity(cityname, url, package):
    if cityname == 'hamburg':
        # Only take 'open data'
        if package['type'] != 'dataset' or 'forward-reference' in package['title']:
            return {}

    #There is a version of CKAN that can output private datasets! but DKAN is using this field for different purposes
    if package['private'] and cityname not in dkanCities:
        return {}

    resources = []
    formats = set()
    files = []
    # Key for the file link in the resource
    urlkeys = ['url']
    formatkey = 'format'

    if ('resources' in package):
        resources = package['resources']

    for file in resources:
        for urlkey in urlkeys:
            if (file[urlkey] not in [None, '']):
                if '://' not in file[urlkey]:
                    files.append(url + file[urlkey])
                else:
                    files.append(file[urlkey])
                break
        if formatkey in file and file[formatkey] not in [None, '']:
            format = file[formatkey]
            formats.add(format.upper())

    row = {}

    row[u'Stadt'] = cityname
    row[u'Dateibezeichnung'] = package['title']
    if 'name' in package:
        row[u'URL PARENT'] = url + '/dataset/' + package['name']
    elif 'url' in package:
        row[u'URL PARENT'] = package['url']
    else:
        row[u'URL PARENT'] = ''
    if cityname in v3cities:
        licensekey = 'license_id'
        vstellekey = 'author'
        catskey = 'groups'
        catssubkey = 'title'
    elif cityname == 'muenchen':
        licensekey = 'license_id'
        vstellekey = 'maintainer'
        catskey = 'groups'
        catssubkey = 'title'
    elif cityname in ('berlin', ) + dkanCities:
        licensekey = 'license_title'
        vstellekey = 'maintainer'
        if cityname in dkanCities:
            catskey = 'tags'
        elif cityname == 'berlin':
            catskey = 'groups'
        catssubkey = 'name'
    # Generate URL for the catalog page
    if 'notes' in package and package['notes'] != None:
        row[u'Beschreibung'] = package['notes']
        if cityname == 'koeln':
            soup = BeautifulSoup(row[u'Beschreibung'])
            row[u'Beschreibung'] = soup.getText('\n')
    else:
        row[u'Beschreibung'] = ''
    row[u'Zeitlicher Bezug'] = ''
    if licensekey in package and package[licensekey] != None:
        row[u'Lizenz'] = package[licensekey]
        # if not already short, try to convert
        if metautils.isopen(row[u'Lizenz']) is 'Unbekannt':
            row[u'Lizenz'] = metautils.long_license_to_short(row[u'Lizenz'])
    else:
        row[u'Lizenz'] = 'nicht bekannt'
    if vstellekey in package and package[vstellekey] != None:
        row[u'Veröffentlichende Stelle'] = package[vstellekey]
    else:
        row[u'Veröffentlichende Stelle'] = ''
        if 'extras' in package:
            print 'WARNING: No author/maintainer/publisher, checking extras'
            for extra in package['extras']:
                if extra['key'] == 'contacts':
                    print 'WARNING: No author, but amazingly there is possibly data in the contacts: ' + extra['value']
    cat_groups = metautils.setofvaluesasarray(package[catskey], catssubkey)
    if cityname != 'berlin':
        odm_cats = metautils.matchCategories(cat_groups)
    else:
        for group in cat_groups:
            odm_cats = berlin_to_odm(group)
    row[u'categories'] = odm_cats

    row[u'Format'] = formats
    row[u'files'] = files

    row['metadata'] = package

    row[u'original_metadata'] = {
            u'metadata_created': package['metadata_created'],
            u'metadata_modified': package['metadata_modified']
            }

    return row


class CkanReader(CatalogReader):
    city = None
    url = None
    portalname = None

    def __init__(self, cityname):
        self.city = cityname
        if cityname in cities:
            self.url = cities[cityname]["url"]
            self.portalname = cities[cityname]["portalname"]
        else:
            print 'First argument must be an city; unsupported city'
            exit()

    def info(self):
        return {
            'name': self.city + '_harvester',
            'title': str(self.portalname),
            'description': ''
        }

    def gather(self, apikey = None):
        data = gatherCity(self.city, self.url, apikey)
        return data

    def fetch(self, d):
        return d

    def import_data(self, d):
        d = importCity(self.city, self.url, d)
        if d != {}:
            d = metautils.gerToEngKeys(d)
            d = dict(d)
            d['city'] = self.city
            d['originating_portal'] = self.portalname
            d['accepted'] = True
            d['costs'] = None
            d['spatial'] = None
            d['source'] = 'd'
            d['metadata_xml'] = None
            d['formats'] = list(d['formats'])
            d['open'] = metautils.isopen(d['licenseshort'].strip())
            if 'categories' not in d:
                d['categories'] = []
            d['filelist'] = d['files']
        return d
