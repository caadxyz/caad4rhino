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
import caad.config as config
import caad.utility as util

__commandname__ = "Caad"
def RunCommand( is_interactive ):

    print ("caad4rhino 0.0.1")
    print (config.HOMEPAGE)

    go = Rhino.Input.Custom.GetOption()
    go.AcceptNothing(True)
    go.SetCommandPrompt( "caad4rhino setting" )

    scaleOption = Rhino.Input.Custom.OptionDouble( config.DRAWINGSCALE )
    go.AddOptionDouble("DrawingScale", scaleOption)

    aliasOption = Rhino.Input.Custom.OptionToggle( config.IMPORTCOMMANDALIAS, "Off", "On")
    go.AddOptionToggle("ImportCommandAlias", aliasOption)

    homePageOption = Rhino.Input.Custom.OptionToggle( config.SHOWHOMEPAGE, "Off", "On")
    go.AddOptionToggle("GotoHelpPage", homePageOption)

    while True:
        get_rc = go.Get()
        if go.CommandResult()!=Rhino.Commands.Result.Success:
            break
        if get_rc==Rhino.Input.GetResult.Option: 
            isHomePage = homePageOption.CurrentValue
            if isHomePage : util.openUrl( config.HOMEPAGE  )
            continue

        break
     
    if go.CommandResult() != Rhino.Commands.Result.Cancel:
        config.DRAWINGSCALE  = scaleOption.CurrentValue
        print (config.DRAWINGSCALE)
        isImportedAlias = aliasOption.CurrentValue
        if isImportedAlias : config.importCaadAlias()

if __name__ == "__main__":
    RunCommand(True)


