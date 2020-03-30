#coding=utf-8
'''
Copyright
create on 2020.02.19
@author mahaidong

description:
'''
import System
import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc
import caad.config as config
import caad.utility as util
import caad.Dimension as Dim

__commandname__ = "Caad"
def RunCommand( is_interactive ):

    print ("caad4rhino 0.0.1")
    print (config.HOMEPAGE)

    go = Rhino.Input.Custom.GetOption()
    go.AcceptNothing(True)
    go.SetCommandPrompt( "caad4rhino setting" )

    scaleOption = Rhino.Input.Custom.OptionDouble( config.DRAWINGSCALE )
    scaleOpIndex, scaleOpValue = go.AddOptionDouble("DrawingScale", scaleOption)

    arrowValues = []
    for arrow in System.Enum.GetNames(Rhino.DocObjects.DimensionStyle.ArrowType):
        if (arrow != 'None') and (arrow != 'UserBlock'):
            arrowValues.append(arrow)
    arrowValue = config.DIMARROWHEAD
    arrowIndex = arrowValues.index(arrowValue)
    arrowOpList = go.AddOptionList("DimArrowHead", arrowValues, arrowIndex)

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
            if go.OptionIndex() == scaleOpIndex:
                if  scaleOption.CurrentValue  in config.DRAWINGSCALEList:
                    config.DRAWINGSCALE  = scaleOption.CurrentValue
                else:
                    print ( "The scale is not working." )
                    print ( "It should be in " + " ,".join([str(elem) for elem in config.DRAWINGSCALEList]) + "." )
                    scaleOpValue.CurrentValue = config.DRAWINGSCALE
            elif go.OptionIndex() == arrowOpList:
                arrowIndex = go.Option().CurrentListOptionIndex
                arrowValue = arrowValues[arrowIndex]
                config.DIMARROWHEAD = arrowValue
            continue
        break
     
    if go.CommandResult() != Rhino.Commands.Result.Cancel:
        Dim.ChangeDrawingScale(config.DRAWINGSCALE)
        print ("current drawwing scale = 1:"+str(int(config.DRAWINGSCALE)))
        Dim.ChangeCaadDimArrowHead( config.DIMARROWHEAD )
        print ( "current dimension arrowhead: "+ config.DIMARROWHEAD )
        isImportedAlias = aliasOption.CurrentValue
        if isImportedAlias : 
            config.importCaadAlias()
            print ("caad4rhino command aliases imported")

if __name__ == "__main__":
    RunCommand(True)


