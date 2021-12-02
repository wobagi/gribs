#!/usr/bin/env python3

import re
import math
import argparse
import datetime as dt

from os import stat
from glob import glob

from gribs.gribmapper import GribMapper

def diff(dir1, dir2):
    cmc_files1 = [f for f in dir1.glob("*.grib?")]
    cmc_files2 = [f for f in dir2.glob("*.grib?")]

    # "CMC_glb_WTMP_SFC_0_latlon.15x.15_2021120200_P000.grib2"

    stems1 = [re.match("(CMC.+)_\d{10}_.+\.grib2", name).group(1) for name in cmc_files1]
    stems2 = [re.match("(CMC.+)_\d{10}_.+\.grib2", name).group(1) for name in cmc_files2]

    dif1 = sorted(set(stems1)-set(stems2))
    dif2 = sorted(set(stems2)-set(stems1))

    print(f"Dir 1:\n{'\n'.join(dif1)}")
    print(f"Dir 2:\n{'\n'.join(dif2)}")

def cli():
    parser = argparse.ArgumentParser(description="Diff two dirs in terms of CMC grib file types")
    parser.add_argument("dir1", type=pathlib.Path, help="First dir")
    parser.add_argument("dir2", type=pathlib.Path, help="Second dir")
    args = parser.parse_args()

    diff(args.dir1, args.dir2)

if __name__=="__main__":
    cli()
