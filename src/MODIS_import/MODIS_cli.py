import argparse
import sys

from MODIS_import.MODIS_download_conversion import download_conversion_nc

def main():
    # Create the parser
    parser = argparse.ArgumentParser()
    # Add an argument
    parser.add_argument("-f", "--configfile",
                        default=None, type=str, required=True, dest='f',
                        help="Path to MODIS_import TOML configuration file.")

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    else:
        args = parser.parse_args()
        download_conversion_nc(args.configfile)