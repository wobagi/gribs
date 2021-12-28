import argparse
import pathlib
from gribs.gribmapper import GribMapper

def cli():
    parser = argparse.ArgumentParser(description="List grib files contents to stdout")
    parser.add_argument("source", type=pathlib.Path, help="Source file")
    args = parser.parse_args()

    gm = GribMapper.from_path(str(args.source))
    gm.list()

if __name__=="__main__":
    cli()
