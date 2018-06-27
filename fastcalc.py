##value=string

from qgis.core import *
from qgis.gui import *
import qgis.utils
import processing
import re
from PyQt4.QtCore import *

valid_hires_ccap_values = [0, 2, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23,24, 25]

layer = qgis.utils.iface.activeLayer()
selected = layer.selectedFeatures()

old_idx = layer.fieldNameIndex('CCAP')
new_idx = layer.fieldNameIndex('CCAP_2016')

ids = []
for sel in selected:
    ids.append(sel.id())

request = QgsFeatureRequest().setFilterFids(ids)
for feat in layer.getFeatures(request):
    if value.upper() == 'C':
        old_val = feat.attributes()[old_idx]
        print(r"found old CCAP field, updating...")
        if not layer.isEditable():
            with edit(layer):
                layer.changeAttributeValue(feat.id(), new_idx, old_val)
        else:
            layer.changeAttributeValue(feat.id(), new_idx, old_val)    
    else:
        if int(value) in valid_hires_ccap_values:
            print(r"New value specified. Using that.")
            if not layer.isEditable():
                with edit(layer):
                    layer.changeAttributeValue(feat.id(), new_idx, int(value))
            else:
                layer.changeAttributeValue(feat.id(), new_idx, int(value))
        else:
            print(str(value), "is not a valid C-CAP value")

print("done")