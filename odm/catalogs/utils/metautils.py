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


def category_to_group(groupname):
        # maybe some other id
#        return {'name': force_alphanumeric_short(groupname), 'id': force_alphanumeric_short(groupname)}
        return {'name': force_alphanumeric_short(groupname)}
