import folium
from jinja2 import Template

m = folium.Map(max_zoom=22)
p=folium.LatLngPopup().add_to(m)
p._template = Template(
        """
            {% macro script(this, kwargs) %}
                var {{this.get_name()}} = L.popup();
                function latLngPop(e) {
                    {{this.get_name()}}
                        .setLatLng(e.latlng)
                        .setContent("<a href='http://127.0.0.1:5500/map.html?lat="+e.latlng.lat.toFixed(4)+"&lng="+e.latlng.lng.toFixed(4)+"'>click</a>")
                        .openOn({{this._parent.get_name()}});
                    }
                {{this._parent.get_name()}}.on('click', latLngPop);
            {% endmacro %}
            """
    )  # noqa
m.save('map.html')