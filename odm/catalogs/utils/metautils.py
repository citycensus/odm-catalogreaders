# -*- coding: utf-8 -*-

fileformats = ('CSV', 'XLS', 'XLSX', 'JSON', 'RDF', 'ZIP')
geoformats = ('GEOJSON', 'GML', 'GPX', 'GJSON', 'TIFF', 'SHP', 'KML', 'KMZ', 'WMS', 'WFS', 'GML2', 'GML3', 'SHAPE', 'OVL', 'IKT', 'CRS', 'TCX', 'DBF', 'SHX')

allfiletypes = []
allfiletypes.extend(fileformats)
allfiletypes.extend(geoformats)
allfiletypes = tuple(allfiletypes)


def isopen(licensetext):
    if any(licensetexttest in ("cc-by", "odc-by", "CC-BY 3.0", "dl-de-by-2.0", "dl-de/by-2-0", "CC-BY-SA 3.0", "other-open", "CC0-1.0", "cc-zero", "dl-de-zero-2.0", "Andere offene Lizenzen", "CC BY 3.0 DE", "dl-de-by-1.0", "dl-de-by 1.0", "gfdl", "odbl", "cc-by-sa") for licensetexttest in (licensetext.lower(), licensetext.upper())):
        return 'Offen'
    elif licensetext.lower() in ("other-closed", u"andere eingeschränkte lizenzen", u"andere eingeschränkte lizenz", "cc-nc", "CC-BY-ND 3.0", "CC BY-NC-ND 3.0 DE", "dl-de-by-nc-1.0", "CC BY-NC-SA 3.0 DE"):
        return 'Nicht offen'
    else:
        return 'Unbekannt'


def findLcGermanCharsAndReplace(germanstring):
    germanchars = (u'ü', u'ä', u'ö', u'é', u'ß')
    englishreplacements = ('ue', 'ae', 'oe', 'ee', 'ss')
    for x in range(0, len(germanchars)):
        if germanchars[x] in germanstring:
            germanstring = germanstring.replace(germanchars[x], englishreplacements[x])
    return germanstring


# Useful for CKAN import
def force_alphanumeric_short(title):
    title = findLcGermanCharsAndReplace(title.lower())
    retval = ''
    for char in title:
        if char == ' ':
            retval += '-'
        elif char.isalnum():
            retval += char
    return retval


def gerToEngKeys(d):
    mapping = {'city': u'Stadt',
               'source': u'Quelle',
               'title': u'Dateibezeichnung',
               'description': u'Beschreibung',
               'temporalextent': u'Zeitlicher Bezug',
               'licenseshort': u'Lizenz',
               'costs': u'Kosten',
               'publisher': u'Veröffentlichende Stelle'}
    mapping = {y: x for x, y in mapping.iteritems()}
    return {mapping.get(k, k): v for k, v in d.items()}


def govDataShortToODM(group):
    group = group.strip()
    if any(x == group for x in ('bevoelkerung', 'society')):
        return [u'Bevölkerung']
    elif any(x == group for x in('bildung_wissenschaft', 'bildung')):
        return [u'Bildung und Wissenschaft']
    elif 'wirtschaft' in group or group == 'economy':
        return [u'Wirtschaft und Arbeit']
    elif group == 'infrastruktur_bauen_wohnen':
        return [u'Infrastruktur, Bauen und Wohnen']
    elif any(x == group for x in ('geo', 'geografie', 'gdi-rp', 'boundaries')):
        return [u'Geographie, Geologie und Geobasisdaten']
    elif group == 'infrastruktur' or group == 'structure':
        return [u'Infrastruktur, Bauen und Wohnen']
    elif any (x == group for x in ('gesundheit', 'health')):
        return [u'Gesundheit']
    elif group == 'soziales' or group == 'sozial':
        return [u'Soziales']
    elif 'kultur' in group:
        return [u'Kultur, Freizeit, Sport, Tourismus']
    elif any (x == group for x in ('umwelt_klima', 'umwelt', 'environment', 'biota', 'oceans')):
        return [u'Umwelt und Klima']
    elif any(x == group for x in ('transport_verkehr', 'transport')):
        return [u'Transport und Verkehr']
    elif group == 'verbraucher':
        return [u'Verbraucherschutz']
    elif any(x == group for x in ('politik_wahlen', 'politik')):
        return [u'Politik und Wahlen']
    elif any(x == group for x in ('gesetze_justiz', 'justiz')):
        return [u'Gesetze und Justiz']
    elif group == 'verwaltung':
        return [u'Öffentliche Verwaltung, Haushalt und Steuern']
    else:
        print 'Warning: could not return a category for ' + group
        return []

    
