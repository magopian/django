from django import forms
from django.conf import settings
from django.contrib.gis import gdal
from django.contrib.gis.geos import GEOSGeometry, GEOSException
from django.template import loader
from django.utils import translation


class GeometryWidget(forms.Textarea):
    """
    The base class for rich geometry widgets. Custom widgets may be
    obtained by subclassing this base widget.
    """
    # Public API
    map_template = 'gis/widget.html'
    map_width = 600
    map_height = 400
    color = 'ee9900'
    opacity = 0.4
    default_lon = 2 # 0
    default_lat = 47 # 0
    default_zoom = 5 # 4
    point_zoom = 14
    srid = 4326

    modifiable = True
    scrollable = True
    display_wkt = False
    layerswitcher = True

    # Semi-public, doesn't apply for google maps for instance
    wms_url = 'http://labs.metacarta.com/wms/vmap0'
    wms_layer = 'basic'
    wms_name = 'OpenLayers WMS'

    # Internal stuff, not supposed to be overriden
    is_point = False
    is_linestring = False
    is_polygon = False
    is_collection = False
    collection_type = 'None'

    def __init__(self, *args, **kwargs):
        super(GeometryWidget, self).__init__(*args, **kwargs)
        attrs = kwargs.pop('attrs', {})

        self.params = {
            'map_width': attrs.pop('map_width', self.map_width),
            'map_height': attrs.pop('map_height', self.map_height),
            'color': attrs.pop('color', self.color),
            'opacity': attrs.pop('opacity', self.opacity),
            'default_lon': attrs.pop('default_lon', self.default_lon),
            'default_lat': attrs.pop('default_lat', self.default_lat),
            'default_zoom': attrs.pop('default_zoom', self.default_zoom),
            'point_zoom': attrs.pop('point_zoom', self.point_zoom),
            'srid': attrs.pop('srid', self.srid),
            'scrollable': attrs.pop('scrollable', self.scrollable),

            'wms_url': self.wms_url,
            'wms_name': self.wms_name,
            'wms_layer': self.wms_layer,
            'geom_type': gdal.OGRGeomType(self.geom_type),
            'layerswitcher': self.layerswitcher,

            'modifiable': self.modifiable,
            'display_wkt': self.display_wkt,

            'is_polygon': self.is_polygon,
            'is_linestring': self.is_linestring,
            'is_point': self.is_point,
            'is_collection': self.is_collection,
        }

    class Media:
        js = ('http://openlayers.org/api/2.10/OpenLayers.js',)

    def render(self, name, value, attrs=None):
        if attrs:
            self.params.update(attrs)

        # If a string reaches here (via a validation error on another
        # field) then just reconstruct the Geometry.
        if isinstance(value, basestring):
            try:
                value = GEOSGeometry(value)
            except (GEOSException, ValueError):
                value = None

        if value and value.geom_type.upper() != self.geom_type:
            value = None

        # Constructing the dictionary of the map options
        self.params['map_options'] = self.map_options()

        # Defaulting the WKT value to a blank string
        wkt = ''
        if value:
            srid = self.params['srid']
            if value.srid != srid:
                try:
                    ogr = value.ogr
                    ogr.transform(srid)
                    wkt = ogr.wkt
                except gdal.OGRException:
                    pass  # wkt left as an empty string
            else:
                wkt = value.wkt

        context = {
            'module': 'map_%s' % name.replace('-', '_'),
            'name': name,
            'wkt': wkt,
            'ADMIN_MEDIA_PREFIX': settings.ADMIN_MEDIA_PREFIX,
            'LANGUAGE_BIDI': translation.get_language_bidi(),
        }
        context.update(self.params)
        from pprint import pprint
        pprint(context)
        return loader.render_to_string(self.map_template, context)

    def map_options(self):
        "Builds the map options hash for the OpenLayers template."

        def ol_bounds(extent):
            return 'new OpenLayers.Bounds(%s)' % str(extent)

        def ol_projection(srid):
            return 'new OpenLayers.Projection("EPSG:%s")' % srid

        # parameter name, OpenLayers counterpart, type of variable
        map_types = [
            ('srid', 'projection', 'srid'),
            ('display_srid', 'displayProjection', 'srid'),
            ('units', 'units', str),
            ('max_resolution', 'maxResolution', float),
            ('max_extent', 'maxExtent', 'bounds'),
            ('num_zoom', 'numZoomLevels', int),
            ('max_zoom', 'maxZoomLevels', int),
            ('min_zoom', 'minZoomLevel', int),
        ]

        # Building the map options hash.
        map_options = {}
        for param_name, js_name, option_type in map_types:
            if self.params.get(param_name, False):
                if option_type == 'srid':
                    value = ol_projection(self.params[param_name])
                elif option_type == 'bounds':
                    value = ol_bounds(self.params[param_name])
                elif option_type in (float, int):
                    value = self.params[param_name]
                elif option_type in (str,):
                    value = '"%s"' % self.params[param_name]
                else:
                    raise TypeError, "Unrecognized option type: '%s'" % option_type
                map_options[js_name] = value
        return map_options


class PointWidget(GeometryWidget):
    is_point = True
    geom_type = 'POINT'


class MultiPointWidget(PointWidget):
    is_collection = True
    collection_type = 'MultiPoint'
    geom_type = 'MULTIPOINT'


class LineStringWidget(GeometryWidget):
    is_linestring = True
    geom_type = 'LINESTRING'


class MultiLineStringWidget(LineStringWidget):
    is_collection = True
    collection_type = 'MultiLineString'
    geom_type = 'MULTILINESTRING'


class PolygonWidget(GeometryWidget):
    is_polygon = True
    geom_type = 'POLYGON'


class MultiPolygonWidget(PolygonWidget):
    is_collection = True
    collection_type = 'MultiPolygon'
    geom_type = 'MULTIPOLYGON'


if gdal.HAS_GDAL:
    class OSMWidget(GeometryWidget):
        map_template = 'gis/osm.html'
        num_zoom = 20
        srid = 900913
        max_extent = '-20037508,-20037508,20037508,20037508'
        max_resolution = '156543.0339'
        point_zoom = num_zoom - 6
        units = 'm'

        class Media:
            js = ('http://www.openstreetmap.org/openlayers/OpenStreetMap.js',)


    class GMapWidget(GeometryWidget):
        map_template = 'gis/google.html'
        num_zoom = 20
        srid = 900913
        point_zoom = num_zoom - 6
        units = 'm'

        class Media:
            js = (
                'http://openlayers.org/dev/OpenLayers.js',
                'http://maps.google.com/maps/api/js?sensor=false',
            )
