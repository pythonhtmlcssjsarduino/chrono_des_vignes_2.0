import requests
from math import acos, sin, radians, cos


def midpoint(latlng1, latlng2):
    lat = (latlng1[0]+latlng2[0])/2
    lng = (latlng1[1]+latlng2[1])/2
    return (lat, lng)

def get_points_elevation(points:list[tuple[float]]):
    if len(points) == 0:
        return []
    data = {'locations':[{'latitude':float(lat), 'longitude':float(lng)} for lat, lng in points]}
    url = 'https://api.open-elevation.com/api/v1/lookup'
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()['results']

def calc_points_dist(lat1, lng1, lat2, lng2):
    'return the spherical dist of the two points in km'
    return acos((sin(radians(lat1)) * sin(radians(lat2))) + (cos(radians(lat1)) * cos(radians(lat2))) * (cos(radians(lng2) - radians(lng1)))) * 6371


def deg_to_dms(deg):
    """Convert from decimal degrees to degrees, minutes, seconds."""
    m, s = divmod(abs(deg)*3600, 60)
    d, m = divmod(m, 60)
    if deg < 0:
        d = -d
    d, m = int(d), int(m)
    return d, m, s
