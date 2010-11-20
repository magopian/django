from django.forms import *
from django.contrib.gis.forms.fields import (GeometryField,
                                             GeometryCollectionField,
                                             PointField,
                                             MultiPointField,
                                             LineStringField,
                                             MultiLineStringField,
                                             PolygonField,
                                             MultiPolygonField)
from django.contrib.gis.forms.widgets import (GeometryWidget,
                                              GeometryCollectionWidget,
                                              PointWidget,
                                              MultiPointWidget,
                                              LineStringWidget,
                                              MultiLineStringWidget,
                                              PolygonWidget,
                                              MultiPolygonWidget)

try:
    from django.contrib.gis.forms.widgets import OSMWidget, GMapWidget
    HAS_OSM = True
    HAS_GMAP = True
except ImportError:
    HAS_OSM = False
    HAS_GMAP = False
