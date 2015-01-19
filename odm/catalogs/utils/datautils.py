# -*- coding: utf-8 -*-
import unicodecsv as csv
from odm.catalogs.utils import metautils
import os.path

dir = os.path.dirname(__file__)

def getCities(alternativeFile=''):
    if alternativeFile == '':
        filetoread = os.path.join(dir, '../data/settlementsInGermany.csv')
    else:
        filetoread = alternativeFile
    with open(filetoread, 'rb') as csvfile:
        cityreader = csv.reader(csvfile, delimiter=',')
        cities = []
        for row in cityreader:
            # First column is word to look for, second is original city name
            newname = row[0].lower()
            newname = metautils.findLcGermanCharsAndReplace(newname)
            cityToAdd = dict()
            cityToAdd['shortname'] = row[0].lower()
            cityToAdd['shortnamePadded'] = ' ' + cityToAdd['shortname'].title() + ' '
            cityToAdd['originalname'] = row[1]
            if len(row) > 2:
                cityToAdd['land'] = row[2]
            cities.append(cityToAdd)
            if newname != row[0].lower():
                newCity = cityToAdd.copy()
                newCity['shortname'] = newname
                newCity['shortnamePadded'] = ' ' + newCity['shortname'] + ' '
                cities.append(newCity)
        return cities


def filterCitiesByLand(cities, land):
    citiesreturned = []
    for city in cities:
        if city['land'] == land:
            citiesreturned.append(city)
    return citiesreturned


# City names can be found in all sorts of places, but they shouldn't be found as parts of
# words. Therefore a good test is to see if they appear as whole words. A simple test for
# whole words is to see if the word is surrounded by spaces. This function reduces other
# separating items to spaces as a pre-processing step. In case the city might be mentioned
# at the very beginning, we add a space at the beginning, ditto at the end.
def createwholelcwords(words):
    return ' ' + words.replace(',', ' ').replace('.', ' ').replace('\n', ' ') + ' '


# There are times when we need to test for city names without expecting whole words, like
# email addresses. But then we really have to rule out a few things. Stein, Au and Bunde are always
# ignored, and stelle (the city) must not be matched against the word poststelle.
def testnospacematch(cityname, searchtext):
    return (not any(x in cityname for x in baninemails) and
            not ('poststelle' in searchtext.lower() and cityname == 'stelle') and
            cityname in searchtext.lower())


def extract_em_domain(email):
    return email.split('@')[-1]


# Things that are banned everywhere (except emails, different kind of search)
# Used for tags
banlevel1 = ('konstanz', 'boden', 'wald', 'nusse', 'fisch', 'berge', 'wiesen', 'heide', 'loehne', u'löhne', 'bruecken', u'brücken', 'lichtenberg')

# More things that are banned everywhere (except tags)
# Used for titles
banlevel2 = list(banlevel1)
banlevel2.extend(['sylt', 'jade', 'erden', 'gering', 'balje', 'breit', 'auen', 'stelle', 'ohne', 'bescheid', 'lage', 'muessen', u'müssen', 'steinen', 'schutz', 'elbe', 'fahren', 'plate', 'wellen', 'bodensee'])
banlevel2 = tuple(banlevel2)

# More things that are banned everywhere (except titles)
# Used for notes, contact points
banlevel3 = list(banlevel2)
banlevel3.extend(['norden', 'list'])
banlevel3 = tuple(banlevel3)

# Finally some things that are bad in email addresses
# au is in bau, and haus and goodness knows what else
# stelle is in poststelle and handled specially (below)
baninemails = ('stein', 'au', 'bunde')


# Try to get data that relates to a 'city'
def findOnlyCityData(data, cities, verbose=False):
    foundItems = []
    notfoundItems = []

    for item in data:
        founditem = False
        foundcity = None
        matchedon = ''
        if ('maintainer' in item and item['maintainer'] != None):
            searchtext = createwholelcwords(item['maintainer'])
            for city in cities:
                if city['shortname'] not in banlevel3 and city['shortnamePadded'] in searchtext:
                        if verbose: print 'Found in maintainer: ' + city['shortname'] + '\nin\n' + searchtext
                        founditem = True
                        foundcity = city
                        matchedon = 'maintainer'
                        break
        if ((not founditem) and 'author' in item and item['author'] != None):
            searchtext = createwholelcwords(item['author'])
            for city in cities:
                if city['shortname'] not in banlevel3 and city['shortnamePadded'] in searchtext:
                    if verbose: print 'Found in author: ' + city['shortname'] + '\nin\n' + searchtext
                    founditem = True
                    foundcity = city
                    matchedon = 'author'
                    break
        if ((not founditem) and 'maintainer_email' in item and item['maintainer_email'] != None):
            for city in cities:
                if testnospacematch(city['shortname'], extract_em_domain(item['maintainer_email'])):
                    if verbose: print 'Found in maintainer email domain: ' + city['shortname'] + '\nin\n' + item['maintainer_email'].lower()
                    founditem = True
                    foundcity = city
                    matchedon = 'maintainer_email'
                    break
        if ((not founditem) and 'author_email' in item and item['author_email'] != None):
            for city in cities:
                if testnospacematch(city['shortname'], extract_em_domain(item['author_email'])):
                    if verbose: print 'Found in author email domain: ' + city['shortname'] + '\nin\n' + item['author_email'].lower()
                    founditem = True
                    foundcity = city
                    matchedon = 'author_email'
                    break
        if ((not founditem) and 'title' in item and item['title'] != None):
            searchtext = createwholelcwords(item['title'])
            for city in cities:
                if city['shortname'] not in banlevel2 and city['shortnamePadded'] in searchtext:
                    if verbose: print 'Found in title: ' + city['shortname'] + '\nin\n' + searchtext
                    founditem = True
                    foundcity = city
                    matchedon = 'title'
                    break
        if ((not founditem) and 'notes' in item and item['notes'] != None):
            searchtext = createwholelcwords(item['notes'])
            for city in cities:
                if city['shortname'] not in banlevel3 and city['shortnamePadded'] in searchtext:
                    if verbose: print 'Found in notes: ' + city['shortname'] + '\nin\n' + searchtext
                    founditem = True
                    foundcity = city
                    matchedon = 'notes'
                    break
        if ((not founditem) and 'tags' in item and len(item['tags']) != 0):
            for city in cities:
                if (founditem):
                    break
                for tag in item['tags']:
                    # Tag must be exact match
                    if city['shortname'] == tag.lower() and tag.lower() not in banlevel1:
                        if verbose: print 'Matched tag: ' + city['shortname'] + '\nin\n' + tag.lower()
                        founditem = True
                        foundcity = city
                        matchedon = 'tags'
                        break
        if founditem:
            recordtoadd = dict()
            recordtoadd['item'] = item
            recordtoadd['city'] = foundcity
            recordtoadd['match'] = matchedon
            foundItems.append(recordtoadd)
        else:
            recordtoadd = dict()
            recordtoadd['item'] = item
            notfoundItems.append(recordtoadd)

    return [foundItems, notfoundItems]
