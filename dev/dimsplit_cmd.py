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
import caad.utility as util
import caad.Dimension as Dim

__commandname__ = "DimSplit"
def RunCommand( is_interactive ):
    go = Rhino.Input.Custom.GetObject()
    go.SetCommandPrompt( "Select a LinearDimension" )
    go.GeometryFilter = Rhino.DocObjects.ObjectType.Annotation
    go.Get()

    if go.CommandResult() != Rhino.Commands.Result.Success : 
        return go.CommandResult()

    object_id = go.Objects()[0].ObjectId

    if not rs.IsLayer("Dim"): 
        util.initCaadLayer("Dim")
    oldLayer = rs.CurrentLayer("Dim")
    Dim.DimSplit(object_id)
    rs.CurrentLayer(oldLayer)

    sc.doc.Views.Redraw()


