from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='epel_to_ius',
      version=version,
      description="Sync packages from EPEL to IUS Community",
      long_description="""\
Sync packages from EPEL to RPMdev""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Jeffrey Ness',
      author_email='jeffrey.ness@rackspace.com',
      url='',
      license='GPLv2',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'simplejson',
        'configobj',
        'monkeyfarm.interface',
        'monkeyfarm.core',
        'monkeyfarm.client',
      ],
      entry_points= {
        'console_scripts': ['epel_to_ius = epel_to_ius.main:main']
         },
      )
