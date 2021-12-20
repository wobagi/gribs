import sys
import pathlib
import argparse

from gribs.gribmapper import GribMapper

RGB_G = "\u001b[32m" 
RGB_B = "\u001b[34m"
RGB_0 = "\u001b[0m"

def convert(path, args):
    CR = RGB_G if args.color else RGB_0
    CG = RGB_B if args.color else RGB_0
    C0 = RGB_0

    for gm in GribMapper.from_path(str(path)):
        gm.etiket = args.etiket
        if gm.is_recognized():
            print(f"{CR}... {str(path.name)} - Converting {gm.gribvar} @ {gm._level_type} ({gm._level}){C0}")
            if not args.dry:
                gm.to_rpn(target=args.target,
                          overwrite=args.overwrite,
                          ip_oldstyle=args.oldstyle,
                          verbose=args.verbose)
        else:
            print(f"{CG}??? {str(path.name)} -",
                f"{gm.gribvar} @ {gm._level_type} ({gm._level}) is missing from GribMapper dictionary.{C0}")

def cli():
    parser = argparse.ArgumentParser(description="Convert grib files to rpn format")
    parser.add_argument("source", nargs="+", type=pathlib.Path, help="List of dirs and/or grib files")
    parser.add_argument("-t", "--target", type=pathlib.Path, required=True, help="Target rpn file")
    parser.add_argument("-g", "--glob", type=str, default="*.grib?", help="Glob string applied to all specified source dirs. Does not affect individual files specified explicitly. Defaults to '*.grib?' to match both grib and grib2 extension.")
    group1 = parser.add_argument_group('fstd options')
    group1.add_argument("-e", "--etiket", type=str, default="G092V3N", help="Set etiket column value for resulting rpn file.")
    group1.add_argument("-o", "--overwrite", action="store_true", help="Overwrite target file if exists. Does not make much sense when processing multiple files.")
    group1.add_argument("--oldstyle", action="store_true", help="Get IP1 code values in oldstyle format.")
    group1.add_argument("-v", "--verbose", action="store_true", help="Display FSTD output")
    group2 = parser.add_argument_group('other options')
    group2.add_argument("-d", "--dry", action="store_true", help="Dry run with no actual file saving")
    group2.add_argument("-c", "--color", action="store_true", help="Use color for messages")
    args = parser.parse_args()

    for pt in args.source:
        if pt.is_file():
            convert(pt, args)
        elif pt.is_dir():
            for f in sorted(pt.glob(args.glob)):
                convert(f, args)

if __name__=="__main__":
    cli()
