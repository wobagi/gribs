import sys
import pathlib
import argparse

from gribs.gribmapper import GribMapper

def convert(path, args):
    gm = GribMapper(str(path))
    gm.verbose = args.verbose
    gm.etiket = "G0928V3N"
    if gm.is_required():
        print(f"{str(path.name)} - Converting ...")
        gm.to_rpn(target=args.target, overwrite=args.overwrite)
    else:
        print(f"{str(path.name)} -",
              f"{gm.name} @ {gm._level_type} ({gm._level}) is missing from GribMapper dictionary.")

def cli():
    parser = argparse.ArgumentParser(description="Convert grib files to rpn format")
    parser.add_argument("source", nargs="+", type=pathlib.Path, help="A dir or a single grib file")
    parser.add_argument("--target", "-t", type=pathlib.Path, required=True, help="Target rpn file")
    parser.add_argument("--glob", "-g", type=str, default="*.grib?", help="Glob string. Defaults to '*.grib?'")
    parser.add_argument("-o", "--overwrite", action="store_true", help="Overwrite target if exists")
    parser.add_argument("-v", "--verbose", action="store_true", help="Display FSTD output")
    args = parser.parse_args()

    for pt in args.source:
        if pt.is_file():
            convert(pt, args)
        elif pt.is_dir():
            for f in sorted(pt.glob(args.glob)):
                convert(f, args)

if __name__=="__main__":
    cli()
