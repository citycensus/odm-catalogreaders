# -*- coding: utf-8 -*-
import urllib2
from lxml import html
from lxml import objectify
from odm.catalogs.utils import metautils
from odm.catalogs.CatalogReader import CatalogReader

# meta data json probably wrong !!!!!!!!!!!!!!!!!!!!!!!!!!!! have a look at that

root = u'http://daten.ulm.de'
startUrl = root + u'/suche?search_api_views_fulltext='


def gatherData():
    page = 0
    alldata = []

    dataCount = -1

    while True:
        if dataCount == 0:
            print u'INFO: Search page contained no results, stopping.'
            # Done
            break
        if dataCount != -1:
            print u'INFO: Search page contained ' + str(dataCount) + ' results, ' + str(len(alldata)) + ' datasets downloaded so far'
        dataCount = 0
        searchurl = startUrl + '&page=' + str(page)
        print u'Reading search page ' + searchurl
        data = html.parse(searchurl)
        page += 1
        sites = data.xpath('//body//a')
        for site in sites:
            if len(site.xpath('@href')) > 0:
                dataurl = site.xpath('@href')[0]
            else:
                continue

            if ('/daten/' in dataurl) or ('/datenkatalog/' in dataurl):
                dataCount += 1
                #Not all data records contain actual files; geo services have a download form
                #It would be nice if this gave us the node id, and then we could just
                #call the XML link directly. But its an alias, so to find the actual node
                #id/link for XML (which doesn't work with aliases), we have to look at the page,
                #the link to the XML is a good place to start; it is relative so in the end we still
                #create the link ourselves.
                dataurl = root + dataurl

                print u'Reading dataset page ' + dataurl
                try:
                    datapage = html.parse(dataurl)
                except:
                    print u'WARNING: Could not download ' + dataurl
                    continue

                links = datapage.xpath('//body//a')

                data_dict = {}
                data_dict['url'] = dataurl
                data_dict['filelist'] = []
                for link in links:
                    if len(link.xpath('@href')) > 0:
                        linkurl = link.xpath('@href')[0]
                    else:
                        continue

                    #Get files... they are not listed in the XML...!
                    #Seems that link files have a nice type attribute
                    if len(link.xpath('@type')) > 0:
                        print 'Found file: ' + link.xpath('@href')[0]
                        data_dict['filelist'].append(link.xpath('@href')[0] + '\n')

                    #Find the license, also not in XML  
                    if len(link.xpath('@rel')) > 0 and link.xpath('@rel')[0] == 'license' and link.text is not None:
                        print 'Found license: ' + link.text
                        data_dict['license'] = link.text
                    #Find the metadata XML    
                    if ('/iso19139/' in linkurl):
                        node = linkurl.split('/')[-1]
                        xmlurl = root + u'/datenkatalog/iso19139/' + node
                        print u'Downloading XML from ' + xmlurl

                        response = urllib2.urlopen(xmlurl)
                        xml = unicode(response.read(), 'utf-8')
                        data_dict['metadata_xml'] = xml.replace('&', '&amp;')
                alldata.append(data_dict)

    return alldata


def decrypt_role(role):
    # Based on http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml
    if role == 'resourceProvider':
        return 'Provider'
    elif role == 'custodian':
        return 'Custodian'
    elif role == 'owner':
        return 'Owner'
    elif role == 'user':
        return 'User'
    elif role == 'distributor':
        return 'Distributor'
    elif role == 'originator':
        return 'Originator'
    elif role == 'pointOfContact':
        return 'Point of Contact'
    elif role == 'principalInvestigator':
        return 'Principal Investigator'
    elif role == 'processor':
        return 'Processor'
    elif role == 'publisher':
        return 'Publisher'
    elif role == 'author':
        return 'Author'
    else:
        return 'Unbekannt'


ns1 = '{http://www.isotc211.org/2005/gmd}'
ns2 = '{http://www.isotc211.org/2005/gco}'
ns3 = '{http://www.isotc211.org/2005/srv}'
ns4 = '{http://www.opengis.net/gml/3.2}'


