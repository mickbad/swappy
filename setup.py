#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages

# import lib
import swappy

# description
long_description = open('README.md').read()

# setup
setup(
    name='swappy',
    version=swappy.__version__,

#    packages=find_packages(),
    packages=["swappy"],
    scripts=[os.path.join('scripts', 'swappy-check'), ],

    author="MickBad",
    author_email="prog@mickbad.com",
    description="Fast check swap and interact",

    long_description=long_description,
    long_description_content_type='text/markdown',

    install_requires=["mblibs", "psutil"],

    # activate MANIFEST.in
    include_package_data=True,

    # github source
    url='https://github.com/mickbad/swappy',

    # https://pypi.python.org/pypi?%3Aaction=list_classifiers.
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: French",
        "Environment :: Console",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
        "Topic :: System",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Systems Administration",
    ],

    license="MIT",

    keywords="linux tools fasting swap",
)
