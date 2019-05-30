#!/usr/bin/python3
import sys, os
import math
import xml.etree.ElementTree as xml
import matplotlib.pyplot as plt

TEST_COUNT = 4

FEBIO_PATH = "../../FEBio2.8.5/bin/"

mold = None
if len(sys.argv) == 2 and sys.argv[1] == "-mold":
    mold = True
    TEST_COUNT=2
else:
    mold = False

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

def runTests():
    # Total result is true if all stress tests succeed, false otherwise.
        total_result = True
        testArray = [] # A list of test results
        failArray = [] # A list of tests that failed
        for test_count in range(1,TEST_COUNT+1):
            test_result = os.system("./"+FEBIO_PATH+"febio2.lnx64 -i testout_"+str(test_count)+".feb -silent > /dev/null")==0
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
                print("MaxElem is "+str(maxind))
                testArray.append((findCoordinates(maxind),maxval))
            else:
                failArray.append(test_count)
            total_result = total_result & test_result
        return total_result, testArray, failArray

def testCast(width,angle):
    # Generate the mesh and stress tests
        print("Testing with %d mm thickness and %d degree wedge" % (width,angle))
        os.system("./generateMesh.py %d %d" % (width,angle))
        os.system("./generateGeometry.py tmp_model.xml -cast")
        os.system("./applyDisplacement.py tmp_model.feb -cast")

        total_result, testArray, failArray = runTests()

        if total_result:
            validArray.append((width,angle,True))
            stressArray.append((width,angle,testArray))
            print("Success. Elements with highest stress: "+str(testArray))
        else:
            validArray.append((width,angle,False))
            stressArray.append((width,angle,None))
            print("Failure. The following tests failed: "+str(failArray))

def testMold(side,bottom):
    # Generate the mesh and stress tests
        print("Testing with %d mm side and %d mm bottom thickness (%d mm wedge thickness, %d degree wedge)" % (side,bottom,10,90))
        os.system("./generateMesh.py %d %d %d %d" % (10,90,side,bottom))
        os.system("./generateGeometry.py")
        os.system("./applyDisplacement.py tmp_model.feb -mold")

        total_result, testArray, failArray = runTests()

        if total_result:
            validArray.append((side,bottom,True))
            stressArray.append((side,bottom,testArray))
            print("Success. Elements with highest stress: "+str(testArray))
        else:
            validArray.append((side,bottom,False))
            stressArray.append((side,bottom,None))
            print("Failure. The following tests failed: "+str(failArray))

validArray = []
stressArray = []

if mold:
    for b in range(1,11):
        for s in range(1,11):
            testMold(s,b)
else:
    for w in range(1,21,2):
        for a in range(10,170,30):
            testCast(w,a)

f = open("threshold_result", "w+")
for x in range(len(validArray)):
    f.write("%03d %03d\t" % (validArray[x][0],validArray[x][1]))
    if validArray[x][2]:
        f.write("Success : "+str(stressArray[x][2])+"\n")
    else:
        f.write("Failure\n")
f.close()

f = open("linreg_data", "w+")
for x in range(len(validArray)):
    if validArray[x][2]:
        f.write("%d,%d" % (validArray[x][0],validArray[x][1]))
        for n in range(len(stressArray[x][2])):
            f.write(",%E" %
                    stressArray[x][2][n][1])
        f.write("\n")

scatter_x = []
scatter_z = []
scatter_w = []
scatter_a = []
for x in range(len(stressArray)):
    if validArray[x][2]:
        scatter_w.append(validArray[x][0])
        scatter_a.append(validArray[x][1])
        for y in range(len(stressArray[x][2])):
            c_List = stressArray[x][2][y][0]
            x_sum = 0
            z_sum = 0
            for c in range(len(c_List)):
                x_sum += c_List[c][0]
                z_sum += c_List[c][2]
            scatter_x.append(x_sum / len(c_List))
            scatter_z.append(z_sum / len(c_List))

plt.scatter(scatter_x, scatter_z)
plt.xlabel('X')
plt.ylabel('Z')
plt.title('Scatterplot of coordinates with most stress')
plt.ylim
plt.grid(False)
ax = plt.gca()
ax.set_xlim([-50, 50])
ax.set_ylim([-25, 0])
plt.show()

plt.scatter(scatter_w, scatter_a)
plt.xlabel('Thickness (mm)')
plt.ylabel('Wedge (degrees)')
plt.title('Scatterplot of successful tests')
plt.grid(True)
plt.show()
