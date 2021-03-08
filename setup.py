#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from xml.dom.minidom import parse

from setuptools import setup

project_dir = os.path.dirname(os.path.abspath(__file__))
metadata = parse(os.path.join(project_dir, 'addon.xml'))
addon_version = metadata.firstChild.getAttribute('version')
addon_id = metadata.firstChild.getAttribute('id')

setup(
    name='AddonConnector',
    version=addon_version,
    url='https://github.com/CastagnaIT/script.module.addon.connector',
    author='Stefano Gottardo (CastagnaIT)',
    description='Kodi Addon connector',
    long_description='A Kodi module to provide the communication between add-ons and add-ons services',
    keywords='Kodi, plugin, addon, connector',
    license='LGPL-2.1-only',
    py_modules=['addonconnector', 'helper'],
    package_dir={'': 'lib'},
    zip_safe=False,
    platforms=['all'],
    python_requires='>=3.5'
)
