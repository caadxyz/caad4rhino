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

class SunPosition:
    Deg2Rad = math.pi/180.0
    Rad2Deg = 180.0/math.pi
    """
    brief Calculates the sun light. 
    
    CalcSunPosition calculates the suns "position" based on a 
    given date and time in local time, latitude and longitude 
    expressed in decimal degrees. It is based on the method 
    found here: 
    http://guideving.blogspot.com/2010/08/sun-position-in-c.html
    The calculation is only satisfiably correct for dates in 
    the range March 1 1900 to February 28 2100. 
    param dateTime Time and date in local time. 
    param latitude Latitude expressed in decimal degrees. 
    param longitude Longitude expressed in decimal degrees. 
    """
    def calculateSunPositionWithGMT(self, theDatetime, GMT, theLatitude, theLongitude):
        # Convert to UTC
        aUtcDatetime = theDatetime - timedelta(hours=GMT)
        return self.calculateSunPosition( aUtcDatetime, theLatitude, theLongitude)
    def calculateSunPositionByLocalDatetime(self, theLocalDatetime, theLatitude, theLongitude):
        # Convert to UTC
        aUtcDatetime = SunPosition.Local2utc(theLocalDatetime) 
        return self.calculateSunPosition( aUtcDatetime, theLatitude, theLongitude)
    def calculateSunPosition(self, theUtcDatetime, theLatitude, theLongitude):
        # Number of days from J2000.0.
        julianDate = 367 * theUtcDatetime.year - \
                math.floor((7.0 / 4.0) * (theUtcDatetime.year + \
                math.floor((theUtcDatetime.month + 9.0) / 12.0))) + \
                math.floor((275.0 * theUtcDatetime.month ) / 9.0) +  theUtcDatetime.day - 730531.5
        julianCenturies = julianDate / 36525.0

        # Sidereal Time  
        SECONDS_PER_MINUTE  = 60
        SECONDS_PER_HOUR    = 3600
        totalHours = theUtcDatetime.hour + theUtcDatetime.minute/60 + theUtcDatetime.second/3600
        siderealTimeHours = 6.6974 + 2400.0513 * julianCenturies
        siderealTimeUT = siderealTimeHours +  (366.2422 / 365.2422) * totalHours
        siderealTime = siderealTimeUT * 15 + theLongitude

        # Refine to number of days (fractional) to specific time.
        julianDate += totalHours / 24.0
        julianCenturies = julianDate / 36525.0

        #Solar Coordinates
        meanLongitude = SunPosition.CorrectAngle(self.Deg2Rad * (280.466 + 36000.77 * julianCenturies))

        meanAnomaly = SunPosition.CorrectAngle(self.Deg2Rad * (357.529 + 35999.05 * julianCenturies))

        equationOfCenter = self.Deg2Rad * ((1.915 - 0.005 * julianCenturies) * math.sin(meanAnomaly) + \
                0.02 * math.sin(2 * meanAnomaly))

        elipticalLongitude = SunPosition.CorrectAngle(meanLongitude + equationOfCenter)

        obliquity = (23.439 - 0.013 * julianCenturies) * self.Deg2Rad

        # Right Ascension  
        rightAscension = math.atan2( math.cos(obliquity) * math.sin(elipticalLongitude),  
                math.cos(elipticalLongitude));  
          
        declination = math.asin( math.sin(rightAscension) * math.sin(obliquity))

        # Horizontal Coordinates
        hourAngle = SunPosition.CorrectAngle(siderealTime * self.Deg2Rad) - rightAscension

        if (hourAngle > math.pi):
            hourAngle -= 2 * math.pi
  
        altitude = math.asin(math.sin(theLatitude * self.Deg2Rad) * math.sin(declination) + \
                math.cos(theLatitude * self.Deg2Rad) * math.cos(declination) * math.cos(hourAngle))

        # Nominator and denominator for calculating Azimuth
        # angle. Needed to test which quadrant the angle is in.
        aziNom = -math.sin(hourAngle)
        aziDenom = math.tan(declination) * math.cos(theLatitude * self.Deg2Rad) - \
                math.sin(theLatitude * self.Deg2Rad) * math.cos(hourAngle)

        azimuth = math.atan(aziNom / aziDenom)

        if (aziDenom < 0): 
            # In 2nd or 3rd quadrant
            azimuth += math.pi
        elif (aziNom < 0): 
            # In 4th quadrant
            azimuth += 2 * math.pi

        #radian
        return {"altitude": altitude, "azimuth": azimuth}

    
    @staticmethod
    def Local2utc(theLocalTime):
        aTimeStruct = time.mktime(theLocalTime.timetuple())
        return datetime.utcfromtimestamp(aTimeStruct)
    
    @staticmethod
    def CorrectAngle( angleInRadians ):
        if angleInRadians < 0:
            return 2 * math.pi - (math.fabs(angleInRadians) % (2 * math.pi))
        elif angleInRadians > 2 * math.pi :
            return angleInRadians % (2 * math.pi)
        else:
            return angleInRadians
