#coding=utf-8
'''
Copyright
create on 2020.02.13
@author mahaidong
description:
'''
import Rhino
import Rhino.Geometry as geo
import rhinoscriptsyntax as rs
import scriptcontext as sc
import caad.config as config
import caad.utility as util


def GetFrameSize(size):
    # get the width and height by the size of layout
    width = config.A5FRAMEWIDTH
    height = config.A5FRAMEHEIGHT
    if len(size) !=2 :
        return None
    elif size[0] != 'A':
        return None
    else:
        size = int(size[1])
        i = 5
        while i != size:
            i -=1
            oldWidth = width
            width = height*2
            height = oldWidth
    return (width, height)

def DrawFrameBySize(size,location, rightMargin, leftMargin ):
    width, height = GetFrameSize(size)
    # draw layout frame
    width = width/config.DRAWINGSCALE
    height = height/config.DRAWINGSCALE
    rightMargin = rightMargin/config.DRAWINGSCALE
    leftMargin = leftMargin/config.DRAWINGSCALE

    p0 = rs.PointAdd((0,0,0),location)
    p1 = rs.PointAdd((width,0,0),location)
    p2 = rs.PointAdd((width,height,0),location)
    p3 = rs.PointAdd((0,height,0),location)
    outPolyline = rs.AddPolyline([p0,p1,p2,p3,p0])

    p0 = rs.PointAdd((leftMargin,rightMargin,0),location)
    p1 = rs.PointAdd((width-rightMargin,rightMargin,0),location)
    p2 = rs.PointAdd((width-rightMargin,height-rightMargin,0),location)
    p3 = rs.PointAdd((leftMargin,height-rightMargin,0),location)
    inPolyline = rs.AddPolyline([p0,p1,p2,p3,p0])
    return ( outPolyline, inPolyline)


def ChangeDrawingScale():
    pass

def DimSplit(object_id):
    annotation_object = sc.doc.Objects.Find(object_id )
    dim = annotation_object.Geometry
    isAligned = False
    if isinstance(dim, Rhino.Geometry.LinearDimension):
        # isAligned = dim.Aligned
        _, extensionLine1End, extensionLine2End, _, _, dimlinepoint, _ = dim.Get3dPoints() 
        plane = dim.Plane
        splitPoint = rs.GetPoint("Pick spliting point")
        if splitPoint:
            rs.AddLinearDimension(plane,  extensionLine1End, splitPoint, dimlinepoint )
            rs.AddLinearDimension(plane,  splitPoint, extensionLine2End, dimlinepoint )
            rs.DeleteObject(object_id)
        else: 
            print ("error: not point")
    else:
        print ("error: not dimension")


def LinearDimJoin(object_id0, object_id1):
    annotation_object0 = sc.doc.Objects.Find( object_id0 )
    dim0 = annotation_object0.Geometry
    annotation_object1 = sc.doc.Objects.Find( object_id1 )
    dim1 = annotation_object1.Geometry
    if isinstance(dim0, Rhino.Geometry.LinearDimension) and isinstance(dim1, Rhino.Geometry.LinearDimension):
        _, extensionLine01End, extensionLine02End, arrowhead01End, arrowhead02End, dimlinepoint0, _ = dim0.Get3dPoints() 
        _, extensionLine11End, extensionLine12End, arrowhead11End, arrowhead12End, dimlinepoint1, _ = dim1.Get3dPoints() 

        line0 = geo.Line(arrowhead01End, arrowhead02End)
        direct0=rs.VectorUnitize(line0.Direction)
        line1 = geo.Line(arrowhead11End, arrowhead12End)
        direct1=rs.VectorUnitize(line1.Direction)
        if rs.IsVectorParallelTo(direct0, direct1 ) != 0 :
            param0 = line0.ClosestParameter(line1.From)
            param1 = line0.ClosestParameter(line1.To)
            paramDictionary = {
                    0.0 : extensionLine01End, 
                    1.0 : extensionLine02End, 
                    param0 : extensionLine11End, 
                    param1 : extensionLine12End
                    }
            extensionLineList = []
            for key in sorted(paramDictionary.keys()):
                extensionLineList.append(paramDictionary[key])

            distance0 = line0.DistanceTo(extensionLineList[0],False)
            distance1 = line1.DistanceTo(extensionLineList[0],False)
            if distance0 > distance1: 
                rs.AddLinearDimension(dim0.Plane, extensionLineList[0], extensionLineList[len(extensionLineList)-1], dimlinepoint0 )
            else:
                rs.AddLinearDimension(dim1.Plane, extensionLineList[0], extensionLineList[len(extensionLineList)-1], dimlinepoint1 )

            rs.DeleteObject(object_id0)
            rs.DeleteObject(object_id1)

