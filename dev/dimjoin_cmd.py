#coding=utf-8
'''
Copyright
create on 2020.02.19
@author mahaidong

description:
'''
import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc
from caad.geometry.DoubleLine import DoubleLine
import caad.utility as util
import caad.Dimension as Dim

__commandname__ = "DimJoin"
def RunCommand( is_interactive ):
    go = Rhino.Input.Custom.GetObject()
    go.SetCommandPrompt( "Select 2 LinearDimension" )
    go.GeometryFilter = Rhino.DocObjects.ObjectType.Annotation
    go.GetMultiple( 2, 2 )

    if go.CommandResult() != Rhino.Commands.Result.Success : 
        return go.CommandResult()

    object_id0 = go.Objects()[0].ObjectId
    object_id1 = go.Objects()[1].ObjectId 

    if not rs.IsLayer("Dim"): 
        util.initCaadLayer("Dim")
    oldLayer = rs.CurrentLayer("Dim")
    Dim.LinearDimJoin( object_id0, object_id1 )
    rs.CurrentLayer(oldLayer)

    sc.doc.Views.Redraw()


