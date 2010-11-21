from django.contrib.admin import ModelAdmin
from django.contrib.gis import forms
from django.contrib.gis.db import models


class GeoModelAdmin(ModelAdmin):
    widget = forms.GeometryWidget

    def formfield_for_dbfield(self, db_field, **kwargs):
        if isinstance(db_field, models.GeometryField):
            request = kwargs.pop('request', None)
            kwargs['widget'] = self.get_map_widget(db_field)
            return db_field.formfield(**kwargs)
        return super(GeoModelAdmin, self).formfield_for_dbfield(db_field,
                                                                **kwargs)

    def get_map_widget(self, db_field):
        widget = db_field.formfield().widget
        for param in widget.map_attrs:
            if hasattr(self, param):
                setattr(self.widget, param, getattr(self, param))

        class MapWidget(self.widget):
            geom_type = widget.geom_type
            is_point = widget.is_point
            is_linestring = widget.is_linestring
            is_polygon = widget.is_polygon
            is_collection = widget.is_collection
            collection_type = widget.collection_type

        return MapWidget


from django.contrib.gis import gdal
if gdal.HAS_GDAL:
    class OSMGeoAdmin(GeoModelAdmin):
        widget = forms.OSMWidget
