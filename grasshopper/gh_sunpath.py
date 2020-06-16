#coding=utf-8
################################################################################
# gh_sunpath.py
# Copyright (c) 2020.4 mahaidong
# Supported by ikuku.cn & caad.xyz 
# See License in the root of this repository for details.
################################################################################
import rhinoscriptsyntax as rs
import Rhino
from System.Drawing import Color
import ghpythonlib.treehelpers as th

import os
import sys
sys.path.append( os.path.dirname( ghenv.Component.OnPingDocument().FilePath ) )
from textGoo import TextGoo
from caad.physics.SunPath import SunPath,Sun


beijingPath = SunPath(39.9, 116.3,8)

cenPt = Rhino.Geometry.Point3d.Origin
northVector = Rhino.Geometry.Vector3d.YAxis
radius = 200.0
centerLine = False
# draw compass
compassLines, compassTextPts, texts = beijingPath.compassCurves( cenPt,northVector,radius,centerLine )
compassText = []
for i in range( len(compassTextPts) ):
    plane = Rhino.Geometry.Plane( compassTextPts[i],Rhino.Geometry.Vector3d(0,0,1))
    text3d = TextGoo( Rhino.Display.Text3d( texts[i], plane, 8.0 ))
    compassText.append(text3d)
monthlyCrvs, hourlyCrvs = beijingPath.yearlyPath(radius)
