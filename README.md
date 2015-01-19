odm-catalogreaders
==================

Readers for various open data catalogs

We try to read anything. We have API/structured data readers, html scrapers and mixtures of both.

### APIs
APIs vary greatly in their structure and data format. The most common format is JSON. This makes the data very straightforward to write out to a tabular format, even though some nested data has to be ‘flattened’ first. A less common format is XML, specifically ISO 19139. ISO 19139 is "an XML Schema defining how metadata conforming to ISO 19115 should be stored in XML format". ISO 19115 is "a content standard that defines what information should exist in a metadata document"(1). The standard comes from the Open Geospatial Consortium(2) and can be referred to as OGC-CSW (Open Geospatial Consortium Catalog Service for the Web(3)). A summary of which cities maintain which type of API is being maintained at http://okfde.github.io/catalogmetadata/. For a number of cases, there is no simple ‘endpoint’ to grab the entire metadata from. 

1. Both quotations from: http://support.esri.com/en/knowledgebase/techarticles/detail/25895
2. http://www.opengeospatial.org/
3. http://en.wikipedia.org/wiki/Catalog_Service_for_the_Web
