# -*- coding: utf-8 -*-
import urllib
import urllib2
import json
import os
from BeautifulSoup import BeautifulSoup
from odm.catalogs.utils import metautils
from odm.catalogs.CatalogReader import CatalogReader

# TODO: rework bonn


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


def gatherCity(cityname, url):
    if cityname in ("hamburg", "koeln", "bonn"):
        if cityname == 'bonn':
            jsonurl = urllib.urlopen(url + "/data.json")
        else:
            jsonurl = urllib.urlopen(url + "/api/3/action/package_list")
        listpackages = json.loads(jsonurl.read())

        if cityname != 'bonn':
            listpackages = listpackages['result']
        elif cityname == 'bonn':
            listpackages = listpackages[1:]

        groups = []

        print 'INFO: the names that follow have had special characters removed'
        for item in listpackages:
            if cityname == 'bonn':
                urltoread = url + "/api/3/action/package_show?id=" + item['identifier']
            else:
                urltoread = url + "/api/3/action/package_show?id=" + item

            print 'Downloading ' + metautils.findLcGermanCharsAndReplace(urltoread)
            trycount = 0
            try:
                req = urllib2.Request(urltoread.encode('utf8'))
                resp = urllib2.urlopen(req)
                urldata = resp.read()
            except IOError:
                if trycount == 100:
                    print 'Download failed 100 times, giving up...'
                    exit()
                print 'Something went wrong, retrying...'
                trycount += 1
            pdata = json.loads(urldata)
            if 'success' in pdata and pdata['success']:
                if cityname in ["koeln", "bonn"]:
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
            apikey = os.environ['BERLINCKANAPIKEY']
            request.add_header('Authorization', apikey)
            jsonurl = urllib2.urlopen(request, "{}")
        else:
            jsonurl = urllib.urlopen(url + "/api/3/action/current_package_list_with_resources")
        groups = json.loads(jsonurl.read())
        groups = groups['result']
    return groups


def importCity(cityname, url, package):
    if cityname == 'hamburg':
        # Only take 'open data'
        if package['type'] != 'dataset' or 'forward-reference' in package['title']:
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
    row[u'URL PARENT'] = url + '/dataset/' + package['name']
    if cityname in ('hamburg', 'koeln', 'frankfurt', 'aachen', 'berlin', 'muenchen'):
        if cityname in ('hamburg', 'frankfurt', 'aachen'):
            licensekey = 'license_id'
            vstellekey = 'author'
            catskey = 'groups'
            catssubkey = 'title'
        elif cityname == 'muenchen':
            licensekey = 'license_id'
            vstellekey = 'maintainer'
            catskey = 'groups'
            catssubkey = 'title'
        elif cityname in ('koeln', 'berlin'):
            licensekey = 'license_title'
            vstellekey = 'maintainer'
            if cityname == 'koeln':
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
        for group in metautils.setofvaluesasarray(package[catskey], catssubkey):
            if cityname != 'berlin':
                odm_cats = metautils.govDataLongToODM(group)
            else:
                odm_cats = berlin_to_odm(group)
            row[u'categories'] = odm_cats

    # Bonn is just different enough to do it separately. TODO: Consider combining into above.
    elif cityname == 'bonn':
        row[u'Beschreibung'] = package.get('description', '')
        for timeattempt in ['temporal', 'modified']:
            if timeattempt in package and package[timeattempt] not in [None, '']:
                row[u'Zeitlicher Bezug'] = package[timeattempt]
                break
        row[u'Zeitlicher Bezug'] = row.get(u'Zeitlicher Bezug', '')

        row[u'Lizenz'] = package.get('license', False)
        if not row[u'Lizenz']:
            row[u'Lizenz'] = package['license_title']

        row[u'Veröffentlichende Stelle'] = package.get('publisher', '')

        cats = package.get('keyword', [])
        odm_cats = map(lambda x: metautils.govDataLongToODM(x, checkAll=True), cats)
        resources = package.get(u'distribution', [])
        for r in resources:
            files.append(r[u'accessURL'])
            formats.append(r[u'format'])

    row[u'Format'] = formats
    row[u'files'] = files

    row['metadata'] = package
    return row


class CkanReader(CatalogReader):
    city = None
    url = None
    portalname = None

    def __init__(self, cityname):
        self.city = cityname
        if cityname == "koeln":
            self.url = "http://offenedaten-koeln.de"
            self.portalname = "offenedaten-koeln.de"
        elif cityname == "bonn":
            self.url = "http://opendata.bonn.de"
            self.portalname = "opendata.bonn.de"
        elif cityname == "hamburg":
            self.url = "http://suche.transparenz.hamburg.de"
            self.portalname = "transparenz.hamburg.de"
        elif cityname == "frankfurt":
            self.url = "http://www.offenedaten.frankfurt.de"
            self.portalname = "offenedaten.frankfurt.de"
        elif cityname == "aachen":
            self.url = "http://daten.aachen.de"
            self.portalname = "daten.aachen.de"
        elif cityname == "berlin":
            self.url = "http://datenregister.berlin.de"
            self.portalname = "datenregister.berlin.de"
        elif cityname == "muenchen":
            self.url = "http://www.opengov-muenchen.de"
            self.portalname = "opengov-muenchen.de"
        else:
            print 'First argument must be an city; unsupported city'
            exit()

    def info(self):
        return {
            'name': self.city + '_harvester',
            'title': str(self.portalname),
            'description': ''
        }

    def gather(self):
        data = gatherCity(self.city, self.url)
        return data

    def fetch(self, d):
        return d

    def import_data(self, d):
        d = importCity(self.city, self.url, d)
        if d != {}:
            d = metautils.gerToEngKeys(d)
            d = dict(d)
            d['originating_portal'] = self.portalname
            d['accepted'] = True
            d['costs'] = None
            d['spatial'] = None
            d['source'] = 'd'
            d['metadata_xml'] = None
            d['formats'] = list(d['formats'])
            d['open'] = metautils.isopen(d['licenseshort'].strip())
            if 'categoies' not in d:
                d['categories'] = []
            d['filelist'] = d['files']
        return d
