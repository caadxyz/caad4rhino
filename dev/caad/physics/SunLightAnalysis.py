#coding=utf-8
'''
Copyright
create on 2020.02.28
@author mahaidong

description:
'''
import math
import Rhino
import rhinoscriptsyntax as rs

class SunShadow:
    def __init__(self, theMeshs ):
        self.meshs = theMeshs

    def getShadow(self, thePlane, theSunDirect):
        pass