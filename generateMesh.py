#!/usr/bin/python3
import sys, os
import numpy as np
import math
import xml.etree.ElementTree as xml

# arg 1 = thickness
# arg 2 = angle
# arg 3 = box side thickness
# arg 4 = box bottom thickness
box_side = None
box_bottom = None
if len(sys.argv) == 5:
    box_side = float(sys.argv[3])
    box_bottom = float(sys.argv[4])
elif len(sys.argv) != 3:
    print("Usage: ./generateGeometry thickness angle [box_side_thickness] [box_bottom_thickness]")
    sys.exit(1)
thickness = float(sys.argv[1])
angle = int(sys.argv[2])


ROOT = xml.Element('data')

arm = xml.SubElement(ROOT,'solid')
arm.set('name','arm')
arm.set('shape','cube')
xml.SubElement(arm,'size').text = "[50,10,%d]" % (thickness+5.0) #wedge is 5mm
xml.SubElement(arm,'center').text = "[0.0,0.0,%.2f]" % ((thickness+5.0)/-2.0)
xml.SubElement(arm, 'scale').text = "1"

wedge = xml.SubElement(ROOT,'solid')
wedge.set('name','wedge')
wedge.set('shape','prism')
xml.SubElement(wedge, 'center').text = "[0.0,0.0,-5]"
xml.SubElement(wedge, 'length').text = "10"
xml.SubElement(wedge, 'height').text = "5"
xml.SubElement(wedge, 'angle').text = str(angle)

cast = xml.SubElement(ROOT,'binary_op')
cast.set('name','cast')
cast.set('type','difference')
xml.SubElement(cast, 'operand').text = "arm"
xml.SubElement(cast, 'operand').text = "wedge"

if box_side != None:
    box = xml.SubElement(ROOT,'solid')
    box.set('name','box')
    box.set('shape','cube')
    xml.SubElement(box,'size').text = "[%.2f,%.2f,%.2f]" % (50+box_side*2,
                                                            10+box_bottom*2,
                                                            box_bottom+thickness+5) #wedge is 5mm
    xml.SubElement(box,'center').text = "[0.0,0.0,%.2f]" % ((thickness+5.0)/-2.0+box_bottom/2.0)
    xml.SubElement(box, 'scale').text = "1"

    arm.find('size').text = "[50,10,%d]" % (thickness+6) #wedge is 5mm
    arm.find('center').text = "[0.0,0.0,%.2f]" % ((thickness+6)/-2.0)

    mold = xml.SubElement(ROOT,'binary_op')
    mold.set('name','mold')
    mold.set('type','difference')
    xml.SubElement(mold, 'operand').text = "box"
    xml.SubElement(mold, 'operand').text = "cast"

f = open('tmp_model.xml','wb+')
f.write(xml.tostring(ROOT))
f.close()
