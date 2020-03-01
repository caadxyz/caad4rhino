#coding=utf-8
'''
Copyright
create on 2020.02.28
@author mahaidong

description:
'''
import math
from datetime import datetime, timedelta
import time
import Rhino
import rhinoscriptsyntax as rs

class SunPath:
    def __init__(self,theLatitude, theLongitude, GMT ):
        self.latitude = theLatitude
        self.longitude = theLongitude
        self.GMT = GMT

    def calculateSunFromLocalDatetime( self, theLocalDatetime ):
        utcDatetime = theLocalDatetime - timedelta( hours=self.GMT )
        return self.__calculateSunPosition( utcDatetime )
    
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

    def calculateSunriseSunset(self, year, month, day):
        pass
    
    def drawSunPath(self):
        pass

class Sun:
    def __init__(self, datetime, altitude, azimuth ):
        self.datetime = datetime
        self.altitude = altitude
        self.azimuth = azimuth
        self.sunVector = self._calculateSunVector() 

    def _calculateSunVector(self):
        """
        sunVector = rs.VectorRotate( (0,1,0), -(azimuth*180/math.pi), (0,0,1) )
        return rs.VectorRotate( sunVector, altitude*180/math.pi, rs.VectorCrossProduct( sunVector,(0,0,1)) )
        """
        northVector = Rhino.Geometry.Vector3d(0,1,0)
        zAxis = Rhino.Geometry.Vector3d(0,0,1)
        northVector.Rotate( -self.azimuth, zAxis )
        northVector.Rotate( self.altitude, Rhino.Geometry.Vector3d.CrossProduct(northVector,zAxis) )
        return northVector


