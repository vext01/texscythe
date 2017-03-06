#!/usr/bin/env python

from setuptools import setup
from setuptools.command.test import test as TestCommand
import sys

from texscythe import VERSION

# https://pytest.org/latest/goodpractises.html


class PyTest(TestCommand):

    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(name='texscythe',
      version=VERSION,
      description='TeX Live texmf subsetter',
      author='Edd Barrett',
      author_email='edd@theunixzoo.co.uk',
      license='ISC',
      keywords='LaTeX texmf subset',
      url='https://github.com/vext01/texscythe',
      install_requires=['sqlalchemy>=0.7'],  # although i'm not sure
      packages=['texscythe'],
      scripts=['texscyther'],
      classifiers=[
          "Development Status :: 4 - Beta",
          "Environment :: Console",
          "License :: OSI Approved",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 2.7",
          "Topic :: Text Processing :: Markup :: LaTeX"
      ],
      tests_require=['pytest'],
      cmdclass={'test': PyTest},
      )
