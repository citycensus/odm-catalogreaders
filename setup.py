from setuptools import setup, find_packages

setup(
    name='odm-catalogreaders',
    description="Extraction of metadata from various data catalogs",
    license='mit',
    packages=['odm', 'odm.catalogs', 'odm.catalogs.portals', 'odm.catalogs.utils'],
    install_requires=[
        'lxml',
    ],
)
