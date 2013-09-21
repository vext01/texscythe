#!/usr/bin/env python

from setuptools import setup
import sys

setup(name              = 'texscythe',
    version           = '0.1',
    description       = 'TeX Live texmf subsetter',
    author            = 'Edd Barrett',
    author_email      = 'vext01@gmail.com',
    license           = 'ISC',
    keywords          = 'LaTeX texmf subset',
    long_description  = 'TeX Live texmf subsetter',
    url               = 'https://github.com/vext01/texscythe',
    install_requires  = ['sqlalchemy>=0.7'], # although i'm not sure
    packages          = ['texscythe'],
    scripts           = ['texscyther'],
    classifiers       = [
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: ISC License (ISCL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Topic :: Text Processing :: Markup :: LaTeX"
    ]
)
