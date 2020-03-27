#coding=utf-8
'''
Copyright
create on 2020.02.19
@author mahaidong

description:
'''

import math
import System

import Rhino
import Rhino.Geometry as geo
import scriptcontext as sc
import rhinoscriptsyntax as rs

from caad.geometry.DoubleLine import DoubleLine
import caad.utility as util
import caad.config as config


# tuple p0 p1 pi
def getTwoParallelLineSelectionRegion( p0, p1, pi, width ):
    lineDirect = rs.VectorUnitize( rs.VectorCreate( p1, p0 ) )
    lineCross = rs.VectorRotate(lineDirect, 90, (0,0,1))
    piUp = rs.VectorAdd(pi, rs.VectorScale(lineCross, width ) )
    piDown = rs.VectorAdd(pi, rs.VectorScale(rs.VectorReverse(lineCross), width ) )
    piDownRight = rs.VectorAdd( piDown, lineDirect*width) 
    return (geo.Point3d(piUp), geo.Point3d(piDown), geo.Point3d(piDownRight))

def findTwoParallelLines():

    gp = Rhino.Input.Custom.GetPoint()
    gp.SetCommandPrompt("find doubleline by clicking a point")
    gp.Get()
    if gp.CommandResult() != Rhino.Commands.Result.Success:
        print gp.CommandResult()
    pi = gp.Point()

    obj = gp.PointOnObject()
    if obj and isinstance(obj.Object(), Rhino.DocObjects.CurveObject):
        if isinstance(obj.Object().CurveGeometry, Rhino.Geometry.LineCurve):
            line = obj.Object().CurveGeometry.Line
            width = config.DOUBLELINEWIDTHLIMIT[1]
            region = getTwoParallelLineSelectionRegion(line.From, line.To, pi, width)
            filter = Rhino.DocObjects.ObjectType.Curve
            objects = sc.doc.Objects.FindByCrossingWindowRegion(sc.doc.Views.ActiveView.MainViewport, region, True, filter )
            anotherObj = None
            minDistance = config.DOUBLELINEWIDTHLIMIT[1]+1.0
            if objects:
                for rhobj in objects:
                    # rhobj.Select(True)
                    if isinstance(rhobj.CurveGeometry, Rhino.Geometry.LineCurve) and rhobj.Id != obj.Object().Id :
                        anotherLine = rhobj.CurveGeometry.Line
                        if rs.IsVectorParallelTo(line.Direction, anotherLine.Direction ) != 0 :
                            if anotherLine.DistanceTo(pi,False) < minDistance:
                                minDistance = anotherLine.DistanceTo(pi,False)
                                anotherObj = rhobj
            return (pi, obj.Object(), anotherObj ) 


# block 0=empty 1=window 2=door
def drawOpening (distance,length, block=0):
    if block == 1 and rs.IsBlock("window") == False :
        util.initWindowBlock()
    if block == 2 and rs.IsBlock("door") == False :
        util.initDoorBlock()
    if not rs.IsLayer("Axis"): 
        util.initCaadLayer("Axis")
   
    twoLines = findTwoParallelLines()
    if not twoLines : 
        return 0
    pi, linei, linej = twoLines 
    if not linej : 
        return 0
    pj = linej.CurveGeometry.Line.ClosestPoint(pi,False)

    oldLockMode = rs.LayerLocked("Axis", True)
    # side=0 start from startPoint , side=1 start from endPoint 
    if rs.Distance(linei.CurveGeometry.Line.From, pi) <= rs.Distance(pi, linei.CurveGeometry.Line.To):
        side = 0 
    else: 
        side = 1

    # direct:
    #  0 | 1
    # -------
    #  2 | 3
    vji = rs.VectorCreate( pj, pi ) 
    vi = linei.CurveGeometry.Line.Direction
    angle = rs.Angle((0,0,0), rs.VectorRotate(vji, -rs.Angle( (0,0,0), vi)[0], (0,0,1)) )
    if abs(angle[0]-90) < sc.doc.ModelAbsoluteTolerance :
        line0=linei
        line1=linej
        if side == 0:
            direct = 2
        else: 
            direct = 3
    elif abs(angle[0]+90) < sc.doc.ModelAbsoluteTolerance :
        line0=linej
        line1=linei
        if side == 0:
            direct = 0
        else: 
            direct = 1

    dl = DoubleLine(line0.CurveGeometry.Line,line1.CurveGeometry.Line)
    newLayer = rs.ObjectLayer(line0.Id)
    oldLayer = rs.CurrentLayer(newLayer)
    dl.drawOpening( distance,length, side, block, direct )
    rs.DeleteObject(line0.Id)
    rs.DeleteObject(line1.Id)
    rs.CurrentLayer(oldLayer)
    rs.LayerLocked("Axis", oldLockMode)

__commandname__ = "Opening"
def RunCommand( is_interactive ):
    # type
    go = Rhino.Input.Custom.GetOption()
    go.AcceptNothing(True)
    go.SetCommandPrompt( "set opening type" )
    blockValues = "empty", "window", "door"
    blockIndex = config.OPENINGTYPE
    go.AddOptionList("Type", blockValues, blockIndex)
    if go.Get() == Rhino.Input.GetResult.Option:
        blockIndex = go.Option().CurrentListOptionIndex
        config.OPENINGTYPE = blockIndex 
    
    # distance and length
    go = Rhino.Input.Custom.GetOption()
    go.AcceptNothing(True)
    go.SetCommandPrompt( "set distance and length" )
    distanceOption = Rhino.Input.Custom.OptionDouble( config.OPENINGDISTANCE )
    go.AddOptionDouble("Distance", distanceOption)
    if blockIndex == 0:
        lengthOption = Rhino.Input.Custom.OptionDouble( config.OPENINGLENGTH )
    elif blockIndex == 1:
        lengthOption = Rhino.Input.Custom.OptionDouble( config.WINDOWLENGTH )
    elif blockIndex == 2:
        lengthOption = Rhino.Input.Custom.OptionDouble( config.DOORLENGTH )
    go.AddOptionDouble("Length", lengthOption)
    while True:
        get_rc = go.Get()
        if go.CommandResult()!=Rhino.Commands.Result.Success:
            break
        if get_rc==Rhino.Input.GetResult.Option: continue
        break
     
    if go.CommandResult() != Rhino.Commands.Result.Cancel:
        config.OPENINGDISTANCE  = distanceOption.CurrentValue
        length = lengthOption.CurrentValue
        if blockIndex == 0 : config.OPENINGLENGTH = length
        elif blockIndex == 1 : config.WINDOWLENGTH = length
        elif blockIndex ==2 : config.DOORLENGTH = length
        drawOpening (config.OPENINGDISTANCE,length, blockIndex)

    sc.doc.Views.Redraw()


