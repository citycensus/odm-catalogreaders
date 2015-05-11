# -*- coding: utf-8 -*-
import itertools
from lxml import html
from lxml import etree

from odm.catalogs.utils import metautils
from odm.catalogs.CatalogReader import CatalogReader

verbose = False
rooturl = u'http://www.bochum.de'
url = u'/opendata/datensaetze/nav/75F9RD294BOLD'


def findfilesanddata(html):
    # Start to get the data for each dataset
    tables = html.xpath('//table')
    # Tables with captions contain info, tables with no caption and no border contain the files
    datatables = []
    filetables = []
    for table in tables:
        # We append the text because for some reason the objects are weird and contain data from elsewhere in the page
        if len(table.xpath('caption')) == 1:
            datatables.append(etree.tostring(table))
            if (verbose): print 'Found table of data'
        if len(table.xpath('caption')) == 0 and len(table.xpath('@border')) > 0 and table.xpath('@border')[0] == '0':
            if (verbose): print 'Found table of files'
            filetables.append(etree.tostring(table))
    return datatables, filetables


def get_datasets(data):
    # Get the number of datasets
    datasets = data.xpath('//body//h2/text()')
    # Maybe it's there, maybe it isn't
    if 'Inhaltsverzeichnis' in datasets:
        datasets.remove('Inhaltsverzeichnis')
    return datasets


def get_categorie_urls():
    if (verbose): print u'Reading page of categories: ' + rooturl + url
    data = html.parse(rooturl + url)

    # Get the first spanned URL in each cell. There must be a way to do this all in one xpath query
    cat_sites = data.xpath('//body//table//td')
    cat_urls = []
    for cat_site in cat_sites:
        cat_site_url = cat_site.xpath('span[1]/a/@href')[0]
        if 'neueste-datensaetze' not in cat_site_url:
            cat_urls.append(cat_site_url)
    if (verbose): print str(len(cat_urls)) + ' categories found'
    return cat_urls


