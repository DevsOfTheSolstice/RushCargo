from arcgis.gis import GIS
from arcgis.geocoding import geocode, reverse_geocode
from arcgis.geometry import Point


# ArcGIS Geocoder Class
class ArcGisGeocoder:
    # GIS
    _gis = None

    def __init__(self, arcGisApiKey: str):
        self._gis = GIS(api_key=arcGisApiKey, referer="https")


# Initialize ArcGis Geocoder
def initArcGisGeocoder(arcGisApiKey: str) -> ArcGisGeocoder:
    return ArcGisGeocoder(arcGisApiKey)
