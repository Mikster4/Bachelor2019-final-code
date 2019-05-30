#!/usr/bin/python3
import sys
import math
import xml.etree.ElementTree as xml

# Simple coordinate class
class Coordinate:
    def __init__(self, id_num, x, y, z):
        self.ID = id_num
        self.X = x
        self.Y = y
        self.Z = z

mold = None

# Exit to terminal if wrong number of arguments
if len(sys.argv) == 3:
    if sys.argv[2] == "-cast":
        mold = False
    elif sys.argv[2] == "-mold":
        mold = True
    else:
        print("Usage: ./applyDisplacement.py path [-cast | -mold]")
        sys.exit(1)
else:
    print("Usage: ./applyDisplacement.py path [-cast | -mold]")
    sys.exit(1)

# Open the file and create coordinate list
filename = sys.argv[1]
model_xml = xml.parse(filename)
model_data = model_xml.getroot()
coords = []
for coord in model_data.iter('node'):
    c_text = coord.text
    if c_text != None:
        c = c_text.split(',')
        coords.append(Coordinate(int(coord.get('id')),float(c[0]),float(c[1]),float(c[2])))

def findMinList(coordList):
    min_x = None
    for c in coordList:
        if min_x == None or c.X < min_x:
            min_x = c.X
    minList = []
    for c in coordList:
        if c.X == min_x:
            minList.append(c)
    return minList

def findMaxList(coordList):
    max_x = None
    for c in coordList:
        if max_x == None or c.X > max_x:
            max_x = c.X
    maxList = []
    for c in coordList:
        if c.X == max_x:
            maxList.append(c)
    return maxList

def findMoldInnerLeft(coordList):
    innerLeftList = []
    for c in coordList:
        if c.X == -25.0:
            innerLeftList.append(c)
    return innerLeftList

def findMoldInnerRight(coordList):
    innerRightList = []
    for c in coordList:
        if c.X == 25.0:
            innerRightList.append(c)
    return innerRightList

def findMoldInnerFront(coordList):
    innerFrontList = []
    for c in coordList:
        if c.Y == -5.0 and c.X < 5 and c.X > -5:
            innerFrontList.append(c)
    return innerFrontList

def findMoldInnerBack(coordList):
    innerBackList = []
    for c in coordList:
        if c.Y == 5.0 and c.X < 5 and c.X > -5:
            innerBackList.append(c)
    return innerBackList

# === Declare the root node ===
ROOT = xml.Element('febio_spec')
ROOT.set('version','2.5')


# === Create the "Globals" tag ===
module = model_data.find('Module')
if module == None:
    module = xml.Element('Module')
    module.set('type','solid')
ROOT.append(module)
GLOBALS = model_data.find('Globals')
if GLOBALS == None:
    GLOBALS = xml.Element('Globals')
    constants = xml.SubElement(GLOBALS,'Constants')
    t = xml.SubElement(constants,'T')
    t.text = str(0)
    R = xml.SubElement(constants,'R')
    R.text = str(0)
    Fc = xml.SubElement(constants,'Fc')
    Fc.text = str(0)
ROOT.append(GLOBALS)


# === Create the "Material" tag ===
def getSiliconeMaterial():
    silicone = xml.Element('material')
    silicone.set('id','1')
    silicone.set('name','silicone')
    silicone.set('type','isotropic elastic')
    xml.SubElement(silicone,'density').text='1.07'
    xml.SubElement(silicone,'E').text='0.2642'
    xml.SubElement(silicone,'v').text='0.48'
    return silicone

def getPLAMaterial():
    silicone = xml.Element('material')
    silicone.set('id','1')
    silicone.set('name','PLA')
    silicone.set('type','isotropic elastic')
    xml.SubElement(silicone,'density').text='1.3'
    xml.SubElement(silicone,'E').text='3.5'
    xml.SubElement(silicone,'v').text='0.3'
    return silicone

MATERIAL = model_data.find('Material')
if MATERIAL == None:
    MATERIAL = xml.Element('Material')
    if mold:
        MATERIAL.append(getPLAMaterial())
    else:
        MATERIAL.append(getSiliconeMaterial())
ROOT.append(MATERIAL)


# === Create the "Geometry" tag ===
def getFixedGeometry():
    fixed_nodes = xml.Element('NodeSet')
    fixed_nodes.set('name', 'fixedSet')
    fixed_coords = findMinList(coords)
    for c in fixed_coords:
        newNode = xml.Element('node')
        newNode.set('id', str(c.ID))
        fixed_nodes.append(newNode)
    return fixed_nodes

GEOMETRY = model_data.find('Geometry')
if GEOMETRY == None:
    GEOMETRY = xml.Element('Geometry')
GEOMETRY.append(getFixedGeometry())
ROOT.append(GEOMETRY)


# === Create the "Boundary" tag ===
def getFixedBoundary():
    fix = xml.Element('fix')
    fix.set('bc','x,y,z')
    fix.set('node_set','fixedSet')
    return fix

BOUNDARY = model_data.find('Boundary')
if BOUNDARY == None:
    BOUNDARY = xml.Element('Boundary')
BOUNDARY.append(getFixedBoundary())
ROOT.append(BOUNDARY)


LOADDATA = model_data.find('LoadData')
if LOADDATA == None:
    LOADDATA = xml.Element('LoadData')
loadcurve = xml.SubElement(LOADDATA, 'loadcurve')
loadcurve.set('id','1')
loadcurve.set('type','smooth')
point0 = xml.SubElement(loadcurve,'point')
point0.text = '0,0'
point1 = xml.SubElement(loadcurve,'point')
point1.text = '1,1'
ROOT.append(LOADDATA)


