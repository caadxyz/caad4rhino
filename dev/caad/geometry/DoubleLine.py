#coding=utf-8
'''
Copyright
create on 2018.12.27
@author mahaidong

description:
'''
import math

import Rhino
import Rhino.Geometry as geo

import rhinoscriptsyntax as rs
import scriptcontext as sc

import caad.config  as config

class DoubleLine:
    def __init__(self, line0, line1):
        # initialized by two Rhino.Geometry.Line
        self.isDoubleLine = True
        self.direction = None
        self.line0 = None
        self.line1 = None
        self.width = 0

        direction0=rs.VectorUnitize(line0.Direction)
        self.direction = direction0
        # not parallel
        if rs.IsVectorParallelTo(direction0, rs.VectorUnitize(line1.Direction) ) == 0 :
            self.isDoubleLine = False
        else :
            # parallel but in oppersite direction
            if rs.IsVectorParallelTo(direction0, rs.VectorUnitize(line1.Direction) ) == -1 :
                line1.Flip()

            # find the closest point to line1's start point
            line0ClosePoint=line0.ClosestPoint(line1.From, False)
            vector = rs.VectorCreate(line1.From, line0ClosePoint )
            distance = rs.Distance(line1.From, line0ClosePoint)

            if distance >= config.DOUBLELINEWIDTHLIMIT[0] and distance <= config.DOUBLELINEWIDTHLIMIT[1] :
                self.width = distance
                angle =  rs.Angle((0,0,0), rs.VectorRotate(vector, -rs.Angle(line0.From, line0.To)[0], (0,0,1)) )
                if abs(angle[0]-90) < sc.doc.ModelAbsoluteTolerance :
                    self.line0=line1
                    self.line1=line0
                elif abs(angle[0]+90) < sc.doc.ModelAbsoluteTolerance :
                    self.line0=line0
                    self.line1=line1
   
    @classmethod  
    def MakeDoubleLine(cls,width, p0, p1, type = 0):  
        """Make a doubleLine by width and two points 
        Parameters:
            width: Type real, the width
            p0,p1: Type Point3d
            type 0=middle, 1=right, 2=left
        returns: DoubleLine
        """

        line = geo.Line( p0, p1)
        curveLine = geo.LineCurve(line)

        plane = rs.PlaneFromNormal( p0, (0,0,1),p1-p0 )
        halfWidth = width/2.0
        if type == 0:
            offLine0 = curveLine.Offset( plane, halfWidth,
                                        sc.doc.ModelAbsoluteTolerance, geo.CurveOffsetCornerStyle.None )
            offLine1 = curveLine.Offset( plane, -halfWidth,
                                        sc.doc.ModelAbsoluteTolerance, geo.CurveOffsetCornerStyle.None )
            return  cls(offLine0[0].Line, offLine1[0].Line)
        elif type == 1:
            offLine0 = curveLine.Offset( plane, width,
                                        sc.doc.ModelAbsoluteTolerance, geo.CurveOffsetCornerStyle.None )
            return  cls(offLine0[0].Line, line )
        elif type == 2:
            offLine1 = curveLine.Offset( plane, -width,
                                        sc.doc.ModelAbsoluteTolerance, geo.CurveOffsetCornerStyle.None )
            return  cls( line, offLine1[0].Line )

    def __str__(self):
        return "isDoubleLine: %s\n direction: %s \nwidth: %d\nline0: %s \nline1: %s\
        " %(self.isDoubleLine, self.direction, self.width, self.line0, self.line1)

    def flip(self):
        # flip this doubleLine's direction
        self.line0.Flip()
        self.line1.Flip()
        self.direction.Reverse()

    def drawOpening(self, distance,length, side=0, block=0, direct=0):
        """
        side=0 start from startPoint , side=1 start from endPoint 
        direct:
          0 | 1
         -------
          2 | 3
        block 0=empty 1=window 2=door
        """

        localDirect = direct
        if side == 1:
            self.flip()
            if direct == 0 : localDirect = 3
            if direct == 1 : localDirect = 2
            if direct == 2 : localDirect = 1
            if direct == 3 : localDirect = 0

        startParameter = self.line1.ClosestParameter( self.line0.From )
        startPoint = self.line1.ClosestPoint(self.line0.From, False)
        if startParameter >=0 :
            distance00 = distance
            distance10 = distance + startPoint.DistanceTo(self.line1.From) 
        else: 
            distance00 = distance + startPoint.DistanceTo(self.line1.From) 
            distance10 = distance 
        distance01 = distance00 + length
        distance11 = distance10 + length

        """
            p10    p11
        ------     ------>line1
             |     |
        ------     ------>line0
            p00    p01
        """
        point00 = self.line0.PointAtLength(distance00)
        point10 = self.line1.PointAtLength(distance10)
        point01 = self.line0.PointAtLength(distance01)
        point11 = self.line1.PointAtLength(distance11)
        parameter00 = self.line0.ClosestParameter(point00)
        parameter10 = self.line1.ClosestParameter(point10)
        parameter01 = self.line0.ClosestParameter(point01)
        parameter11 = self.line1.ClosestParameter(point11)
        if parameter00 <0 or parameter00>1 or parameter10 <0 or parameter10>1 or parameter01 <0 or parameter01>1 or parameter11 <0 or parameter11>1 : 
            print("error: wrong opening length")
            return 0
        # drawing        
        sc.doc.Objects.AddLine(point00, point10)
        sc.doc.Objects.AddLine(point01, point11)

        sc.doc.Objects.AddLine( self.line0.From, self.line0.PointAt(parameter00) )
        sc.doc.Objects.AddLine( self.line0.PointAt(parameter01), self.line0.To )
        sc.doc.Objects.AddLine( self.line1.From, self.line1.PointAt(parameter10) )
        sc.doc.Objects.AddLine( self.line1.PointAt(parameter11), self.line1.To )

        # empty
        if block==0:
            pass
        # window
        elif block==1:
            scaleX=point00.DistanceTo(point01)/1000
            scaleY=point00.DistanceTo(point10)/100
            origin = (point00+point10+point01+point11)/4
            block_id = rs.InsertBlock( "window", origin, (scaleX,scaleY,1), 0, (0,0,1) )
            angle_degrees=rs.Angle(point00, point01)[0]
            rs.RotateObject(block_id, origin, angle_degrees)
        # door
        elif block==2:
            scaleX=point00.DistanceTo(point01)/1000
            scaleY=scaleX
            origin = (point00+point10+point01+point11)/4
            block_id = rs.InsertBlock( "door", origin, (scaleX,scaleY,1), 0, (0,0,1) )
            angle_degrees=rs.Angle(point00, point01)[0]
            rs.RotateObject(block_id, origin, angle_degrees)
            if localDirect == 0:
                pass
            elif localDirect == 1:
                rs.MirrorObject(block_id, (point10+point11)/2, (point00+point01)/2 )
            elif localDirect == 2:
                rs.MirrorObject(block_id, (point00+point10)/2, (point01+point11)/2 )
            elif localDirect == 3:
                rs.MirrorObject(block_id, (point10+point11)/2, (point00+point01)/2 )
                rs.MirrorObject(block_id, (point00+point10)/2, (point01+point11)/2 )


    ##########IntersectionWithDoubleLine start####################
    @classmethod
    def GetIntersectedDoubleline(cls,lineList):
        """
        Parameters:
            lineList: Type list of Rhino.Geometry.Line
        Returns: 
           boolean
           two intersected DoubleLine
        """

        doubleLineList=[]
        if len(lineList) ==4:
            for i in range(0,4):
                if len(doubleLineList) < 2:
                    for j in range(i+1,4):
                       if rs.IsVectorParallelTo(lineList[i].Direction, lineList[j].Direction ) != 0 :
                            myDoubleLine = cls(lineList[i],lineList[j])
                            doubleLineList.append(myDoubleLine)
                            break
                else:
                    break
        if len(doubleLineList) == 2:
            if rs.IsVectorParallelTo(doubleLineList[0].direction, doubleLineList[1].direction ) == 0 :
                if doubleLineList[0].width !=0 and doubleLineList[1].width !=0:
                    return (True,doubleLineList)
        return (False, None)


    def drawIntersectionWithDoubleLine(self, doubleLine):
        """draw two doubleLines:  selfDoubleLine and antherDoubleLine
        a=selfDoubleLine Type: System.Double
        Parameter on self.line0 that is closest to doubeLine.line0. 
        ab > 1 : means outside of self.line0.To
        ab < 0 : means outside of self.line0.From
        0 <=ab<= 1 : means inside of self.line0

        b=anotherDoubleLine Type: System.Double
        Parameter on doubleLine.line0 that is closest to self.line0. 
        ba > 1 : means outside of doubleLine.line0.To
        ba < 0 : means outside of doubleLine.line0.From
        0<= ba <= 1 : means inside of doubleLine.line0

        angle Type: System.Double
        counterclockwise angle between self and another
        """
        #get intersection infomation between two doubleLines
        rc, a0b0, b0a0 = geo.Intersect.Intersection.LineLine(self.line0, doubleLine.line0)
        if not rc:
            print "Parallel doubleLine found."
            return (False, None, None)
        rc, a0b1, b1a0 = geo.Intersect.Intersection.LineLine(self.line0, doubleLine.line1)
        rc, a1b0, b0a1 = geo.Intersect.Intersection.LineLine(self.line1, doubleLine.line0)
        rc, a1b1, b1a1 = geo.Intersect.Intersection.LineLine(self.line1, doubleLine.line1)

        # self.direction, doubleLine.direction
        angle =  rs.Angle((0,0,0), rs.VectorRotate(doubleLine.direction, -rs.Angle((0,0,0), self.direction)[0], (0,0,1)) )
        selfRawParameter    = ((a0b0, a0b1, a1b0, a1b1, b0a0, b1a0, b0a1, b1a1),  -angle[0])
        anotherRawParameter = ((b0a0, b0a1, b1a0, b1a1, a0b0, a1b0, a0b1, a1b1), angle[0])

        # ----self-doubleLine-a----
        selfParam = self._getDoubleLineParameterByIntersection(selfRawParameter)
        # ----another-doubleLine-b---
        anotherParam = doubleLine._getDoubleLineParameterByIntersection(anotherRawParameter)

        # ----draw self-doubleLine-a----
        self.drawDoubleLineByparameterList( selfParam[0], selfParam[1] )
        # ----draw another-doubleLine-b---
        doubleLine.drawDoubleLineByparameterList(  anotherParam[0], anotherParam[1] )


    #modify this doubleLine with parameter
    def _getDoubleLineParameterByIntersection(self, parameter):

        (a0b0, a0b1, a1b0, a1b1, b0a0, b1a0, b0a1, b1a1), angle = parameter
        #初始化a0, a1的参数数组 
        a0List=(0,1)
        a1List=(0,1)
        if angle > 0:
            #self.line0 a0
            if a0b0<1 and a0b1>0: 
                #a0 splited
                if b0a0 > 0 and b1a0 > 0 :
                    a0List=(0,a0b1,a0b0,1)
                #a0 no change
                elif b0a0 <= 0 or b1a0 <= 0 :
                    pass
            elif a0b0 >=1 :
                #a0 become longer
                if b0a0<0 or b1a0<0:
                    a0List=(0,a0b0)
                #a0 become shorter
                else:
                    a0List=(0,a0b1)
            elif  a0b1 <=0 :
                #a0 become longer
                if b0a0<0 or b1a0<0:
                    a0List=(a0b1,1)
                #a0 become shorter
                else:
                    a0List=(a0b0,1)

            #self.line1 a1
            if a1b0<1 and a1b1>0: 
                #a1 splited
                if b0a1 < 1 and b1a1 < 1 :
                    a1List=(0,a1b1,a1b0,1)
                #a1 no change
                elif b0a1 >= 1 or b1a1 >= 1 :
                    pass
            elif a1b0 >=1  :
                #a1 become longer
                if b0a1>1 or b1a1>1:
                    a1List=(0,a1b0)
                #a1 become short
                else:
                    a1List=(0,a1b1)
            elif a1b1 <=0 :
                #a1 become longer
                if b0a1>1 or b1a1>1:
                    a1List=(a1b1,1)
                #a1 become short
                else:
                    a1List=(a1b0,1)

        else:
            #self.line0 a0
            if a0b0>0 and a0b1<1: 
                #a0 splited
                if b0a0 < 1 and b1a0 < 1 :
                    a0List= (0,a0b0,a0b1,1)
                #a0 no change
                elif b0a0 >= 1 or b1a0 >= 1 :
                    pass
            elif a0b0 <=0 :
                #a0 become longer
                if b0a0>1 or b1a0>1:
                    a0List=(a0b0,1)
                #a0 become shorter
                else:
                    a0List=(a0b1,1)
            elif a0b1 >=1 :
                #a0 become longer
                if b0a0>1 or b1a0>1:
                    a0List=(0,a0b1)
                #a0 become shorter
                else:
                    a0List=(0,a0b0)

            #self.line1 a1
            if a1b0>0 and a1b1<1: 
                #a1 splited
                if b0a1 > 0 and b1a1 > 0 :
                    a1List=(0,a1b0,a1b1,1)
                #a1 no change
                elif b0a1 <= 0 or b1a1 <= 0 :
                    pass
            elif a1b0 <=0 :
                #a1 become longer
                if b0a1<0 or b1a1<0:
                    a1List=(a1b0,1)
                #a1 become short
                else:
                    a1List=(a1b1,1)
            elif a1b1 >=1 :
                #a1 become longer
                if b0a1<0 or b1a1<0:
                    a1List=(0,a1b1)
                #a1 become short
                else:
                    a1List=(0,a1b0)

        # line0 parameterList  and line1 parameterList
        return (a0List, a1List)

    ##########IntersectionWithDoubleLine end######################

   
    def draw(self):
        # draw this doubleLine in sc.doc
        line0Id = sc.doc.Objects.AddLine(self.line0)
        line1Id = sc.doc.Objects.AddLine(self.line1)
        return (line0Id,line1Id)

    @staticmethod
    def _DrawLineByParameter(line, parameterList):
        # draw line segments to current doc.
        for i in range(len(parameterList)): 
            if i%2 == 0:
                sc.doc.Objects.AddLine( line.PointAt(parameterList[i]), line.PointAt(parameterList[i+1]) )

    def drawDoubleLineByparameterList(self, paramList0, paramList1 ):
        """ draw doubleLine with parameterList.
        input:
            paramList0: the paramerter list from  self.line0
            paramList1: the paramerter list from  self.line1
        """
        self._DrawLineByParameter(self.line0, paramList0)
        self._DrawLineByParameter(self.line1, paramList1)

    # sc.doc.Objects.FindByCrossingWindowRegion(viewport, (screen1, screen2, screen3), True, filter)
    @classmethod  
    def DrawDoubleLines(cls, layer, offsetType):
        # startPoint
        gp = Rhino.Input.Custom.GetPoint()
        gp.SetCommandPrompt("Pick first point")
        gp.Get()
        if gp.CommandResult()!=Rhino.Commands.Result.Success:
            return gp.CommandResult()
        point1 = gp.Point()
        line00 = None
        line01 = None
        # secondPoint
        oldLayer = rs.CurrentLayer(layer)
        while True:
            gp.SetCommandPrompt("Pick second point")
            gp.DrawLineFromPoint(point1,True)
            gp.EnableDrawLineFromPoint(True)
            gp.Get()
            if gp.CommandResult() != Rhino.Commands.Result.Success:
                rs.CurrentLayer(oldLayer)
                return gp.CommandResult()
            point2 = gp.Point()
            if point2:
                doubleLine = cls.MakeDoubleLine(config.DOUBLELINEWIDTH, point1, point2, offsetType)
                if (line00 != None)  and (line01 != None) : 
                    line10, line11 = doubleLine.draw()
                    p0 = rs.LineLineIntersection(line00,line10) 
                    p1 = rs.LineLineIntersection(line01,line11) 
                    rs.AddLine(rs.CurveStartPoint(line00),p0[0])
                    rs.AddLine(rs.CurveStartPoint(line01),p1[0])
                    rs.DeleteObject(line00)
                    rs.DeleteObject(line01)
                    line00 = rs.AddLine(p0[1],rs.CurveEndPoint(line10))
                    line01 = rs.AddLine(p1[1],rs.CurveEndPoint(line11))
                    rs.DeleteObject(line10)
                    rs.DeleteObject(line11)
                else: 
                    line00, line01 = doubleLine.draw()

                point1 = point2
            else:
                sc.errorhandler()
                break

        rs.CurrentLayer(oldLayer)
        gp.Dispose()

        
