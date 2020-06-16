#coding=utf-8
import unittest
import sys
sys.path.insert(0,'..')

import scriptcontext as sc
import caad
from datetime import datetime
import caad.physics.SunPath

reload(caad)
reload(caad.physics.SunPath)
from caad.physics.SunPath import SunPath,Sun

class TestCase01(unittest.TestCase):
    def testSunMethod(self):
        beijingPath = SunPath(39.9, 116.3,8)
        # localDatetime = datetime(2019,6,22,12)
        # sun =  beijingPath.calculateSunFromLocalDatetime( localDatetime )
        beijingPath.draw()


