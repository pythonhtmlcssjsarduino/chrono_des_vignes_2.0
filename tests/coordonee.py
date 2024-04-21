import folium
from jinja2 import Template

m = folium.Map(max_zoom=22,location=(46.546753, 6.449788))
p=folium.LatLngPopup().add_to(m)
p._template = Template(
        """
            {% macro script(this, kwargs) %}
                function latLngPop(e) {
                    window.location.href="map.html?lat="+e.latlng.lat.toFixed(4)+"&lng="+e.latlng.lng.toFixed(4)+"&zoomlevel="+{{ this._parent.get_name() }}.getZoom()+"&latmap="+{{ this._parent.get_name() }}.getCenter().lat+"&lngmap="+{{ this._parent.get_name() }}.getCenter().lng
                    }
                {{this._parent.get_name()}}.on('click', latLngPop);
            {% endmacro %}
            """
    )  # noqa

popup = folium.Popup('coucou')
popup._template = Template("""
        var {{this.get_name()}} = L.popup({{ this.options|tojson }});
        {{ this._parent.get_name() }}.once('click', function() {window.location.href='map.html'})
        """)

marker = folium.Marker(
      location=(-12,-38),
      popup=popup
   ).add_to(m)

m.save('coordonee.html')