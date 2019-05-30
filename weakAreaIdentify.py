#!/usr/bin/python3
import sys, os
import math
import xml.etree.ElementTree as xml
import matplotlib.pyplot as plt

TEST_COUNT = 4

FEBIO_PATH = "../../FEBio2.8.5/bin/"

# Finds the start nodes of a given element
# The four (4) nodes are returned as a tuple in an array
def findCoordinates(elemID):
    crd = []
    f = open("position.out", "r")
    l = f.readline()
    while (l):
        id = int(l.split(":")[0])
        if (id == elemID):
            coords = l.split(":")[1]
            for i in range(0,4):
                c = (coords.split("(")[i+1]).split(",")
                crd.append((float(c[0]),
                            float(c[1]),
                            float(c[2].split(")")[0])))
        l = f.readline()
    f.close()
    return crd

def findMaxDisplacement():
    disp_val = 0
    disp_id = 0
    f = open("displacement.out","r")
    l = f.readline()
    while (l):
        id = int(l.split(":")[0])
        distance = 0.0
        coords = l.split(":")[1]
        for i in range(0,4):
            c = (coords.split("(")[i+1]).split(",")
            distance += ((float(c[0]) ** 2) + (float(c[1]) ** 2) + (float(c[2].split(")")[0]) ** 2)) ** 0.5
        distance = distance/4.0
        if distance > disp_val:
            disp_val = distance
            disp_id = id
        l = f.readline()
    f.close()
    return (findCoordinates(disp_id),disp_val)

validArray = []
stressArray = []
dispArray = []

model_path = sys.argv[1]

magnitude = -5
failure = False

os.system("./generateGeometry.py %s -pla" % model_path)
while not failure:
    print("Testing with magnitude %d." % magnitude)
    os.system("./applyForce.py tmp_model.feb %d" % magnitude)

    total_result = True
    stress_testArray = [] # A list of test results for stress
    disp_testArray = [] # A list of test results for displacement
    failArray = [] # A list of tests that failed
    for test_count in range(1,TEST_COUNT+1):
        test_result = os.system("./"+FEBIO_PATH+"febio2.lnx64 -i testmold_"+str(test_count)+".feb -silent")==0
        if (test_result):
            elem_stress_array = []
            f = open("stress.out", "r")
            l = f.readline()
            while (l):
                elem = int(l.split(":")[0])
                cauchy = list(map(float, (l.split(":")[1]).split(";")))

                # For clarity:
                xx = cauchy[0]
                yy = cauchy[1]
                zz = cauchy[2]
                xy = cauchy[3]
                yz = cauchy[4]
                xz = cauchy[5]

                mises = (0.5*((xx-yy)**2.0+(yy-zz)**2.0+(zz-xx)**2.0)+
                         3.0*(xy**2+yz**2+xz**2))**0.5

                elem_stress_array.append(mises)
                l = f.readline()
            f.close()
            maxval = 0.0
            maxind = 0
            for i in range(len(elem_stress_array)):
                if elem_stress_array[i] > maxval:
                    maxval = elem_stress_array[i]
                    maxind = i
            stress_testArray.append((findCoordinates(maxind),maxval))
            disp_testArray.append(findMaxDisplacement())
        else:
            failArray.append(test_count)
        total_result = total_result & test_result

    if total_result:
        magnitude += 1
        print("Success. Continuing with magnitude %d.\n" % magnitude)
        stressArray.append(stress_testArray)
        dispArray.append(disp_testArray)
    else:
        failure = True
        print("Tests "+str(failArray)+" failed. Printing values for tests of magnitude %d:" % (magnitude-1))
        for t in range(0,TEST_COUNT):
            print("\n===[TEST %d]===" % (t+1))
            print("In the previous test %d, the element with the highest stress had these coordinates:" % (t+1))
            stress_coords = stressArray[-1][t][0]
            for c in range(len(stress_coords)):
                print("X : %f ; Y : %f ; Z : %f" % (stress_coords[c][0],stress_coords[c][1],stress_coords[c][2]))
            print("In the previous test %d, the element with the highest displacement had these initial coordinates:" % (t+1))
            disp_coords = dispArray[-1][t][0]
            for c in range(len(disp_coords)):
                print("X : %f ; Y : %f ; Z : %f" % (disp_coords[c][0],disp_coords[c][1],disp_coords[c][2]))
