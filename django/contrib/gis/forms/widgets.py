from django import forms
from django.conf import settings
from django.contrib.gis import gdal, geos
from django.template import loader
from django.utils import translation


class GeometryWidget(forms.Textarea):
    """
    The base class for rich geometry widgets. Custom widgets may be
    obtained by subclassing this base widget.
    """
    # Public API
    color = 'ee9900'
    default_lon = 0
    default_lat = 0
    default_zoom = 4
    display_srid = False
    display_wkt = False
    layerswitcher = True
    map_width = 600
    map_height = 400
    map_srid = 4326
    map_template = 'gis/widget.html'
    max_extent = False
    max_resolution = False
    max_zoom = False
    min_zoom = False
    modifiable = True
    mouse_position = True
    num_zoom = 18
    opacity = 0.4
    point_zoom = num_zoom - 6
    scale_text = True
    scrollable = True
    units = False
    wms_url = 'http://labs.metacarta.com/wms/vmap0'
    wms_layer = 'basic'
    wms_name = 'OpenLayers WMS'

    # Deprecated?
    debug = False

    # Internal stuff, not supposed to be overriden
    is_point = False
    is_linestring = False
    is_polygon = False
    is_collection = False
    collection_type = 'None'
    geom_type = 'GEOMETRY'

    map_attrs = (
        'color', 'default_lon', 'default_lat', 'default_zoom', 'display_srid',
        'display_wkt', 'layerswitcher', 'map_width', 'map_height', 'map_srid',
        'map_template', 'max_extent', 'max_resolution', 'max_zoom', 'min_zoom',
        'modifiable', 'mouse_position', 'num_zoom', 'opacity', 'point_zoom',
        'scale_text', 'scrollable', 'units', 'wms_url', 'wms_layer',
        'wms_name',
    )

    def __init__(self, *args, **kwargs):
        super(GeometryWidget, self).__init__(*args, **kwargs)
        attrs = kwargs.pop('attrs', {})
        self.params = {}

        for key in ('is_polygon', 'is_linestring', 'is_point',
                    'is_collection', 'collection_type'):
            self.params[key] = getattr(self, key)

        for key in self.map_attrs:
            self.params[key] = attrs.pop(key, getattr(self, key))
        self.params['geom_type'] = gdal.OGRGeomType(self.geom_type)
        if self.geom_type == 'GEOMETRYCOLLECTION':
            self.params['geom_type'] = 'Collection'

    class Media:
        js = ('http://openlayers.org/api/2.10/OpenLayers.js',)

    def render(self, name, value, attrs=None):
        if attrs:
            self.params.update(attrs)

        # If a string reaches here (via a validation error on another
        # field) then just reconstruct the Geometry.
        if isinstance(value, basestring):
            try:
                value = geos.GEOSGeometry(value)
            except (geos.GEOSException, ValueError):
                value = None

        if value and value.geom_type.upper() != self.geom_type and self.geom_type != 'GEOMETRY':
            value = None

        # Constructing the dictionary of the map options
        self.params['map_options'] = self.map_options()

        # Defaulting the WKT value to a blank string
        wkt = ''
        if value:
            srid = self.params['map_srid']
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
                    raise TypeError("Unrecognized option type: '%s'" % option_type)
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


class GeometryCollectionWidget(GeometryWidget):
    is_collection = True
    collection_type = 'Any'
    geom_type = 'GEOMETRYCOLLECTION'


if gdal.HAS_GDAL:
    class OSMWidget(GeometryWidget):
        map_srid = 900913
        map_template = 'gis/osm.html'
        max_extent = '-20037508,-20037508,20037508,20037508'
        max_resolution = '156543.0339'
        num_zoom = 20
        point_zoom = num_zoom - 6
        units = 'm'

        class Media:
            js = ('http://www.openstreetmap.org/openlayers/OpenStreetMap.js',)

    class GMapWidget(GeometryWidget):
        map_srid = 900913
        map_template = 'gis/google.html'
        num_zoom = 20
        point_zoom = num_zoom - 6
        units = 'm'

        class Media:
            js = (
                'http://openlayers.org/dev/OpenLayers.js',
                'http://maps.google.com/maps/api/js?sensor=false',
            )
