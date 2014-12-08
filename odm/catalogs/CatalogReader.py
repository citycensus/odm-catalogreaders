class CatalogReader(object):
    """
    Basic "interface" to the ODM catalog readers.
    Resembles the structure of CKAN harvesters, for later CKAN imports.
    """

    def info(self):
        pass

    def gather(self):
        pass

    def fetch(self, data_dict):
        pass

    def import_data(self, data_dict):
        pass

    def read_data(self):
        """Get the data as a list of python dicts. """
        gs = self.gather()
        ds = []
        for g in gs:
            f = self.fetch(g)
            i = self.import_data(f)
            ds.append(i)
        return ds
