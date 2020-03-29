#coding=utf-8
'''
Copyright
create on 2020.02.19
@author mahaidong

description:
'''
import Rhino
import rhinoscriptsyntax as rs
import caad.utility as util

__commandname__ = "DimLayer"
def RunCommand( is_interactive ):

    if not rs.IsLayer("Dim"): 
        util.initCaadLayer("Dim")
    oldLayer = rs.CurrentLayer("Dim")
    rs.Command("_DimAligned") 
    rs.CurrentLayer(oldLayer)



