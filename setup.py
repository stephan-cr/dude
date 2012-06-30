#!/usr/bin/env python

# Copyright (c) 2010,2012 Diogo Becker and Stephan Creutz
# Distributed under the MIT License
# See accompanying file LICENSE

import ast
import os
import sys

extra = {}
try:
    from setuptools import setup
    # convert source to Python 3 if setup is called with Python interpreter
    # version 3
    if sys.version_info >= (3,):
        extra['use_2to3'] = True
except ImportError:
    # fall back to standard distutils
    from distutils.core import setup

# we cannot directly import dude, because that would fail when, e.g. we want to
# translate the source code to Python 3
class VersionPattern(ast.NodeVisitor):
    '''
    Extract value of '__version__' variable, which must be initialized directly
    by a string literal. The AST in such a case may look as follows:

    Module(body=[Assign(targets=[Name(id='__version__', ctx=Store())],
    value=Str(s='1.2.3'))])
    '''

    def __init__(self):
        ast.NodeVisitor.__init__(self)
        self.__version = None
        self.__is_version_id = False

    def visit_Assign(self, node):
        for target in node.targets:
            self.visit(target)
            if self.__is_version_id:
                self.visit(node.value)
                return

    def visit_Module(self, node):
        for statement in node.body:
            self.visit(statement)
            if self.__is_version_id:
                return

    def visit_Name(self, node):
        self.__is_version_id = node.id == '__version__'

    def visit_Str(self, node):
        self.__version = node.s

    def generic_visit(self, node):
        pass # don't recurse by default

    def version(self):
        return self.__version

dude_version = None
with open(os.path.join('dude', '__init__.py'), 'r') as version_file:
    pattern = VersionPattern()
    pattern.visit(ast.parse(version_file.read()))
    dude_version = pattern.version()

dude_url = 'http://bitbucket.org/db7/dude'

if dude_version is None:
    sys.stderr.write('cannot determine dude version from source code\n' +
                     'please report that issue here: ' + dude_url)
    sys.exit(1)

setup(name='dude',
      version=dude_version,
      description='dude - experimentation framework',
      author='Diogo Becker',
      packages=['dude'],
      scripts=['scripts/dude'],
      license='MIT License',
      url=dude_url,
      **extra
      )
