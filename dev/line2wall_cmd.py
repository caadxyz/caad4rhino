#coding=utf-8
'''
Copyright
create on 2020.02.11
@author mahaidong
description:
'''
import Rhino
import Rhino.Geometry as geo

import rhinoscriptsyntax as rs
import scriptcontext as sc

from  caad.geometry.DoubleLine import DoubleLine
import caad.config as config
import caad.utility as util

def line2wall(layer):

    go = Rhino.Input.Custom.GetOption()
    go.AcceptNothing(True)
    go.SetCommandPrompt( "set wall width" )
    # set up the options
    widthOption = Rhino.Input.Custom.OptionDouble( config.DOUBLELINEWIDTH, 
            config.DOUBLELINEWIDTHLIMIT[0],config.DOUBLELINEWIDTHLIMIT[1] )
    go.AddOptionDouble("Width", widthOption)
    while True:
        get_rc = go.Get()
        if go.CommandResult()!=Rhino.Commands.Result.Success:
            print go.CommandResult()
            break 
        if get_rc==Rhino.Input.GetResult.Option:
            continue
        break
    
    if go.CommandResult() != Rhino.Commands.Result.Cancel:
        config.DOUBLELINEWIDTH = widthOption.CurrentValue

        if not rs.IsLayer("Axis"): 
            util.initCaadLayer("Axis")
        if not rs.IsLayer(layer): 
            util.initCaadLayer(layer)
            
        go = Rhino.Input.Custom.GetObject()
        go.SetCommandPrompt( "Select lines" )
        go.GeometryFilter = Rhino.DocObjects.ObjectType.Curve
        go.GetMultiple( 1, 0 )
        if go.CommandResult() != Rhino.Commands.Result.Success: 
            return go.CommandResult()
        
        oldLayer = rs.CurrentLayer(layer); 
        for lineCurveId in go.Objects():
            if rs.IsLine(lineCurveId):
                # make axis
                rs.ObjectLayer(lineCurveId, "Axis")

                # make wall
                point0 = rs.CurveStartPoint(lineCurveId) 
                point1 = rs.CurveEndPoint(lineCurveId) 
                doubleLine = DoubleLine.MakeDoubleLine(config.DOUBLELINEWIDTH, point0, point1);
                doubleLine.draw()
        rs.CurrentLayer(oldLayer); 

__commandname__ = "Line2Wall"
def RunCommand( is_interactive ):
    if not rs.IsLayer("Wall"): 
        util.initCaadLayer("Wall")
    line2wall("wall")
    sc.doc.Views.Redraw()


