#coding=utf-8
'''
Copyright
create on 2020.02.28
@author mahaidong
'''
import math
from datetime import datetime, timedelta
import time
import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc

class SunPath:
    def __init__(self,theLatitude, theLongitude, GMT ):
        self.basePlane = Rhino.Geometry.Plane( Rhino.Geometry.Point3d.Origin, Rhino.Geometry.Vector3d.ZAxis)
        self.latitude = theLatitude
        self.longitude = theLongitude
        self.GMT = GMT

    def calculateSunFromLocalDatetime( self, theLocalDatetime ):
        utcDatetime = theLocalDatetime - timedelta( hours=self.GMT )
        return self.__calculateSun( utcDatetime )
 
    def __calculateSun(self, theUtcDatetime ):
        localDatetime = theUtcDatetime + timedelta( hours=self.GMT )
        """
        brief Calculates the sun light. 
        CalcSunPosition calculates the suns "position" based on a 
        given date and time in local time, latitude and longitude 
        expressed in decimal degrees. It is based on the method 
        found here: 
        http://guideving.blogspot.com/2010/08/sun-position-in-c.html
        The calculation is only satisfiably correct for dates in 
        the range March 1 1900 to February 28 2100. 
        param latitude Latitude expressed in decimal degrees. 
        param longitude Longitude expressed in decimal degrees. 
        """
        Deg2Rad = math.pi/180.0
        Rad2Deg = 180.0/math.pi
        # Number of days from J2000.0.
        julianDate = 367 * theUtcDatetime.year - \
                math.floor((7.0 / 4.0) * (theUtcDatetime.year + \
                math.floor((theUtcDatetime.month + 9.0) / 12.0))) + \
                math.floor((275.0 * theUtcDatetime.month ) / 9.0) +  theUtcDatetime.day - 730531.5
        julianCenturies = julianDate / 36525.0

        # Sidereal Time  
        SECONDS_PER_MINUTE  = 60
        SECONDS_PER_HOUR    = 3600
        totalHours = theUtcDatetime.hour + theUtcDatetime.minute/60.0 + theUtcDatetime.second/3600.0
        siderealTimeHours = 6.6974 + 2400.0513 * julianCenturies
        siderealTimeUT = siderealTimeHours +  (366.2422 / 365.2422) * totalHours
        siderealTime = siderealTimeUT * 15 + self.longitude

        # Refine to number of days (fractional) to specific time.
        julianDate += totalHours / 24.0
        julianCenturies = julianDate / 36525.0

        #Solar Coordinates
        meanLongitude = SunPath.CorrectAngle( Deg2Rad * (280.466 + 36000.77 * julianCenturies))

        meanAnomaly = SunPath.CorrectAngle( Deg2Rad * (357.529 + 35999.05 * julianCenturies))

        equationOfCenter = Deg2Rad * ((1.915 - 0.005 * julianCenturies) * math.sin(meanAnomaly) + \
                0.02 * math.sin(2 * meanAnomaly))

        elipticalLongitude = SunPath.CorrectAngle(meanLongitude + equationOfCenter)

        obliquity = (23.439 - 0.013 * julianCenturies) * Deg2Rad

        # Right Ascension  
        rightAscension = math.atan2( math.cos(obliquity) * math.sin(elipticalLongitude),  
                math.cos(elipticalLongitude));  
          
        declination = math.asin( math.sin(rightAscension) * math.sin(obliquity))

        # Horizontal Coordinates
        hourAngle = SunPath.CorrectAngle(siderealTime * Deg2Rad) - rightAscension

        if (hourAngle > math.pi):
            hourAngle -= 2 * math.pi
  
        altitude = math.asin(math.sin( self.latitude * Deg2Rad) * math.sin(declination) + \
                math.cos( self.latitude * Deg2Rad) * math.cos(declination) * math.cos(hourAngle))

        # Nominator and denominator for calculating Azimuth
        # angle. Needed to test which quadrant the angle is in.
        aziNom = -math.sin(hourAngle)
        aziDenom = math.tan(declination) * math.cos( self.latitude * Deg2Rad) - \
                math.sin( self.latitude * Deg2Rad) * math.cos(hourAngle)

        azimuth = math.atan(aziNom / aziDenom)

        if (aziDenom < 0): 
            # In 2nd or 3rd quadrant
            azimuth += math.pi
        elif (aziNom < 0): 
            # In 4th quadrant
            azimuth += 2 * math.pi

        #radian
        return Sun(localDatetime, altitude, azimuth)

    @staticmethod
    def CorrectAngle( angleInRadians ):
        if angleInRadians < 0:
            return 2 * math.pi - (math.fabs(angleInRadians) % (2 * math.pi))
        elif angleInRadians > 2 * math.pi :
            return angleInRadians % (2 * math.pi)
        else:
            return angleInRadians

    def dailyPathFromLocalDate( self, year, month, day, radius = 200.0 ):
        theLocalDatetime = datetime(year,month,day)
    
        # find the sun position for midnight, noon - 1 hour, noon + 1 hour!
        hours = [0, 11, 13]
        sunP = []
        validCircle =  False
        for hour in hours:
            utcDatetime = theLocalDatetime + timedelta( hours = hour) - timedelta( hours=self.GMT )
            sun = self.__calculateSun(utcDatetime)
            sunP.append(Rhino.Geometry.Point3d( sun.sunVector*radius ))

        # draw the circle base on these three points
        circle = Rhino.Geometry.Circle(*sunP)
        # intersect with the plan
        intersection = Rhino.Geometry.Intersect.Intersection.PlaneCircle(self.basePlane, circle)
    
        #if intersection draw the new curve for intersections and noon
        if intersection[1] != intersection[2]:
            startPt = circle.PointAt(intersection[1])
            endPt = circle.PointAt(intersection[2])
            midPt = sunP[1]
            return Rhino.Geometry.Arc(startPt, midPt, endPt)
        else:
            # add to check to be above the plane
            return circle
    

    def yearlyPath(self,radius = 200.0):
        # draw daily curves for all the months
        monthlyCrvs = []
        for m in range(1,13):
            crv = self.dailyPathFromLocalDate( 2000, m, 21 )
            if crv: monthlyCrvs.append(crv)
        
        # draw hourly curves for each of hours for 1st and 21st of all month
        hourlyCrvs = []
        days = [1, 7, 14, 21]
        sunP = []; 
        selHours = []

        if math.degrees(self.latitude)>0: month = 6
        else: month = 12
        
        # find the hours that the sun is up
        for hour in range(0,24):
            theLocalDatetime = datetime(2000,month,21,hour)
            utcDatetime = theLocalDatetime - timedelta( hours=self.GMT )
            sun = self.__calculateSun(utcDatetime)
            if sun.sunVector.Z > self.basePlane.OriginZ: 
                selHours.append(hour)
        
        for hour in selHours:
            for day in days:
                sunP = []
                for m in range(1,13):
                    theLocalDatetime = datetime( 2000, m, day, hour)
                    utcDatetime = theLocalDatetime - timedelta( hours=self.GMT )
                    sun = self.__calculateSun(utcDatetime)
                    sunP.append(Rhino.Geometry.Point3d( sun.sunVector*radius ))
            sunP.append(sunP[0])
            knotStyle = Rhino.Geometry.CurveKnotStyle.UniformPeriodic
            crv = Rhino.Geometry.Curve.CreateInterpolatedCurve(sunP, 3, knotStyle)
            intersectionEvents = Rhino.Geometry.Intersect.Intersection.CurvePlane(crv, 
                                                            self.basePlane, sc.doc.ModelAbsoluteTolerance)
            
            try:
                if len(intersectionEvents) != 0:
                    crvDomain = crv.Domain
                    crv0 = Rhino.Geometry.Curve.Trim(crv, intersectionEvents[0].ParameterA, intersectionEvents[1].ParameterA)
                    crv1 = Rhino.Geometry.Curve.Trim(crv, intersectionEvents[1].ParameterA, intersectionEvents[0].ParameterA)
                    t0 = crv0.Domain.Mid
                    p0 = crv0.PointAt(t0)
                    t1 = crv1.Domain.Mid
                    p1 = crv1.PointAt(t1)
                    if p0.Z>p1.Z:
                        crv = crv0
                    else:
                        crv = crv1
            except: pass
            
            if crv: 
                hourlyCrvs.append(crv)
        return monthlyCrvs, hourlyCrvs
     

    def compassCurves( self, cenPt, northVector, radius, centerLine ):

        baseCircle  = Rhino.Geometry.Circle(cenPt, radius).ToNurbsCurve()
        outerCircle = Rhino.Geometry.Circle(cenPt, 1.02*radius).ToNurbsCurve()
        angles = range(0,360,30)
        xMove = 0.03*radius
        
        def drawLine(cenPt, vector, radius, mainLine = False, xMove = 5):
            stPtRatio = 1
            endPtRatio = 1.08
            textPtRatio = endPtRatio + 0.08
            if mainLine: endPtRatio = 1.15; textPtRatio = 1.17
            stPt = Rhino.Geometry.Point3d.Add(cenPt, stPtRatio * radius * vector)
            if centerLine: stPt = cenPt
            endPt = Rhino.Geometry.Point3d.Add(cenPt, endPtRatio * radius * vector)
            textBasePt = Rhino.Geometry.Point3d.Add(cenPt, textPtRatio * radius * vector)
            
            if not mainLine: textBasePt = Rhino.Geometry.Point3d(textBasePt.X-xMove, textBasePt.Y-(xMove/4), textBasePt.Z)
            else: textBasePt = Rhino.Geometry.Point3d(textBasePt.X-(xMove/2), textBasePt.Y-(xMove/2), textBasePt.Z)
            return Rhino.Geometry.Line(stPt, endPt).ToNurbsCurve(), textBasePt, baseCircle, outerCircle
        
        lines = []; textBasePts = []
        mainAngles = [0, 90, 180, 270]
        mainText = ['N', 'E', 'S', 'W']
        compassText = []
        for angle in angles:
            mainLine = False
            if angle in mainAngles: mainLine = True
            vector = Rhino.Geometry.Vector3d(northVector)
            vector.Rotate(-math.radians(angle), Rhino.Geometry.Vector3d.ZAxis)
            line, basePt, baseCircle, outerCircle = drawLine(cenPt, vector, radius, mainLine, xMove)
            if len(angles) != 8 and len(angles) != 16:
                if mainLine == True: compassText.append(mainText[mainAngles.index(angle)])
                else: compassText.append(str(int(angle)))
            textBasePts.append(basePt)
            lines.append(line)
        
        lines.append(baseCircle)
        lines.append(outerCircle)

        return lines, textBasePts, compassText

    def draw(self, cenPt = Rhino.Geometry.Point3d.Origin, 
            northVector = Rhino.Geometry.Vector3d.YAxis, 
            radius = 200.0 , centerLine = False):

        # draw compass
        compassLines, compassTextPts, compassText = self.compassCurves(cenPt,northVector,radius,centerLine)
        for line in compassLines:
            sc.doc.Objects.AddCurve(line)

        for i in range( len(compassTextPts) ):
            text_entity = Rhino.Geometry.TextEntity()
            text_entity.Plane = Rhino.Geometry.Plane( compassTextPts[i],Rhino.Geometry.Vector3d(0,0,1))
            text_entity.Text = compassText[i]
            text_entity.TextHeight = 8
            text_entity.Justification = Rhino.Geometry.TextJustification.BottomLeft
            text_entity.FontIndex = sc.doc.Fonts.FindOrCreate("Arial", False, False)
            sc.doc.Objects.AddText(text_entity)

        # draw year path
        monthlyCrvs, hourlyCrvs = self.yearlyPath(radius)
        for arc in monthlyCrvs:
            if isinstance(arc, Rhino.Geometry.Arc):
                sc.doc.Objects.AddArc(arc)
            else: 
                sc.doc.Objects.AddCircle(arc)
        for crv in hourlyCrvs:
            sc.doc.Objects.AddCurve(crv)


class Sun:
    def __init__(self, datetime, altitude, azimuth ):
        self.datetime = datetime
        self.altitude = altitude
        self.azimuth = azimuth
        self.sunVector = self._calculateSunVector() 

    def _calculateSunVector(self):
        northVector = Rhino.Geometry.Vector3d(0,1,0)
        zAxis = Rhino.Geometry.Vector3d(0,0,1)
        northVector.Rotate( -self.azimuth, zAxis )
        northVector.Rotate( self.altitude, Rhino.Geometry.Vector3d.CrossProduct(northVector,zAxis) )
        return northVector

    def altitude2deg(self):
        return self.altitude*180/math.pi
    def azimuth2deg(self):
        return self.azimuth*180/math.pi


