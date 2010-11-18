from django.conf import settings
from django.contrib.admin import ModelAdmin
from django.contrib.gis.forms.widgets import *
from django.contrib.gis.gdal import OGRGeomType
from django.contrib.gis.db import models

class GeoModelAdmin(ModelAdmin):
    """
    The administration options class for Geographic models. Map settings
    may be overloaded from their defaults to create custom maps.
    """
    # The default map settings that may be overloaded -- still subject
    # to API changes.
    default_lon = 0
    default_lat = 0
    default_zoom = 4
    display_wkt = False
    display_srid = False
    extra_js = []
    num_zoom = 18
    max_zoom = False
    min_zoom = False
    units = False
    max_resolution = False
    max_extent = False
    modifiable = True
    mouse_position = True
    scale_text = True
    layerswitcher = True
    scrollable = True
    map_width = 600
    map_height = 400
    map_srid = 4326
    map_template = 'gis/admin/openlayers.html'
    openlayers_url = 'http://openlayers.org/api/2.10/OpenLayers.js'
    point_zoom = num_zoom - 6
    wms_url = 'http://labs.metacarta.com/wms/vmap0'
    wms_layer = 'basic'
    wms_name = 'OpenLayers WMS'
    debug = False