def govDataLongToODM(group, checkAll=False):
    # The name is a misnomer: this checks for a valid govdata category and does some mapping where not. We have one extra category: Sonstiges
    # This is designed to cope either with a single category or a string with all categories. Quotes are allowed.
    # It has been extended to include the wild moers categories
    # Eventually, we need one function that matches all words, short and long to the govdata categories
    group = group.strip()
    returnvalue = []
    if u'Bevölkerung' in group:
        returnvalue.append(u'Bevölkerung')
        if not checkAll: return returnvalue
    if u'Bildung und Wissenschaft' in group:
        returnvalue.append(u'Bildung und Wissenschaft')
        if not checkAll: return returnvalue
    if u'Gesundheit' in group:
        returnvalue.append(u'Gesundheit')
        if not checkAll: return returnvalue
    if u'Transport und Verkehr' in group:
        returnvalue.append(u'Transport und Verkehr')
        if not checkAll: return returnvalue
    if u'Wahlen' in group:
        returnvalue.append(u'Politik und Wahlen')
        if not checkAll: return returnvalue
    if any (x.lower() in group.lower() for x in [u'Gesetze und Justiz', u'Recht']):
        returnvalue.append(u'Gesetze und Justiz')
        if not checkAll: return returnvalue
    if u'Wirtschaft und Arbeit' in group:
        returnvalue.append(u'Wirtschaft und Arbeit')
        if not checkAll: return returnvalue
    if any(x in group for x in [u'Verwaltung', u'Finanzen', ]):
        returnvalue.append(u'Öffentliche Verwaltung, Haushalt und Steuern')
        if not checkAll: return returnvalue
    if u'Infrastruktur, Bauen und Wohnen' in group:
        returnvalue.append(u'Infrastruktur, Bauen und Wohnen')
        if not checkAll: return returnvalue
    if u'Geo' in group:
        returnvalue.append(u'Geographie, Geologie und Geobasisdaten')
        if not checkAll: return returnvalue
    if u'Soziales' in group:
        returnvalue.append(u'Soziales')
        if not checkAll: return returnvalue
    if any(x in group for x in [u'Kultur', u'Tourismus']):
        returnvalue.append(u'Kultur, Freizeit, Sport, Tourismus')
        if not checkAll: return returnvalue
    if u'Umwelt und Klima' in group:
        returnvalue.append(u'Umwelt und Klima')
        if not checkAll: return returnvalue
    if u'Verbraucherschutz' in group:
        returnvalue.append(u'Verbraucherschutz')
        if not checkAll: return returnvalue
    #Moers only
    if u'Allgemein' in group:
        returnvalue.append(u'Sonstiges')
        if not checkAll: return returnvalue
    if u'Internet' in group:
        returnvalue.append('Öffentliche Verwaltung, Haushalt und Steuern')
        if not checkAll: return returnvalue
    if u'Kultur und Bildung' in group:
        returnvalue.extend([u'Bildung und Wissenschaft', u'Kultur, Freizeit, Sport, Tourismus'])
        if not checkAll: return returnvalue
    #end Moers only
    if len(returnvalue) == 0:
        print 'Warning: could not return a category for ' + group
    return returnvalue
    
