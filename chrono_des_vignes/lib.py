import requests
from math import acos, sin, radians, cos
from time import time
from datetime import timedelta

def midpoint(latlng1, latlng2):
    lat = (latlng1[0]+latlng2[0])/2
    lng = (latlng1[1]+latlng2[1])/2
    return (lat, lng)

def get_points_elevation(points:list[tuple[float, float]]) -> list[dict[str, float]]:
    """Get the elevation of a list of points using the open-elevation API

    Args:
        points (list[tuple[float, float]]): A list of points as tuples of latitude and longitude in decimal degrees

    Returns:
        list[dict[str, float]]: A list of dictionaries with keys 'latitude', 'longitude' and 'elevation' in meters
    """
    start = time()
    if len(points) == 0:
        return []
    ic('get_points_elevation', points)
    data = {'locations':[{'latitude':float(lat), 'longitude':float(lng)} for lat, lng in points]}
    url = 'https://api.open-elevation.com/api/v1/lookup'
    try:
        response = requests.post(url, json=data, timeout=1)
    except requests.exceptions.ReadTimeout as e:
        ic(e)
        ic(time() - start, 'get_points_elevation')
    else:
        ic(response.status_code, response)
        ic(time() - start, 'get_points_elevation')
        if response.status_code == 200:
            ic(response.json())
            return response.json()['results'] # [{'latitude':float, 'longitude':float, 'elevation':float}, ...]
        else :
            ic('open-elevation api error', response.status_code)

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

def format_timedelta(delta: timedelta) -> str:
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    days = delta.days

    return f"{f'{days} jours, ' if days>0 else ''}{hours:02}:{minutes:02}:{seconds:02}"