def readXmlPart(part):
    if part != '':
        record = dict()
        record['xml'] = part
        root = objectify.fromstring(part)

        maintainer = root[ns1+'contact'][ns1+'CI_ResponsibleParty']
        record['maintainername'] = maintainer[ns1+'individualName'][ns2+'CharacterString'].text
        record['maintainerposition'] = maintainer[ns1+'positionName'][ns2+'CharacterString'].text
        record['maintainerorganisation'] = maintainer[ns1+'organisationName'][ns2+'CharacterString'].text

        maintainerContact = maintainer[ns1+'contactInfo'][ns1+'CI_Contact']
        maintainerContactPhone = maintainerContact[ns1+'phone'][ns1+'CI_Telephone']

        record['maintainerphone'] = maintainerContactPhone[ns1+'voice'][ns2+'CharacterString'].text
        record['maintainerfax'] = maintainerContactPhone[ns1+'facsimile'][ns2+'CharacterString'].text

        maintainerContactAddress = maintainerContact[ns1+'address'][ns1+'CI_Address']

        record['maintaineraddress'] = maintainerContactAddress[ns1+'deliveryPoint'][ns2+'CharacterString'].text + '\n' + \
            maintainerContactAddress[ns1+'city'][ns2+'CharacterString'].text + '\n' + \
            maintainerContactAddress[ns1+'postalCode'][ns2+'CharacterString'].text + '\n' + \
            maintainerContactAddress[ns1+'country'][ns2+'CharacterString'].text
        record['maintaineremail'] = maintainerContactAddress[ns1+'electronicMailAddress'][ns2+'CharacterString'].text

        record['maintainerrole'] = decrypt_role(maintainer[ns1+'role'][ns1+'CI_RoleCode'].attrib['codeListValue'])

        record['datacatalogdate'] = root[ns1+'dateStamp'][ns2+'DateTime'].text

        details = None
        if root[ns1+'identificationInfo'].getchildren()[0].tag == (ns1+'MD_DataIdentification'):
            details = root[ns1+'identificationInfo'][ns1+'MD_DataIdentification']
        elif root[ns1+'identificationInfo'].getchildren()[0].tag == (ns3+'SV_ServiceIdentification'):
            details = root[ns1+'identificationInfo'][ns3+'SV_ServiceIdentification']
        #Rather bizarre case where the middle identifier is missing
        elif root[ns1+'identificationInfo'].getchildren()[0].tag == (ns1+'citation'):
            details = root[ns1+'identificationInfo']
        else:
            print 'Unknown entity type: ' + root[ns1+'identificationInfo'].getchildren()[0].tag + '. Quitting...'
            exit()

        detailsCitation = details[ns1+'citation'][ns1+'CI_Citation']

        record['title'] = detailsCitation[ns1+'title'][ns2+'CharacterString'].text

        record['datadate'] = ''
        if detailsCitation[ns1+'date'][ns1+'CI_Date'][ns1+'date'].getchildren()[0].tag == (ns2+'DateTime'):
            record['datadate'] = detailsCitation[ns1+'date'][ns1+'CI_Date'][ns1+'date'][ns2+'DateTime'].text
        elif detailsCitation[ns1+'date'][ns1+'CI_Date'][ns1+'date'].getchildren()[0].tag == (ns1+'extent'):
            record['datadate'] = detailsCitation[ns1+'date'][ns1+'CI_Date'][ns1+'date'][ns1+'extent'][ns4+'TimePeriod'][ns4+'beginPosition'].text + \
                ' - ' + detailsCitation[ns1+'date'][ns1+'CI_Date'][ns1+'date'][ns1+'extent'][ns4+'TimePeriod'][ns4+'endPosition'].text
        else:
            print 'Unknown citation date type: ' + detailsCitation[ns1+'date'].getchildren()[0].tag + '. Quitting...'
            exit()

        # Not worth doing lookup
        record['datadatetype'] = detailsCitation[ns1+'date'][ns1+'CI_Date'][ns1+'dateType']['CI_DateTypeCode'].attrib['codeListValue']

        record['url'] = detailsCitation[ns1+'identifier'][ns1+'MD_Identifier'][ns1+'code'][ns2+'CharacterString'].text

        #TODO: Consider doing lookup as above for role
        record['form'] = detailsCitation[ns1+'presentationForm'][ns1+'CI_PresentationFormCode'].attrib['codeListValue']

        record['abstract'] = details[ns1+'abstract'][ns2+'CharacterString'].text

        contact = details[ns1+'pointOfContact'][ns1+'CI_ResponsibleParty']

        #TODO, consider wrapping into function to handle this and maintainer above
        record['contactname'] = contact[ns1+'individualName'][ns2+'CharacterString'].text
        record['contactorganisation'] = contact[ns1+'organisationName'][ns2+'CharacterString'].text
        record['contactposition'] = contact[ns1+'positionName'][ns2+'CharacterString'].text

        contactDetails = contact[ns1+'contactInfo'][ns1+'CI_Contact']
        contactPhone = contactDetails[ns1+'phone'][ns1+'CI_Telephone']
        contactAddress = contactDetails[ns1+'address'][ns1+'CI_Address']

        record['contactphone'] = contactPhone[ns1+'voice'][ns2+'CharacterString'].text
        record['contactfax'] = contactPhone[ns1+'facsimile'][ns2+'CharacterString'].text

        record['contactaddress'] = contactAddress[ns1+'deliveryPoint'][ns2+'CharacterString'].text + '\n' + \
            contactAddress[ns1+'city'][ns2+'CharacterString'].text + '\n' + \
            contactAddress[ns1+'postalCode'][ns2+'CharacterString'].text + '\n' + \
            contactAddress[ns1+'country'][ns2+'CharacterString'].text
        record['contactemail'] = contactAddress[ns1+'electronicMailAddress'][ns2+'CharacterString'].text

        record['contactrole'] = decrypt_role(contact[ns1+'role'][ns1+'CI_RoleCode'].attrib['codeListValue'])

        #Not worth doing lookup
        record['frequpdated'] = details[ns1+'resourceMaintenance'][ns1+'MD_MaintenanceInformation'][ns1+'maintenanceAndUpdateFrequency'][ns1+'MD_MaintenanceFrequencyCode'].attrib['codeListValue']
        #....still inside details

        #Keywords. Nightmare. At the end we will go through and see how many unique categories of categories there are...
        keywordsXML = details[ns1+'descriptiveKeywords']

        record['keywords'] = []
        for keyworddata in keywordsXML:
            for keyword in keyworddata[ns1+'MD_Keywords'][ns1+'keyword'][ns2+'CharacterString']:
                record['keywords'].append(keyword.text)

        #And just for extra merit, we have a topic category too for data entries
        record['topiccategory'] = ''
        try:
            topicCategory = details[ns1+'topicCategory'][ns1 + 'MD_TopicCategoryCode']
            record['topiccategory'] = details[ns1+'topicCategory'][ns1 + 'MD_TopicCategoryCode'].text
        except:
            pass

        record['uselimitations'] = details[ns1+'resourceConstraints'][0][ns1+'MD_Constraints'][ns1+'useLimitation'].text
        record['accesscontraints'] = ''
        record['useconstraints'] = ''

        if details[ns1+'resourceConstraints'][1][ns1+'MD_LegalConstraints'][ns1+'accessConstraints'][ns1+'MD_RestrictionCode'].attrib['codeListValue'] == 'restricted':
            record['accessconstraints'] = details[ns1+'resourceConstraints'][1][ns1+'MD_LegalConstraints'][ns1+'accessConstraints'][ns1+'MD_RestrictionCode'].text
        else:
            print 'WARNING: Didn\'t find a description of access restriction when expecting one'
        if details[ns1+'resourceConstraints'][1][ns1+'MD_LegalConstraints'][ns1+'useConstraints'][ns1+'MD_RestrictionCode'].attrib['codeListValue'] == 'license':
            record['useconstraints'] = details[ns1+'resourceConstraints'][1][ns1+'MD_LegalConstraints'][ns1+'useConstraints'][ns1+'MD_RestrictionCode'].text
        else:
            print 'WARNING: Didn\'t find a description of use license when expecting one'

        distributionInfo = root[ns1+'distributionInfo'][ns1+'MD_Distribution']

        record['format'] = distributionInfo[ns1+'distributionFormat'][ns1+'MD_Format'][ns1+'name'][ns2+'CharacterString'].text
        record['geo'] = ''

        if any(x.upper() in record['format'].upper() for x in metautils.geoformats):
            record['geo'] = 'x'
            print 'INFO: Geo data found. Format was ' + record['format']
        else:
            print 'INFO: Not geo. Format was ' + record['format']

        #TODO, consider wrapping into function to handle this and maintainer above
        distributionDetails = distributionInfo[ns1+'distributor'][ns1+'MD_Distributor']  
        distributorContact = distributionDetails[ns1+'distributorContact'][ns1+'CI_ResponsibleParty']

        record['distributorname'] = distributorContact[ns1+'individualName'][ns2+'CharacterString'].text
        record['distributororganisation'] = distributorContact[ns1+'organisationName'][ns2+'CharacterString'].text
        record['distributorposition'] = distributorContact[ns1+'positionName'][ns2+'CharacterString'].text

        distributorContactDetails = distributorContact[ns1+'contactInfo'][ns1+'CI_Contact']
        distributorContactPhone = distributorContactDetails[ns1+'phone'][ns1+'CI_Telephone']
        distributorContactAddress = distributorContactDetails[ns1+'address'][ns1+'CI_Address']

        record['distributorphone'] = distributorContactPhone[ns1+'voice'][ns2+'CharacterString'].text
        record['distributorfax'] = distributorContactPhone[ns1+'facsimile'][ns2+'CharacterString'].text

        record['distributoraddress'] = distributorContactAddress[ns1+'deliveryPoint'][ns2+'CharacterString'].text + '\n' + \
            distributorContactAddress[ns1+'city'][ns2+'CharacterString'].text + '\n' + \
            distributorContactAddress[ns1+'postalCode'][ns2+'CharacterString'].text + '\n' + \
            distributorContactAddress[ns1+'country'][ns2+'CharacterString'].text
        record['distributoremail'] = distributorContactAddress[ns1+'electronicMailAddress'][ns2+'CharacterString'].text

        record['distributorrole'] = decrypt_role(distributorContact[ns1+'role'][ns1+'CI_RoleCode'].attrib['codeListValue'])

        record['costs'] = distributionDetails[ns1+'distributionOrderProcess'][ns1+'MD_StandardOrderProcess'][ns1+'fees'][ns2+'CharacterString'].text

        #Not worth doing look up
        record['maintenanceInfo'] = root[ns1+'metadataMaintenance'][ns1+'MD_MaintenanceInformation'][ns1+'maintenanceAndUpdateFrequency'][ns1+'MD_MaintenanceFrequencyCode'].attrib['codeListValue']

        return record


