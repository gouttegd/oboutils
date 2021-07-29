# -*- coding: utf-8 -*-
# oboutils - OBO utilities
# Copyright (C) 2021 Damien Goutte-Gattat
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup
from fbcam.oboutils import __version__

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='fbcam.oboutils',
    version=__version__,
    description='Utilities for the OBO format',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Damien Goutte-Gattat',
    author_email='dpg44@cam.ac.uk',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3.8'
        ],

    install_requires=[
        'click',
        'pronto',
        'pyspellchecker',
        ],

    packages=[
        'fbcam',
        'fbcam.oboutils'
        ],

    entry_points={
        'console_scripts': [
            'oboutil = fbcam.oboutils.main:oboutil'
            ]
        }
    )
