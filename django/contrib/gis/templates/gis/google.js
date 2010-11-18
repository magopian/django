{% extends 'gis/widget.js' %}
{% block base_layer %}new OpenLayers.Layer.Google("Google Streets", {numZoomLevels: 20});{% endblock %}
