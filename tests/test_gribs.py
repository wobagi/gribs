#!/usr/bin/env python3

import unittest
from gribs.combine import GribCombine

class TestFSTDMeta(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_grib_combiner_init_empty(self):
        gc = GribCombine("path")
        self.assertTrue(gc)

if __name__ == '__main__':
    unittest.main()