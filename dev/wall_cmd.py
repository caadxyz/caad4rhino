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
import caad.config as config

__commandname__ = "Wall"
def RunCommand( is_interactive ):
    go = Rhino.Input.Custom.GetOption()
    go.AcceptNothing(True)
    go.SetCommandPrompt( "set options" )
    # set up the options
    widthOption = Rhino.Input.Custom.OptionDouble( config.DOUBLELINEWIDTH, 
            config.DOUBLELINEWIDTHLIMIT[0],config.DOUBLELINEWIDTHLIMIT[1] )
    wallOption = Rhino.Input.Custom.OptionToggle(True, "Off", "On")
    go.AddOptionDouble("Width", widthOption)
    go.AddOptionToggle("Wall", wallOption)

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
        isWall = wallOption.CurrentValue
        if not rs.IsLayer("Wall"): 
            util.initCaadLayer("Wall")
        if isWall :
            DoubleLine.DrawDoubleLines("wall")
        else:
            DoubleLine.DrawDoubleLines(rs.CurrentLayer())


    sc.doc.Views.Redraw()


