#coding=utf-8
import unittest
from tests.testCase01_sun import TestCase01
# debug mode , 再次加载caad模块
import tests
reload( tests.testCase01_sun)

suite = unittest.TestLoader().loadTestsFromTestCase( TestCase01 )
unittest.TextTestRunner(verbosity=2).run(suite)
