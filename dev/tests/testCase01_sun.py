#coding=utf-8
import unittest
import sys
sys.path.insert(0,'..')


import scriptcontext as sc
import caad
from datetime import datetime
from caad.physics.sunPath import SunPath
from caad.physics.sunPath import Sun
reload(caad)
reload(caad.physics.sunPath)
class TestCase01(unittest.TestCase):
    def testSunMethod(self):
        beijing = SunPath(39.9, 116.3,8)
        localDatetime = datetime(2019,6,22,12)
        position =  beijing.getSunPositionByLocaltime( localDatetime )
        sun = Sun(localDatetime,position['altitude'], position['azimuth'] )
