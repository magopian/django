# Getting the normal admin routines, classes, and `site` instance.
from django.contrib.admin import autodiscover, site, AdminSite, ModelAdmin, StackedInline, TabularInline, HORIZONTAL, VERTICAL

# Geographic admin options classes and widgets.
from django.contrib.gis.admin.options import GeoModelAdmin

try:
    from django.contrib.gis.admin.options import OSMGeoAdmin
    HAS_OSM = True
except ImportError:
    HAS_OSM = False
