import argparse
import pathlib
from gribs.gribmapper import GribMapper

def cli():
    parser = argparse.ArgumentParser(description="Convert grib files to rpn format")
    parser.add_argument("--source", "-s", type=pathlib.Path, required=True, help="Source directory")
    parser.add_argument("--target", "-t", type=pathlib.Path, required=True, help="Target rpn file")
    parser.add_argument("-o", "--overwrite", action="store_true", help="Overwrite target if exists")
    parser.add_argument("-v", "--verbose", action="store_true", help="Display FSTD output")
    args = parser.parse_args()

    for f in args.source.glob("*.grib2"):
        gm = GribMapper(str(f))
        gm.verbose = args.verbose
        gm.etiket = "G0928V3N"
        if gm.is_required():
            print(f"Converting {str(f.name)}")
            gm.to_rpn(target=args.target, overwrite=args.overwrite)

if __name__=="__main__":
    cli()
