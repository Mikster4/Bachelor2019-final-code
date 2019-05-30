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
if len(sys.argv) == 2:
    print("Usage: ./applyForce.py path force_magnitude")
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
bnd_file = open('boundary_box', 'r')
bnd_min_s = (bnd_file.readline()).split(';')
bnd_max_s = (bnd_file.readline()).split(';')
bnd_file.close()
bnd_min = Coordinate(1,float(bnd_min_s[0]),float(bnd_min_s[1]),float(bnd_min_s[2]))
bnd_max = Coordinate(2,float(bnd_max_s[0]),float(bnd_max_s[1]),float(bnd_max_s[2]))
min_dist = 0
if bnd_max.Y-bnd_min.Y < bnd_max.X-bnd_min.X:
    min_dist = bnd_max.Y-bnd_min.Y
else:
    min_dist = bnd_max.X-bnd_min.X

def findMinXList(coordList):
    c_list = []
    for c in coordList:
        if c.X == bnd_min.X and c.Y >= (bnd_min.Y+bnd_max.Y)/2-min_dist/2 and c.Y <= (bnd_min.Y+bnd_max.Y)/2+min_dist/2:
            c_list.append(c)
    return c_list

def findMaxXList(coordList):
    c_list = []
    for c in coordList:
        if c.X == bnd_max.X and c.Y >= (bnd_min.Y+bnd_max.Y)/2-min_dist/2 and c.Y <= (bnd_min.Y+bnd_max.Y)/2+min_dist/2:
            c_list.append(c)
    return c_list

def findMinYList(coordList):
    c_list = []
    for c in coordList:
        if c.Y == bnd_min.Y and c.X >= (bnd_min.X+bnd_max.X)/2-min_dist/2 and c.X <= (bnd_min.X+bnd_max.X)/2+min_dist/2:
            c_list.append(c)
    return c_list

def findMaxYList(coordList):
    c_list = []
    for c in coordList:
        if c.Y == bnd_max.Y and c.X >= (bnd_min.X+bnd_max.X)/2-min_dist/2 and c.X <= (bnd_min.X+bnd_max.X)/2+min_dist/2:
            c_list.append(c)
    return c_list

force = 10 ** (float(sys.argv[2]))
area = min_dist*(bnd_max.Z-bnd_min.Z)

print("Force applied in -x direction: %f MPa" % (len(findMinXList(coords))*force/area))
print("Force applied in -y direction: %f MPa" % (len(findMinYList(coords))*force/area))
print("Force applied in +x direction: %f MPa" % (len(findMaxXList(coords))*force/area))
print("Force applied in +y direction: %f MPa" % (len(findMaxYList(coords))*force/area))


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
ROOT.append(MATERIAL)


# === Create the "Geometry" tag ===
def addNodeSet(name, nodeset):
    nodes = xml.Element('NodeSet')
    nodes.set('name',name)
    for c in nodeset:
        newNode = xml.Element('node')
        newNode.set('id', str(c.ID))
        nodes.append(newNode)
    GEOMETRY.append(nodes)

GEOMETRY = model_data.find('Geometry')
if GEOMETRY == None:
    GEOMETRY = xml.Element('Geometry')
ROOT.append(GEOMETRY)


# === Create the "Boundary" tag ===
def addFixedBoundary(name):
    fix = xml.Element('fix')
    fix.set('bc','x,y,z')
    fix.set('node_set',name)
    BOUNDARY.append(fix)

BOUNDARY = model_data.find('Boundary')
if BOUNDARY == None:
    BOUNDARY = xml.Element('Boundary')
ROOT.append(BOUNDARY)

loadcurves = 0
def addLoadCurve():
    global loadcurves
    loadcurves += 1
    loadcurve = xml.SubElement(LOADDATA, 'loadcurve')
    loadcurve.set('id',str(loadcurves))
    loadcurve.set('type','smooth')
    point0 = xml.SubElement(loadcurve,'point')
    point0.text = '0,0'
    point1 = xml.SubElement(loadcurve,'point')
    point1.text = '1,1'

LOADDATA = model_data.find('LoadData')
if LOADDATA == None:
    LOADDATA = xml.Element('LoadData')
ROOT.append(LOADDATA)
addLoadCurve()


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

def setLoad(direction, nodeset, value):
    load = STEP.find("Loads")
    if load != None:
        STEP.remove(load)
    load = xml.SubElement(STEP, 'Loads')
    nodal_load = xml.SubElement(load, 'nodal_load')
    nodal_load.set('bc',direction)
    nodal_load.set('node_set',nodeset)

    scale = xml.SubElement(nodal_load,'scale')
    scale.set('lc','1')
    scale.text = '1.0'

    val = xml.SubElement(nodal_load,'value')
    val.text = str(value)

def addLoad(direction, nodeset, value):
    load = STEP.find('Loads')
    nodal_load = xml.SubElement(load, 'nodal_load')
    nodal_load.set('bc',direction)
    nodal_load.set('node_set',nodeset)

    scale = xml.SubElement(nodal_load,'scale')
    scale.set('lc','2')
    scale.text = '1.0'

    val = xml.SubElement(nodal_load,'value')
    val.text = str(value)

STEP = xml.Element("Step")
control = xml.fromstring('<Control>\n<time_steps>10</time_steps><step_size>0.1</step_size><max_refs>15</max_refs><max_ups>10</max_ups><diverge_reform>1</diverge_reform><reform_each_time_step>1</reform_each_time_step><dtol>0.001</dtol><etol>0.01</etol><rtol>0</rtol><lstol>0.9</lstol><min_residual>1e-020</min_residual><qnmethod>0</qnmethod><time_stepper><dtmin>0.01</dtmin><dtmax>0.1</dtmax><max_retries>5</max_retries><opt_iter>10</opt_iter></time_stepper><analysis type="static" /><print_level>PRINT_MAJOR_ITRS</print_level></Control>')
STEP.append(control)
STEP.set("name","thestep")
ROOT.append(STEP)

addNodeSet('MinX', findMinXList(coords))
addNodeSet('MaxX', findMaxXList(coords))
addNodeSet('MinY', findMinYList(coords))
addNodeSet('MaxY', findMaxYList(coords))

addFixedBoundary('MinX')
setLoad('x', 'MaxX', force)
f = open('testmold_1.feb', 'w+')
f.write('<?xml version="1.0" encoding="ISO-8859-1"?>\n')
f.write(xml.tostring(ROOT, encoding="unicode"))
f.close()

BOUNDARY.remove(BOUNDARY.find('fix'))
addFixedBoundary('MinY')
setLoad('y', 'MaxY', force)
f = open('testmold_2.feb', 'w+')
f.write('<?xml version="1.0" encoding="ISO-8859-1"?>\n')
f.write(xml.tostring(ROOT, encoding="unicode"))
f.close()

BOUNDARY.remove(BOUNDARY.find('fix'))
addFixedBoundary('MaxX')
setLoad('x', 'MinX', -1*force)
f = open('testmold_3.feb', 'w+')
f.write('<?xml version="1.0" encoding="ISO-8859-1"?>\n')
f.write(xml.tostring(ROOT, encoding="unicode"))
f.close()

BOUNDARY.remove(BOUNDARY.find('fix'))
addFixedBoundary('MaxY')
setLoad('y', 'MinY', -1*force)
f = open('testmold_4.feb', 'w+')
f.write('<?xml version="1.0" encoding="ISO-8859-1"?>\n')
f.write(xml.tostring(ROOT, encoding="unicode"))
f.close()
