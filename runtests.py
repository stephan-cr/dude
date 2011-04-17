#!/usr/bin/python

import os
import sys
import unittest

from test import *

sys.path.insert(0, os.path.dirname(__file__))

if __name__ == '__main__':
    unittest.main()
    print os.path.dirname(__file__)
