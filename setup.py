#!/usr/bin/env python

# Copyright (c) 2010 Diogo Becker
# Distributed under the MIT License
# See accompanying file LICENSE

from distutils.core import setup
from dude import __version__
setup(name='dude',
      version=__version__,
      description='dude - experimentation framework',
      author='Diogo Becker',
      packages=['dude', 'dude.summaries'],
      scripts=['scripts/dude'],
      license = 'MIT License'
      )

