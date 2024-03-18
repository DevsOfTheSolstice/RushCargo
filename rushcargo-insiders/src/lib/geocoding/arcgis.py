from arcgis.gis import GIS
from arcgis.geocoding import geocode, reverse_geocode
from arcgis.geometry import Point


# ArcGIS Geocoder Class
class Geocoder:
    # GIS
    _gis = None

    def __init__(self, arcGisApiKey: str):
        self._gis = GIS(api_key=arcGisApiKey)

    # Find Latitude and Longitude for a Given Address
    def getCountry(self, address: str):
        geocodeResult = geocode(address=address, category="City")

        return geocodeResult


# Initialize Geocoder
def initGeocoder(arcGisApiKey: str) -> Geocoder:
    return Geocoder(arcGisApiKey)
