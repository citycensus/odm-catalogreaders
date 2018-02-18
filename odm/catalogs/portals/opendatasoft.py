import requests
import json

from odm.catalogs.utils import metautils
from odm.catalogs.CatalogReader import CatalogReader

cities = {
        "potsdam": {
            "url": "https://opendata.potsdam.de",
            "portalname": "opendata.potsdam.de"
            }
        }
def has_next(entry):
    if entry["links"]:
        links = entry["links"]
        refs = [link["ref"] for link in links]
        if "next" in refs:
            return True
    return False

def create_dataset_api_url(base_url):
    return "{}/api/v2/catalog/datasets".format(base_url)

def get_data(url):
    r = requests.get(url)
    return json.loads(r.text)

def get_datasets(data):
    return data["datasets"]

def transform_files(link):
    if link["rel"] != "self":
        return { "format": link["rel"], "url": link["href"]}
    return None

def get_files(url):
    data = get_data(url)
    return filter(None, [transform_files(f) for f in data["links"]])

def gatherCity(city, url, apiKey= ""):
    data = get_data(create_dataset_api_url(url))
    datasets = get_datasets(data)
    while(has_next(data)):
        data = get_data(metautils.next_entry(data))
        datasets + get_datasets(data)
    datasets_with_files = []
    for dataset in datasets:
        single_dataset = dataset["dataset"]
        single_dataset["files"] = get_files(metautils.dataset_exports(dataset))
        datasets_with_files.append(single_dataset)
    return datasets_with_files

class ODSReader(CatalogReader):
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
