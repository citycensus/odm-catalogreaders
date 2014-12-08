# -*- coding: utf-8 -*-

fileformats = ('CSV', 'XLS', 'XLSX', 'JSON', 'RDF', 'ZIP')
geoformats = ('GEOJSON', 'GML', 'GPX', 'GJSON', 'TIFF', 'SHP', 'KML', 'KMZ', 'WMS', 'WFS', 'GML2', 'GML3', 'SHAPE', 'OVL', 'IKT', 'CRS', 'TCX', 'DBF', 'SHX')
allfiletypes = []
allfiletypes.extend(fileformats)
allfiletypes.extend(geoformats)
allfiletypes = tuple(allfiletypes)


def isopen(licensetext):
    if any(licensetexttest in ("cc-by", "odc-by", "CC-BY 3.0", "dl-de-by-2.0", "dl-de/by-2-0", "CC-BY-SA 3.0", "other-open", "CC0-1.0", "cc-zero", "dl-de-zero-2.0", "Andere offene Lizenzen", "CC-BY-ND 3.0", "CC BY-NC-ND 3.0 DE", "CC BY 3.0 DE", "cc-nc", "dl-de-by-1.0", "dl-de-by 1.0", "dl-de-by-nc-1.0", "CC BY-NC-SA 3.0 DE") for licensetexttest in (licensetext.lower(), licensetext.upper())):
        return 'Nicht offen'
    elif licensetext.lower() in ("other-closed", u"andere eingeschränkte lizenzen"):
        return 'Offen'
    else:
        return 'Unbekannt'
