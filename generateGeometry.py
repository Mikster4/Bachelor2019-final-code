#!/usr/bin/python3
import sys, os
import numpy as np
import math
import xml.etree.ElementTree as xml
PATH_TO_LIBIGL = '../../LIBIGL/python'
sys.path.insert(0, PATH_TO_LIBIGL)
import pyigl as igl
PATH_TO_PYXCSG = '../../pyXCSG'
sys.path.insert(0, PATH_TO_PYXCSG)
from csgxml import parse_csg_graph
from utils import save_to_stl
import stl
import tetgen
import meshpy
import pyvista as pv
import vtk
from meshpy import tet
from meshpy.tet import MeshInfo, build
from matplotlib import pyplot as plt

ROOT = xml.Element('febio_spec')
ROOT.set('version','2.5')

module = xml.Element('Module')
module.set('type','solid')
ROOT.append(module)


GLOBALS = xml.Element('Globals')
constants = xml.SubElement(GLOBALS,'Constants')
t = xml.SubElement(constants,'T')
t.text = str(0)
R = xml.SubElement(constants,'R')
R.text = str(0)
Fc = xml.SubElement(constants,'Fc')
Fc.text = str(0)
ROOT.append(GLOBALS)

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
    silicone.set('id','2')
    silicone.set('name','PLA')
    silicone.set('type','isotropic elastic')
    xml.SubElement(silicone,'density').text='1.3'
    xml.SubElement(silicone,'E').text='3.5'
    xml.SubElement(silicone,'v').text='0.3'
    return silicone

MATERIAL = xml.SubElement(ROOT, 'Material')
MATERIAL.append(getSiliconeMaterial())
MATERIAL.append(getPLAMaterial())

GEOMETRY = xml.SubElement(ROOT,'Geometry')
NODES = xml.SubElement(GEOMETRY,'Nodes')
NODES.set('name','Object1')
ELEMENTS = xml.SubElement(GEOMETRY,'Elements')
ELEMENTS.set('type','tet4')
if len(sys.argv) == 3 and sys.argv[2] == "-pla":
    ELEMENTS.set('mat','2')
elif len(sys.argv) == 2:
    ELEMENTS.set('mat','1')
else:
    print("Usage: ./generateGeometry path [-pla]")
    sys.exit(1)
ELEMENTS.set('name','Part1')

nodeCount = 0
def AddNode(x,y,z):
    global nodeCount
    nodeCount += 1
    newNode = xml.SubElement(NODES, 'node')
    newNode.set('id',str(nodeCount))
    newNode.text = " %e, %e, %e" % (x,y,z)

elemCount = 0
def AddElem(n1,n2,n3,n4):
    global elemCount
    elemCount+=1
    global ELEMENTS
    newElem = xml.SubElement(ELEMENTS, 'elem')
    newElem.set('id',str(elemCount))
    newElem.text = " %d, %d, %d, %d" % (n1+1, n2+1, n3+1, n4+1)

csg_graph, last_name = parse_csg_graph(sys.argv[1])
VLast, FLast = csg_graph[last_name]
# Face normals
FN = igl.eigen.MatrixXd()
igl.per_face_normals(VLast, FLast, FN)

## Vertices
V = np.array(VLast)
V_mod = []
for i in range(V.shape[0]):
    V_mod.append((V[i][0],V[i][1],V[i][2]))
## Faces
F = np.array(FLast, dtype=np.int32)
## Face Normals
FN = np.array(FN)

# Save the file as an stl file
save_to_stl("plc.stl", V, F)

## === Making the mesh ===
mesh_info = MeshInfo()
mesh_info.set_points(V_mod)
mesh_info.set_facets(F)
options = tet.Options(switches='pRq1.2/10a10O9/7')
mesh = build(mesh_info,options)

# Save the tet mesh
mesh.write_vtk("tetmesh.vtk")

ns = []
for n in enumerate(mesh.points):
    ns.append((n[1][0],n[1][1],n[1][2]))
elems = []
for e in enumerate(mesh.elements):
    elems.append((e[1][0],e[1][1],e[1][2],e[1][3]))

# ===
test = pv.read('tetmesh.vtk')
grid = pv.UnstructuredGrid(test)

cells = grid.cells.reshape(-1, 5)[:, 1:]
cell_center = grid.points[cells].mean(1)

# extract cells below the 0 xy plane
mask = cell_center[:, 2] < -4
cell_ind = mask.nonzero()[0]
subgrid = grid.extract_cells(cell_ind)

cell_qual = subgrid.quality
print(len(cell_qual), np.mean(cell_qual))
plt.hist(cell_qual, bins=20)
plt.show()
# plot quality
#subgrid.plot(scalars=cell_qual, stitle='quality', cmap='bwr', flip_scalars=True)


for n in range(len(ns)):
    AddNode(ns[n][0],ns[n][1],ns[n][2])

for e in range(len(elems)):
    AddElem(elems[e][0],elems[e][1],elems[e][2],elems[e][3])

f = open('tmp_model.feb','w+')
f.write('<?xml version="1.0" encoding="ISO-8859-1"?>\n')
f.write(xml.tostring(ROOT, encoding="unicode"))
f.close()
