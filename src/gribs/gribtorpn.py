import sys
import pathlib
import argparse

from gribs.gribmapper import GribMapper

def convert(path, args):
    gm = GribMapper(str(path))
    gm.verbose = args.verbose
    gm.etiket = args.etiket
    if gm.is_required():
        print(f"{str(path.name)} - Converting ...")
        gm.to_rpn(target=args.target, overwrite=args.overwrite)
    else:
        print(f"{str(path.name)} -",
              f"{gm.name} @ {gm._level_type} ({gm._level}) is missing from GribMapper dictionary.")

def cli():
    parser = argparse.ArgumentParser(description="Convert grib files to rpn format")
    parser.add_argument("source", nargs="+", type=pathlib.Path, help="List of dirs and/or grib files")
    parser.add_argument("-t", "--target", type=pathlib.Path, required=True, help="Target rpn file")
    parser.add_argument("-g", "--glob", type=str, default="*.grib?", help="Glob string applied to all specified source dirs. Does not affect individual files specified explicitly. Defaults to '*.grib?' to match both grib and grib2 extension.")
    parser.add_argument("-e", "--etiket", type=str, default="G092V3N", help="Set etiket column value for resulting rpn file.")
    parser.add_argument("-o", "--overwrite", action="store_true", help="Overwrite target file if exists. Does not make much sense when processing multiple files.")
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
