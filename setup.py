#!/usr/bin/env python

from distutils.core import setup
import sys

setup(name              = 'texscythe',
      version           = '0.1',
      description       = 'TeX Live texmf subsetter',
      maintainer        = 'Edd Barrett',
      maintainer_email  = 'vext01@gmail.com',
      license           = 'ISC',
      long_description  = 'TeX Live texmf subsetter',
      url               = 'https://github.com/vext01/texscythe',
      packages          = ['texscythe'],
      scripts           = ['texscythe.py'],
      )
