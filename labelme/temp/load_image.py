import PIL
import io 
import base64
import contextlib
import io
import json
import os.path as osp
import time 
import PIL.Image

from labelme import __version__
from labelme.logger import logger
from labelme import PY2
from labelme import QT4
from labelme import utils

from qtpy import QtGui
import cv2 

def load_image_file(filename):
    try:
        image_pil = PIL.Image.open(filename)
    except IOError:
        logger.error("Failed opening image file: {}".format(filename))
        return

    # apply orientation to image according to exif
    image_pil = utils.apply_exif_orientation(image_pil)

    with io.BytesIO() as f:
        ext = osp.splitext(filename)[1].lower()
        if PY2 and QT4:
            format = "PNG"
        elif ext in [".jpg", ".jpeg"]:
            format = "JPEG"
        else:
            format = "PNG"
        image_pil.save(f, format=format)
        f.seek(0)
        return f.read()



filename = r"C:/BaiduNetdisk/Day20210624/procuct(25)-SEQUENCE_B-rawImge.bmp"
t1 = time.time()
#imagedata = load_image_file(filename)
imagedata = cv2.imread(filename)
t2 = time.time()
tt = t2 -t1
print(type(imagedata))
image = QtGui.QImage.fromData(imagedata)
print(tt)
print("Done.")