# === Create the "Output" step ===
OUTPUT = model_data.find('Output')
if OUTPUT == None:
    OUTPUT = xml.fromstring('<Output><plotfile type="febio"><var type="displacement"/><var type="stress_printout"/><var type="stress"/></plotfile></Output>')
ROOT.append(OUTPUT)


# === Create each step ===
def setDisplacement (step, direction, nodeset, scale_val):
    step_nodes = GEOMETRY.find("NodeSet[@name='thestep']")
    if step_nodes != None:
        GEOMETRY.remove(step_nodes)
    step_nodes = xml.Element('NodeSet')
    step_nodes.set('name', step.attrib['name'])
    for n in nodeset:
        newNode = xml.Element('node')
        newNode.set('id', str(n.ID))
        step_nodes.append(newNode)
    GEOMETRY.append(step_nodes)

    bnd = step.find("Boundary")
    if bnd != None:
        step.remove(bnd)
    bnd = xml.SubElement(step, 'Boundary')
    prescribe = xml.SubElement(bnd, 'prescribe')
    prescribe.set('bc',direction)
    prescribe.set('node_set',step_nodes.attrib['name'])

    scale = xml.SubElement(prescribe,'scale')
    scale.set('lc','1')
    scale.text = str(scale_val)

    relative = xml.SubElement(prescribe, 'relative')
    relative.text = '0'

def setLoad(step, direction, nodeset, value):
    step_nodes = GEOMETRY.find("NodeSet[@name='thestep']")
    if step_nodes != None:
        GEOMETRY.remove(step_nodes)
    step_nodes = xml.Element('NodeSet')
    step_nodes.set('name', step.attrib['name'])
    for n in nodeset:
        newNode = xml.Element('node')
        newNode.set('id', str(n.ID))
        step_nodes.append(newNode)
    GEOMETRY.append(step_nodes)

    load = step.find("Loads")
    if load != None:
        step.remove(load)
    load = xml.SubElement(step, 'Loads')
    nodal_load = xml.SubElement(load, 'nodal_load')
    nodal_load.set('bc',direction)
    nodal_load.set('node_set',step_nodes.attrib['name'])

    scale = xml.SubElement(nodal_load,'scale')
    scale.set('lc','1')
    scale.text = str(1.0)

    val = xml.SubElement(nodal_load,'value')
    val.text = str(value)

def addLoad(step, direction, nodeset, value, name):
    step_nodes = xml.Element('NodeSet')
    step_nodes.set('name', name)
    for n in nodeset:
        newNode = xml.Element('node')
        newNode.set('id', str(n.ID))
        step_nodes.append(newNode)
    GEOMETRY.append(step_nodes)

    load = step.find('Loads')
    nodal_load = xml.SubElement(load, 'nodal_load')
    nodal_load.set('bc',direction)
    nodal_load.set('node_set',name)

    scale = xml.SubElement(nodal_load,'scale')
    scale.set('lc','1')
    scale.text = str(1.0)

    val = xml.SubElement(nodal_load,'value')
    val.text = str(value)

STEP = xml.Element("Step")
control = xml.fromstring('<Control>\n<time_steps>10</time_steps><step_size>0.1</step_size><max_refs>15</max_refs><max_ups>10</max_ups><diverge_reform>1</diverge_reform><reform_each_time_step>1</reform_each_time_step><dtol>0.001</dtol><etol>0.01</etol><rtol>0</rtol><lstol>0.9</lstol><min_residual>1e-020</min_residual><qnmethod>0</qnmethod><time_stepper><dtmin>0.01</dtmin><dtmax>0.1</dtmax><max_retries>5</max_retries><opt_iter>10</opt_iter></time_stepper><analysis type="static" /><print_level>PRINT_MAJOR_ITRS</print_level></Control>')
STEP.append(control)
STEP.set("name","thestep")
ROOT.append(STEP)

if mold:
    setLoad(STEP, "x", findMoldInnerRight(coords), 0.1)
    f = open('testout_1.feb', 'w+')
    f.write('<?xml version="1.0" encoding="ISO-8859-1"?>\n')
    f.write(xml.tostring(ROOT, encoding="unicode"))
    f.close()

    setLoad(STEP, "y", findMoldInnerFront(coords),-0.1)
    addLoad(STEP, "y", findMoldInnerBack(coords), 0.1, "backCoords")
    f = open('testout_2.feb', 'w+')
    f.write('<?xml version="1.0" encoding="ISO-8859-1"?>\n')
    f.write(xml.tostring(ROOT, encoding="unicode"))
    f.close()

else:
    setDisplacement(STEP, "x", findMaxList(coords), -10)
    f = open('testout_1.feb', 'w+')
    f.write('<?xml version="1.0" encoding="ISO-8859-1"?>\n')
    f.write(xml.tostring(ROOT, encoding="unicode"))
    f.close()

    setDisplacement(STEP, "x", findMaxList(coords), 20)
    f = open('testout_2.feb', 'w+')
    f.write('<?xml version="1.0" encoding="ISO-8859-1"?>\n')
    f.write(xml.tostring(ROOT, encoding="unicode"))
    f.close()

    setDisplacement(STEP, "y", findMaxList(coords), 10)
    f = open('testout_3.feb', 'w+')
    f.write('<?xml version="1.0" encoding="ISO-8859-1"?>\n')
    f.write(xml.tostring(ROOT, encoding="unicode"))
    f.close()

    setDisplacement(STEP, "y", findMaxList(coords), -10)
    f = open('testout_4.feb', 'w+')
    f.write('<?xml version="1.0" encoding="ISO-8859-1"?>\n')
    f.write(xml.tostring(ROOT, encoding="unicode"))
    f.close()
