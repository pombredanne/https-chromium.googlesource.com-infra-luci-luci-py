# Lint as: python3
"""TODO(jwata): DO NOT SUBMIT without one-line documentation for test.

TODO(jwata): DO NOT SUBMIT without a detailed description of test.
"""

from __future__ import absolute_import

import unittest2 as unittest

def main():
  loader = unittest.TestLoader()
  loader.discover('./', pattern='*_test.py')

if __name__ == '__main__':
  main()
