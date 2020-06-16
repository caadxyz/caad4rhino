#coding=utf-8
'''
Copyright
create on 2020.02.28
@author mahaidong

description:
'''
import math
import System.Threading.Tasks as Tasks
import Rhino
import rhinoscriptsyntax as rs
import time
import datetime

class SunLightAnalysis(object):
    def __init__(self, theMeshs ):
        self.meshs = theMeshs
    
    def calculatePts( self, mesh, parallel = True ):
        pass

    def parallel_sunlightHoursCalculator(self, testPts, testVec, bldgMesh, contextMesh, parallel, sunVectors, northVector, timeStep = 1):
        # preparing bulk lists
        sunlightHours = [0] * len(testPts)
        sunlightHoursResult = [0] * len(testPts)
        intersectionStTime = time.time()
        YAxis = Rhino.Geometry.Vector3d.YAxis
        ZAxis = Rhino.Geometry.Vector3d.ZAxis
        PI = math.pi
        
        # Converting vectors to Rhino 3D Vectors
        sunV = []
        sunVectorCount = 0
        for vector in sunVectors:
            if vector[2] < 0: print "Sun vector " + `sunVectorCount + 1` + " removed since it represents a vector with negative Z!" 
            else: sunV.append(Rhino.Geometry.Vector3d(vector))
            sunVectorCount =+ 1
            
        angle = Rhino.Geometry.Vector3d.VectorAngle(northVector, YAxis)
        if northVector.X > 0 : angle = -angle
        # print math.degrees(angle)
        if angle != 0: [vec.Rotate(angle, ZAxis) for vec in sunV]
        
        sunVisibility = []
        for pt in testPts: sunVisibility.append(range(len(sunV)))
        
        try:
            def sunlightHoursCalculator(i):
                for vectorCount, vector in enumerate(sunV):
                    vecAngle = Rhino.Geometry.Vector3d.VectorAngle(vector, testVec[i]) # calculate the angle between the surface and sun vector
                    check = 0
                    if vecAngle < (PI/2):
                        check = 1; # this is simply here becuse I can't trust the break! Isn't it stupid?
                        ray = Rhino.Geometry.Ray3d(testPts[i], vector) # generate the ray
                        
                        if bldgMesh!=None:
                            if Rhino.Geometry.Intersect.Intersection.MeshRay(bldgMesh, ray) >= 0.0: check = 0
                        if check != 0 and contextMesh!=None:
                            if Rhino.Geometry.Intersect.Intersection.MeshRay(contextMesh,ray) >= 0.0: check = 0
                        
                        if check != 0:
                            sunlightHours[i] += 1/timeStep
                        
                    sunVisibility[i][vectorCount] = check
                
                sunlightHoursResult[i] = sunlightHours[i] # This is stupid but I'm tired to change it now...
        except:
            #print 'Error in Sunligh Hours calculation...'
            print "The calculation is terminated by user!"
            assert False
        
        # calling the function
        try:
            # calling the function
            if parallel:
                Tasks.Parallel.ForEach(range(len(testPts)), sunlightHoursCalculator)
            else:
                for i in range(len(testPts)):
                    sunlightHoursCalculator(i)
        except:
            return None, None, None
            
        intersectionEndTime = time.time()
        print 'Sunlight hours calculation time = ', ("%.3f" % (intersectionEndTime - intersectionStTime)), 'Seconds...'
        
        return sunlightHoursResult, sunVisibility
 
class MeshPreparation(object):
    
    def joinMesh(self, meshList):
        joinedMesh = Rhino.Geometry.Mesh()
        for m in meshList: joinedMesh.Append(m)
        return joinedMesh

    def parallel_testPointCalculator(self, analysisSrfs, disFromBase, parallel = True):
        # Mesh functions should be modified and be written interrelated as a class
        movingDis = disFromBase
    
        # preparing bulk lists
        testPoint =   [[]] * len(analysisSrfs)
        srfNormals =  [[]] * len(analysisSrfs)
        meshSrfCen =  [[]] * len(analysisSrfs)
        
        srfCount = 0
        for srf in analysisSrfs:
            testPoint[srfCount]   = range(srf.Faces.Count)
            srfNormals[srfCount]  = range(srf.Faces.Count)
            meshSrfCen[srfCount]  = range(srf.Faces.Count)
            srfCount += 1

        try:
            def srfPtCalculator(i):
                # calculate face normals
                analysisSrfs[i].FaceNormals.ComputeFaceNormals()
                analysisSrfs[i].FaceNormals.UnitizeFaceNormals()
                
                for face in range(analysisSrfs[i].Faces.Count):
                    srfNormals[i][face] = (analysisSrfs[i].FaceNormals)[face] # store face normals
                    meshSrfCen[i][face] = analysisSrfs[i].Faces.GetFaceCenter(face) # store face centers
                    # calculate test points
                    if srfNormals[i][face]:
                        movingVec = Rhino.Geometry.Vector3f.Multiply(movingDis,srfNormals[i][face])
                        testPoint[i][face] = Rhino.Geometry.Point3d.Add(Rhino.Geometry.Point3d(meshSrfCen[i][face]), movingVec)
                    
        except:
            print 'Error in Extracting Test Points'
            pass
        
        # calling the function
        if parallel:
            Tasks.Parallel.ForEach(range(len(analysisSrfs)),srfPtCalculator)
        else:
            for i in range(len(analysisSrfs)):
                srfPtCalculator(i)
    
        return testPoint, srfNormals
   