import urllib.request
import socket
import math
from PyQt5 import QtGui

DEF_MAPS_SIZE = 640


def get_map(center, zoom, size=(DEF_MAPS_SIZE, DEF_MAPS_SIZE), scale=1,
            markers=None, path=None):
    socket.setdefaulttimeout(1)

    base_url = "http://maps.google.com/maps/api/staticmap?key=" \
               "AIzaSyCS1z_324W8CSzNP6nFXHTK2x40PIW5bM8&center={}&zoom={}" \
               "&size={}&scale={}"
    center_string = "{},{}".format(center[0], center[1])
    zoom_string = "{}".format(zoom)
    size_string = "{}x{}".format(size[0], size[1])
    scale_string = "{}".format(scale)
    url = base_url.format(center_string, zoom_string, size_string,
                          scale_string)
    if markers:
        marker_base = "&markers="
        for marker in markers:
            marker_string = "{},{}".format(marker[0], marker[1])
            marker_base += marker_string + "|"
        url += marker_base[:-1]
    if path:
        path_base = "&path="
        for point in path:
            path_string = "{},{}".format(point[0], point[1])
            path_base += path_string + "|"
        url += path_base[:-1]

    try:
        urllib.request.urlretrieve(url, "/tmp/tmp_data.bin")
    except:
        return QtGui.QPixmap("error.bin")

    return QtGui.QPixmap("/tmp/tmp_data.bin")


def pix_to_deg_lat(pix, zoom, current_lat):
    return ((-math.cos(math.radians(current_lat)) * 360 * pix) /
            (256 * math.pow(2, zoom)))


def pix_to_deg_long(pix, zoom):
    return (360 * pix) / (256 * math.pow(2, zoom))


def deg_lat_to_pix(deg, zoom, current_lat):
    return ((256 * math.pow(2, zoom) * deg) /
            (-math.cos(math.radians(current_lat)) * 360))


def deg_long_to_pix(deg, zoom):
    return (256 * math.pow(2, zoom) * deg) / 360