def get_categorie_content(category_link):
    # Get the page
    allrecords = []

    parser = etree.HTMLParser(encoding='utf-8')
    data = etree.parse(rooturl + category_link, parser)
    # Get the category
    category = data.xpath('/html/body/div/div[5]/div/div[1]//h1/text()')[0].strip()
    # category = urllib.unquote(category).decode('utf8')
    if (verbose): print 'Category: ' + ascii_only(category)

    datasets = get_datasets(data)
    numdatasets = len(datasets)

    if (verbose): print 'There are ' + str(numdatasets) + ' datasets'

    # Now get the html for each one. This is painful.
    # The bit of html concerning the datasets:
    corehtml = data.xpath('//div[@id=\'ContentBlock\']')[0]
    # First try to split by the horizontal rules. This usually works, but not always
    datasetparts = etree.tostring(corehtml).split('<hr id="hr')
    if (verbose): print 'Found ' + str(len(datasetparts)) + ' datasets by splitting by hr elements with ids'
    if len(datasetparts) != numdatasets:
        if (verbose): print 'This doesn\'t match. Trying with links to TOC'
        # If there is TOC, this works. There isn\'t always one.
        datasetparts = etree.tostring(corehtml).split('nach oben')
        del datasetparts[len(datasetparts) - 1]
        for index in range(0, len(datasetparts)):
            datasetparts[index] = datasetparts[index] + '</a>'
        if (verbose): print 'Found ' + str(len(datasetparts)) + ' datasets by splitting by links to TOC'
        if len(datasetparts) != numdatasets:
            if (verbose): print 'Well, that didn\'t work either. Giving up'
            print 'Exciting because of a serious error - turn on verbose in the code to find out what dataset is causing the problem'
            exit()
    else:
        if numdatasets > 1:
            for index in range(1, len(datasetparts)):
                # That split makes for bad HTML. Make it better.
                datasetparts[index] = '<hr id="hr' + datasetparts[index]

    count = 1

    for datasetpart in datasetparts:
        data = etree.HTML(datasetpart)
        record = {}
        record['city'] = 'bochum'
        record['categories'] = []
        record['categories'].append(category)

        datasets = get_datasets(data)
        record['title'] = datasets[0]

        if (verbose): print 'Parsing dataset ' + ascii_only(record['title'])
        if 'noch im Aufbau' in record['title']:
           # Nothing to see here
           if (verbose): print 'Empty category'
           continue
        record['url'] = rooturl + category_link + '#par' + str(count)
        count += 1
        datatables, filetables = findfilesanddata(data)

        if len(datatables) == 0:
            if (verbose): print 'This record contains no data... checking for link to another page...'
            checkforsubpage = data.xpath('//span//a')

            for link in checkforsubpage:
                if (verbose): print etree.tostring(link)
                if len(link.xpath('text()')) > 0 and u'zu den Daten' in link.xpath('text()')[0]:
                    testurl = link.xpath('@href')[0]
                    if (verbose): print 'Following/updating URL: ' + rooturl + testurl
                    record['url'] = rooturl + testurl
                    datatables, filetables = findfilesanddata(html.parse(rooturl + testurl))

        # get the data on the files, and get each link in it
        record['filelist'] = []
        for table in filetables:
            record['filelist'].extend([(rooturl + x) for x in etree.HTML(table).xpath('//a/@href')])

        record['formats'] = set()
        record['spatial'] = False
        for file in record['filelist']:
            formatarray = file.split('/')[-1].split('.')
            format = 'Unknown'
            if len(formatarray)>1:
                format = formatarray[1].upper().split('?')[0]
            elif 'WMS' in formatarray[0]:
                format = 'WMS'
            elif 'WFS' in formatarray[0]:
                format = 'WFS'
            record['formats'].add(format)
            if (format.upper() in metautils.geoformats):
                record['spatial'] = True
        record['formats'] = list(record['formats'])

        if len(datatables) > 1:
            if (verbose): print 'ERROR: More than one data table'
            print 'Exciting because of a serious error - turn on verbose in the code to find out what dataset is causing the problem'
            exit()
        elif len(datatables) == 0:
            if (verbose): print 'ERROR: No data table'
            print 'Exciting because of a serious error - turn on verbose in the code to find out what dataset is causing the problem'
            exit()

        # parse the data table by row
        if (verbose): print 'Reading datatable...'
        rowelements = etree.HTML(datatables[0]).xpath('//tr')
        for row in rowelements:
            if len(row.xpath('td[1]/text()')) == 0: continue
            key = row.xpath('td[1]/text()')[0]
            if (verbose): print ascii_only(key)
            if len(row.xpath('td[2]/text()')) != 0:
                val = row.xpath('td[2]/text()')[0]
            elif len(row.xpath('td[2]//a')) != 0:
                val = row.xpath('td[2]//a/text()')[0]
            else:
                if (verbose): print 'ERROR: Missing value'
                print 'Exciting because of a serious error - turn on verbose in the code to find out what dataset is causing the problem'
                exit()
            if (verbose): print ascii_only('Parsing key ' + key.replace(':', '') + ' with value ' + val)
            if u'veröffentlicht' in key:
                record['publisher'] = val
            elif u'geändert' in key:
                record['temporalextent'] = val.split(' ')[2]
            elif u'Lizenz' in key:
                record['licenseshort'] = metautils.long_license_to_short(val)
                record['open'] = metautils.isopen(record['licenseshort'])
            elif u'Webseite' in key:
                record['website'] = row.xpath('td[2]//a/@href')[0]  # keep, as 'original' metadata
                if 'http://' not in record['website']:
                    record['website'] = rooturl + record['website']
            elif u'Kontakt' in key:
                record['contact'] = rooturl + row.xpath('td[2]//a/@href')[0]

        allrecords.append(record)
    return allrecords


def remove_multiples(allrecords):
    # Find things in multiple categories
    recordsdict = {}
    for record in allrecords:
        if record['title'] not in recordsdict:
            recordsdict[record['title']] = record
        else:
            if (verbose): print ascii_only(record['title']) + ' in ' + ascii_only(str(record['categories'])) + ' is already in ' + ascii_only(str(recordsdict[record['title']]['categories'])) + '. Transferring category.'
            recordsdict[record['title']]['categories'].extend(record['categories'])
    return recordsdict.values()

def ascii_only(text):
    return ''.join(i for i in text if ord(i)<128) + ' (ascii only)'

class BochumReader(CatalogReader):
    def info(self):
        return {
            'name': 'bochum_harvester',
            'title': u'bochum.de',
            'description': ''
        }

    def gather(self):
        cat_urls = get_categorie_urls()
        cat_recs = map(get_categorie_content, cat_urls)
        all_recs = list(itertools.chain(*cat_recs))
        all_recs = remove_multiples(all_recs)
        return all_recs

    # Everthing is done in the gather stage right now,
    # since I don't know, the right method to prevent adding duplicates,
    # at this point
    def fetch(self, d):
        return d

    def import_data(self, record):
        # Expand categories
        record['originating_portal'] = "bochum.de/opendata"
        record['metadata'] = record.copy()
        record['source'] = 'd'
        record['description'] = None
        record['costs'] = None
        record['metadata_xml'] = None
        record['accepted'] = True
        odm_cats = map(lambda x: metautils.govDataLongToODM(x, checkAll=True)[0], record['categories'])
        if len(odm_cats) > 0:
            record['categories'] = odm_cats
        else:
            record['categories'] = ['Noch nicht kategorisiert']

        return record
