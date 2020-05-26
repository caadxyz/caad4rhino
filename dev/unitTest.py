#coding=utf-8
import unittest
from tests.testCase01_sun import TestCase01
import tests

# debug mode
reload( tests.testCase01_sun)
suite1 = unittest.TestLoader().loadTestsFromTestCase( TestCase01 )
unittest.TextTestRunner(verbosity=2).run(suite1)

