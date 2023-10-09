import folium
from jinja2 import Template
# Make an empty map
m = folium.Map(location=[180,0], tiles="OpenStreetMap", zoom_start=2)

popup = folium.Popup()
popup._template = Template("""
        var {{this.get_name()}} = L.popup({{ this.options|tojson }});
        {{ this._parent.get_name() }}.once('click', function() {window.location.href='https://ch.ch'})
        """)

marker = folium.Marker(
      location=(-12,-38),
      popup=popup
   ).add_to(m)

m.save('map.html')