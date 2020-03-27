#coding=utf-8
'''
Copyright
create on 2020.03.28
@author mahaidong

description:
'''
import Rhino
import rhinoscriptsyntax as rs
import caad.utility as util
import caad.Dimension as Dim
import caad.config as config
import System.Drawing

def GetPointDynamicDrawFunc( sender, args ):
  (width, height) = Dim.GetFrameSize( config.FRAMESIZE )
  points= []
  points.append( args.CurrentPoint )
  points.append( args.CurrentPoint + Rhino.Geometry.Point3d( width/config.DRAWINGSCALE,0,0) )
  points.append( args.CurrentPoint + Rhino.Geometry.Point3d( width/config.DRAWINGSCALE,height/config.DRAWINGSCALE,0) )
  points.append( args.CurrentPoint + Rhino.Geometry.Point3d( 0,height/config.DRAWINGSCALE,0) )
  points.append( args.CurrentPoint )
  args.Display.DrawPolyline( points, System.Drawing.Color.Cyan )

__commandname__ = "Frame"
def RunCommand( is_interactive ):

    gp = Rhino.Input.Custom.GetPoint()
    gp.SetCommandPrompt( "get a point as a locaiton and setting frame size, scale 1:"+str( int(1/config.DRAWINGSCALE)) )
    sizeValues = "A5", "A4", "A3","A2","A1","A0"
    sizeValue = config.FRAMESIZE
    sizeIndex = sizeValues.index(sizeValue)
    opList = gp.AddOptionList("FrameSize", sizeValues, sizeIndex)

    gp.DynamicDraw += GetPointDynamicDrawFunc
    while True:
        get_rc = gp.Get()
        if gp.CommandResult()!=Rhino.Commands.Result.Success:
            return gp.CommandResult()

        if get_rc==Rhino.Input.GetResult.Point:
            point = gp.Point()
            if not rs.IsLayer("Dim"): 
                util.initCaadLayer("Dim")
            oldLayer = rs.CurrentLayer("Dim")
            Dim.DrawFrameBySize( sizeValue, point ,config.FRAMERIGHTMARGIN, config.FRAMELEFTMARGIN )
            rs.CurrentLayer(oldLayer)

        elif get_rc==Rhino.Input.GetResult.Option:
            if gp.OptionIndex() == opList:
                sizeIndex = gp.Option().CurrentListOptionIndex
                sizeValue = sizeValues[sizeIndex]
                config.FRAMESIZE = sizeValue
            continue
        break
    return Rhino.Commands.Result.Success


