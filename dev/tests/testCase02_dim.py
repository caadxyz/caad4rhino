#coding=utf-8
import unittest
import sys
sys.path.insert(0,'..')
import scriptcontext as sc
import caad.Dimension as Dim

import caad
reload(caad.Dimension)



class TestCase02(unittest.TestCase):

    def testChangeDrawingScale(self):
        self.assertEqual( Dim.ChangeDrawingScale(0.01), None)

    # 查看是否输出正确的图纸信息
    def testGetFrameSize(self):
        self.assertEqual( Dim.GetFrameSize("A3"), (420,297))
