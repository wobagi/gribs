#!/usr/bin/env python3

import re
import math
from pathlib import Path
import argparse
import datetime as dt

from os import stat
from glob import glob

from gribs.gribmapper import GribMapper

_n = "\n"

def list_gribs(dir):
    grib_files = list()
    if dir.is_dir():
        grib_files = [str(f) for f in dir.glob("*.grib?")]
        if not grib_files:
            raise Exception(f"Dir {dir} contains no grib files.")
    else:
        raise ValueError(f"Dir {dir} not found")
    return grib_files

def stem(name):
    return re.match(".+(CMC.+)_\d{10}_", name).group(1)

def diff(dir1, dir2):
    cmc_files1 = list_gribs(dir1)
    cmc_files2 = list_gribs(dir2)

    stems1 = [stem(name) for name in cmc_files1]
    stems2 = [stem(name) for name in cmc_files2]

    if set(stems1)==set(stems2):
        print("Both directories contain matching layers.")
    else:
        dif1 = sorted(set(stems1)-set(stems2))
        dif2 = sorted(set(stems2)-set(stems1))
        dc = len(dif1) + len(dif2)
        print(f"Found {dc} differences between directories.")
        if dif1:
            print(f"- Dir 1 unmatched layers:{_n}{_n.join(dif1)}")
        if dif2:
            print(f"- Dir 2 unmatched layers:{_n}{_n.join(dif2)}")

def cli():
    parser = argparse.ArgumentParser(description="Diff two dirs in terms of CMC grib layers")
    parser.add_argument("dir1", type=Path, help="First dir")
    parser.add_argument("dir2", type=Path, help="Second dir")
    args = parser.parse_args()

    diff(args.dir1, args.dir2)

if __name__=="__main__":
    cli()
