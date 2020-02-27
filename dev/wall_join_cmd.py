#coding=utf-8
'''
Copyright
create on 2020.02.19
@author mahaidong

description:
'''

import System
import math

import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs

from caad.geometry.DoubleLine import DoubleLine
import caad.utility as util

def wallJoin(layer):
    if not rs.IsLayer("Wall"): 
        util.initCaadLayer("Wall")
    if not rs.IsLayer("Axis"): 
        util.initCaadLayer("Axis")

    haveLayer = True
    items = (layer, "Off", "On")
    result = rs.GetBoolean("current layer option", items, True )
    if result:
        haveLayer = result[0]
  
    oldLockMode = rs.LayerLocked("Axis", True)
    while True:
        go = Rhino.Input.Custom.GetObject()
        go.SetCommandPrompt( "Select 4 lines, each two parallel to anthor" )
        go.GeometryFilter = Rhino.DocObjects.ObjectType.Curve
        go.GetMultiple( 4, 4 )

        if go.CommandResult() != Rhino.Commands.Result.Success : 
            rs.LayerLocked("Axis", oldLockMode)
            return go.CommandResult()

        if go.ObjectCount!=4: return Rhino.Commands.Result.Failure
        crv= []
        for obj in go.Objects():
            crv.append(obj.Geometry().Line)

        rc, doubleLines = DoubleLine.GetIntersectedDoubleline(crv)
        if rc:
            doubleLine0 = doubleLines[0]
            doubleLine1 = doubleLines[1]
            if haveLayer:
                oldLayer = rs.CurrentLayer(layer)
            doubleLine0.drawIntersectionWithDoubleLine(doubleLine1)
            if haveLayer:
                rs.CurrentLayer(oldLayer); 
            rs.DeleteObjects(go.Objects())
        else:
            print "Error: no two doubleLines"



__commandname__ = "WallJoin"
def RunCommand( is_interactive ):
    wallJoin("wall")
