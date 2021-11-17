#!/usr/bin/env python3

import unittest
from eccodes import GribFile
from gribs.units import Unit
from gribs.gribmapper import GribMapper

class TestFSTDMeta(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_grib_combiner_init_empty(self):
        gf = GribFile("/Users/voitek/Projects/Meteo/data/grib/2021102600/CMC_glb_ABSV_ISBL_200_latlon.15x.15_2021102600_P000.grib2")
        gc = GribMapper("path")
        self.assertTrue(gc)

if __name__ == '__main__':
    unittest.main()