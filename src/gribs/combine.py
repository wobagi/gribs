#!/usr/bin/env python3

import os
import sys
import pathlib
import argparse
import numpy as np
import fstd2nc
import rpnpy.librmn.all as rmn
from eccodes import GribFile, GribMessage
from tqdm import tqdm


class Config():
    VARS = {'Specific humidity': ('HU', 1, 0),           # kg/kg -> kg/kg
        'U component of wind': ('UU', 1.9438, 0),    # m/s -> kt
        'Pressure reduced to MSL': ('PN', 0.01, 0),  # Pa  -> hPa
        'Sea surface temperature': ('TM', 1, 0),     # K -> K
        'Temperature': ('TT', 1, -273.15),           # K -> C
        'Surface pressure': ('P0', 0.01, 0),         # Pa  -> hPa
        'V component of wind': ('VV', 1.9438, 0),    # m/s -> kt
        'Snow depth': ('SD', 100, 0),                # m -> cm
        'Geopotential Height': ('GZ', 0.1, 0)        # gpm -> dam
       }

       @staticmethod
       def convert_unit(value, var):
           pass

class GribCombine():
    def __init__(self, path):
        self._path = path
        self._grib_msg = None
        self._levels = {}

    @property
    def levels(self):
        return self._levels

    @levels.setter
    def levels(self, values):
        if isinstance(values, list) or isinstance(values, tuple):
            self._levels = tuple(values)
        else:
            raise Exception("Specify levels as a list/tuple of values")