def imp_rec(record):
    printsafeurl = metautils.findLcGermanCharsAndReplace(record['url'].lower())
    print 'Processing ' + printsafeurl
    row = {}

    # Store the XML in the DB, but don't store it again in the JSON (which we will also store in the DB
    row['metadata_xml'] = record['xml']
    del record['xml']

    # Get license and files info from the HTML (stored during download of XML files)
    row['metadata'] = record

    row['filelist'] = record['filelist']
    row['url'] = record['url']
    row['licenseshort'] = record.get('license', '')

    row[u'Stadt'] = 'ulm'
    row[u'Dateibezeichnung'] = record['title']
    row[u'Beschreibung'] = record['abstract']
    row[u'url'] = record['url']
    row[u'Format'] = record['format'].upper()
    row[u'Format'] = [x.split()[0] for x in row[u'Format'].split(",")]

    row['spatial'] = True if record['geo'] else False

    row[u'Kosten'] = record.get('costs', None)
    row[u'Zeitlicher Bezug'] = record['datadate'][0:4]

    print record['keywords']
    cs = []
    for c in record['keywords']:
        c = metautils.govDataLongToODM(c, True)
        if c:
            cs.append(c[0])

    row['categories'] = list(set(cs))
    print row['categories']
    return row


class UlmReader(CatalogReader):
    def info(self):
        return {
            'name': 'ulm_harvester',
            'title': u'daten.ulm.de',
            'description': ''
        }

    def gather(self):
        data = gatherData()
        return data

    def fetch(self, d):
        rec = readXmlPart(d.get('metadata_xml', ''))
        rec[u'metadata_xml'] = d.get('metadata_xml', '')
        rec['filelist'] = d['filelist']
        rec['url'] = d['url']
        rec['license'] = d.get('license', '')

        return rec

    def import_data(self, rec):
        d = imp_rec(rec)
        d = metautils.gerToEngKeys(d)
        d['open'] = metautils.isopen(d.get('licenseshort', '').strip())

        d['json'] = ''
        d['publisher'] = ''
        d['originating_portal'] = 'daten.ulm.de'
        d['accepted'] = True
        d['source'] = 'd'
        d[u'metadata_xml'] = rec.get('metadata_xml', '')
        return d
