# __main__.py is called on python -m fhirbuild

import sys
import argparse
import csv
from fhirbuild.csvtofhir import csv_to_specimen, csv_to_observation, writeout

# parseargs parses command line arguments
def parseargs():
    parser = argparse.ArgumentParser()
    parser.add_argument("type", help="observation or specimen")
    parser.add_argument("incsv", help="input csv")
    parser.add_argument("outdir", help="fhir json files land here")
    parser.add_argement("-d", help="delimiter (assumed ;)", required=False)
    parser.add_argument("--delete", help="delete these fhir resources")
    args = parser.parse_args()
    return args

# main turns csv from file to fhir
def main():

    args = parseargs()

    # read from stdin
    #reader = csv.DictReader(open(args.incsv, "r"), delimiter=args.d)
    # rows = [row for row in reader]

    file = open(args.incsv, "r")
    
    # build observations or specimen
    if args.type == "observation":
        entries = csv_to_observation(file, delimiter=args.d)
    elif args.type == "specimen":
        entries = csv_to_specimen(file, delimiter=args.d)

    # write fhir observation files
    writeout(entries, args.outdir, args.type)

# kick off program
sys.exit(main())