import folium
from folium.plugins import MarkerCluster
import pandas as pd


Gla_map = folium.Map(location=[55.860916, -4.251433], zoom_start=13)

Gla_map.add_child(folium.LatLngPopup())

folium.Marker(
    location=[39.95, 115.33],
    popup='Mt. Hood Meadows',
    icon=folium.Icon(icon='cloud')
).add_to(Gla_map)

df = pd.read_csv('test.csv')
df0 = df.loc[df['avi'] == 0]
df1 = df.loc[df['avi'] == 1]
incidents = folium.map.FeatureGroup()

for lat, log, in zip(df0.lat, df0.log):
    incidents.add_child(
        folium.CircleMarker(
            [lat, log],
            radius = 4,
            color = 'dodgerblue',
            popup='Waiting for leasen',
            fill = True,
            fill_color = 'turquoise',
            fill_opacity = 0.4
        )
    )

for lat, log, in zip(df1.lat, df1.log):
    incidents.add_child(
        folium.CircleMarker(
            [lat, log],
            radius = 4,
            color = 'tomato',
            popup='Already on loan',
            fill = True,
            fill_color = 'silver',
            fill_opacity = 0.4
        )
    )

Gla_map = folium.Map(location=[55.860916, -4.251433], zoom_start=12)
Gla_map.add_child(incidents)
# Show where are you

folium.Circle(
    location = [55.860916, -4.251433], # the loc of People
    radius=100,
    popup='People',
    color='blue',
    fill=True,
    fill_color = 'lightskyblue',
    fill_opacity = 0.3
).add_to(Gla_map)

Gla_map.add_child(folium.LatLngPopup())  #click for the locs
#Regional bike density

# create a mark cluster object
marker_cluster = MarkerCluster().add_to(Gla_map)

# add data point to the mark cluster
# Bike data
for lat, log, in zip(df1.lat, df1.log):
    folium.Marker(
        location=[lat, log],
        icon=None,
#        popup=label,
    ).add_to(marker_cluster)

# add marker_cluster to map
Gla_map.add_child(marker_cluster)

Gla_map.save("map.html")