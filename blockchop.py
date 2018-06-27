from qgis.core import *
from qgis.gui import *
import qgis.utils
import processing
import re
from PyQt4.QtCore import *

cell_size = 2.4

layer = qgis.utils.iface.activeLayer()
selected = layer.selectedFeatures()
crs = qgis.utils.iface.activeLayer().crs().authid()



ids = []
x_maxs = []
x_mins = []
y_maxs = []
y_mins = []

for lay in selected:
    if lay.geometry().isMultipart() is False:
        print("Multipart is false... proceeding.")
    else:
        print("Found multipart feature. Must explode before running this tool. Exiting.")
        break
    
    id = lay.id()
    ids.append(id)
    print("working on: " + str(id))
    
    x_min, y_min, x_max, y_max = re.split(":|,",  lay.geometry().boundingBox().toString().replace(" ", ""))
    x_mins.append(float(x_min))
    x_maxs.append(float(x_max))
    y_mins.append(float(y_min))
    y_maxs.append(float(y_max))

extent = str(min(x_mins)) + "," + str(max(x_maxs)) + "," + str(min(y_mins)) + "," + str(max(y_maxs))
print(extent)

grid_parameters = {"TYPE":  1,
                                "EXTENT": extent,
                                "HSPACING": cell_size,
                                "VSPACING":cell_size,
                                #"HOVERLAY": 0,
                                #"VOVERLAY": 0,
                                "CRS": crs,
                                "OUTPUT": None}
                                    
grid = processing.runalg("qgis:creategrid",  grid_parameters)

#mem_grid= QgsVectorLayer(grid["OUTPUT"], "lyr_grid", "ogr")
#QgsMapLayerRegistry.instance().addMapLayer(mem_grid)

intersection_parameters = {"INPUT":  layer,
                                           "INPUT2": grid["OUTPUT"],
                                            "IGNORE_NULL": False,
                                            "OUTPUT": None}



intersect = processing.runalg("qgis:intersection", intersection_parameters)


mem_intersect = QgsVectorLayer(intersect["OUTPUT"], "lyr_intersect", "ogr")

#QgsMapLayerRegistry.instance().addMapLayer(mem_intersect)

fields_to_delete = []
fieldnames = set(["left", "right",  "top", "bottom"])
for field in mem_intersect.fields():
    if field.name() in fieldnames:
        fields_to_delete.append(mem_intersect.fieldNameIndex(field.name()))
        
mem_intersect.dataProvider().deleteAttributes(fields_to_delete)
mem_intersect.updateFields()

fid_idx = layer.fieldNameIndex('FID')
#oid_idx = layer.fieldNameIndex('OBJECTID')
fid_max_val = layer.maximumValue(fid_idx)
#oid_max_val = layer.maximumValue(oid_idx)
print(type(fid_max_val))
#print(type(oid_max_val))
fid_start = fid_max_val + 1
#oid_start = oid_max_val + 1

fid_idx_intersect = mem_intersect.fieldNameIndex('FID')
#oid_idx_intersect = mem_intersect.fieldNameIndex('OBJECTID')
cut_idx_intersect = mem_intersect.fieldNameIndex('Cut')

with edit(mem_intersect):
    for feat in mem_intersect.getFeatures():
        mem_intersect.changeAttributeValue(feat.id(), fid_idx_intersect, fid_start)
        #mem_intersect.changeAttributeValue(feat.id(), oid_idx_intersect, oid_start)
        mem_intersect.changeAttributeValue(feat.id(), cut_idx_intersect, 'y')
        
        fid_start += 1
        #oid_start += 1

#QgsMapLayerRegistry.instance().addMapLayer(mem_intersect)

features = []
for feat in mem_intersect.getFeatures():
    calc = QgsDistanceArea()
    calc.setEllipsoid('WGS84')
    calc.setEllipsoidalMode(True)
    calc.computeAreaInit()
    
    polg = feat.geometry().asPolygon()
    if len(polg) > 0:
        area = calc.measurePolygon(polg[0])
        print("area: ", str(area))
        if area > 1000:
            features.append(feat)

if not layer.isEditable():
    with edit(layer):
        layer.deleteFeatures(ids)
        layer.addFeatures(features)
else:
    layer.deleteFeatures(ids)
    layer.addFeatures(features)

