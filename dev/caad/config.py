#coding=utf-8
'''
Copyright
create on 2019.09.05
@author mahaidong
'''

SHOWHOMEPAGE = False
HOMEPAGE = "https://github.com/caadxyz/caad4rhino"

DOUBLELINEWIDTH = 100.0 
DOUBLELINEWIDTHLIMIT = (49.5, 400.5)
# wall offset type 0=middle 1=right 2=left
DOUBLELINEOFFSETSIDETYPE = 0

# openingtype 0=empty 1=window 2=door
OPENINGTYPE     = 2
OPENINGDISTANCE = 100
OPENINGLENGTH   = 1000
WINDOWLENGTH    = 1200
DOORLENGTH      = 900

# DRAWINGSCALE  1:100
DRAWINGSCALE = 0.01
A5FRAMEWIDTH = 210.0
A5FRAMEHEIGHT = 148.5
FRAMESIZE = "A3"
FRAMELEFTMARGIN = 20.0
FRAMERIGHTMARGIN = 10.0

IMPORTCOMMANDALIAS = False
import rhinoscriptsyntax as rs
def importCaadAlias():
    #wall
    rs.AddAlias("WW",  "! wall _Enter")
    rs.AddAlias("DL",  "! wall a _Enter")
    rs.AddAlias("L2W", "! line2wall w _Enter")
    rs.AddAlias("WJ",  "! wall_join _Enter")
    rs.AddAlias("DJ",  "! wall_join w _Enter")

    #opening
    rs.AddAlias("OP",   "! opening")
    rs.AddAlias("WIN",  "! opening t w")
    rs.AddAlias("DOOR",  "! opening t d")

    #dim
    rs.AddAlias("DIMJ",  "! dimjoin")
    rs.AddAlias("DIMS",  "! dimsplit")
    rs.AddAlias("DIML",  "! dimlayer")
    rs.AddAlias("FR",   "! frame")


