#coding=utf-8
import sys
import math
import System
from System.Drawing import Color
import urllib2
import os
import platform
import pydoc
import time
from datetime import datetime, timedelta
import calendar

import Rhino
import Rhino.Geometry as geo

import scriptcontext as sc
import rhinoscriptsyntax as rs


from caad.geometry.DoubleLine import DoubleLine
import caad.Dimension as Dim
import caad.utility as util
import caad.config as config
from caad.physics.SunPosition import SunPosition

# debug mode , 再次加载caad模块
# release mode 要删除 reload
import caad
reload(caad.geometry.DoubleLine)
reload(caad.physics.SunPosition)
reload(caad.utility)
reload(caad.config)
reload(caad.Dimension)

def ObjectDisplayMode():
    filter = Rhino.DocObjects.ObjectType.Brep | Rhino.DocObjects.ObjectType.Mesh
    rc, objref = Rhino.Input.RhinoGet.GetOneObject("Select mesh or surface", True, filter)
    if rc != Rhino.Commands.Result.Success: return rc;
    viewportId = sc.doc.Views.ActiveView.ActiveViewportID

    attr = objref.Object().Attributes
    if attr.HasDisplayModeOverride(viewportId):
        print "Removing display mode override from object"
        attr.RemoveDisplayModeOverride(viewportId)
    else:
        modes = Rhino.Display.DisplayModeDescription.GetDisplayModes()
        mode = None
        if len(modes) == 1:
            mode = modes[0]
        else:
            go = Rhino.Input.Custom.GetOption()
            go.SetCommandPrompt("Select display mode")
            str_modes = []
            for m in modes:
                s = m.EnglishName.replace(" ","").replace("-","")
                str_modes.append(s)
            go.AddOptionList("DisplayMode", str_modes, 0)
            if go.Get()==Rhino.Input.GetResult.Option:
                mode = modes[go.Option().CurrentListOptionIndex]
        if not mode: return Rhino.Commands.Result.Cancel
        attr.SetDisplayModeOverride(mode, viewportId)
    sc.doc.Objects.ModifyAttributes(objref, attr, False)
    sc.doc.Views.Redraw()

def version():
    print sys.version_info
    print sys.version
    print sys.path




def addOneMonth(sourcedate):
    year = sourcedate.year + sourcedate.month // 12
    month = sourcedate.month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year,month)[1])
    return datetime(year, month, day, sourcedate.hour, sourcedate.minute)

def draw2dtext():
  gp = GetDrawStringPoint()
  gp.SetCommandPrompt("Point")
  gp.Get()
  return gp.CommandResult()

class GetDrawStringPoint( Rhino.Input.Custom.GetPoint):
  def OnDynamicDraw(self, e):
    xform = e.Viewport.GetTransform(
      Rhino.DocObjects.CoordinateSystem.World, Rhino.DocObjects.CoordinateSystem.Screen)    
    current_point = e.CurrentPoint
    current_point.Transform(xform)
    screen_point = Rhino.Geometry.Point2d(current_point.X, current_point.Y)
    msg = "screen {0}, {1}".format(screen_point.X, screen_point.Y)
    e.Display.Draw2dText(msg, Color.Blue, screen_point, False)
    circle = Rhino.Geometry.Circle( e.CurrentPoint, 10)
    e.Display.DrawCircle(circle, Color.Blue)

if __name__=="__main__":
    """
    url = "https://jsonplaceholder.typicode.com/posts/"
    lines = util.getContentFromUrl(url)
    util.openUrl(url)

    for line in lines:
        print line
    obj = rs.AddLine((-10,-10,0),(10,10,0))
    for i in range(1000):
        Rhino.RhinoApp.Wait() 
        rs.RotateObject(obj, (0,0,0), 5.0, None, False)
    rs.DeleteObject(obj)
    """
    draw2dtext()

    # if position['altitude'] > 0:
    beijing = SunPath(39.9, 116.3,8)
    for i in range (24):
        localDatetime = datetime(2019,1,1,i)
        for j in range(12):
            day = localDatetime
            for k in range(3):
                position =  beijing.getSunPositionByLocaltime( day )
                sunVect = beijing.getSunVectorFromOrigin(position['altitude'], position['azimuth']) 
                sunVect.Reverse()
                util.drawVector( Rhino.Geometry.Point3d( -20*sunVect ), 5*sunVect, str(i) )
                day += timedelta(days=10) 
            localDatetime = addOneMonth(localDatetime) 
    sc.doc.Views.Redraw()


