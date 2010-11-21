from django.contrib.admin import autodiscover, site, AdminSite, ModelAdmin, StackedInline, TabularInline, HORIZONTAL, VERTICAL

from django.contrib.gis.admin.options import GeoModelAdmin

try:
    from django.contrib.gis.admin.options import OSMGeoAdmin
    HAS_OSM = True
except ImportError:
    HAS_OSM = False
