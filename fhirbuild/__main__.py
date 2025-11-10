# __main__.py is called on python -m fhirbuild

import sys
import argparse
import csv
from fhirbuild.csvtofhir import csv_to_specimen, csv_to_observation, csv_to_patient
from fhirbuild import writeout

def parseargs():
    """parseargs parses command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("type", help="observation or specimen or patient")
    parser.add_argument("incsv", help="input csv")
    parser.add_argument("outdir", help="fhir json files land here")
    parser.add_argument("-d", help="delimiter (assumed ;)", required=False, default=";")
    parser.add_argument("--delim-cmp", help="delimiter for the cmp_value field for the multi-value cmp_types MULTI and CATALOG (assumed ,). needs to be different that the delimiter of the csv file.", required=False, default=",")    
    parser.add_argument("-e", help="encoding (assumed utf-8)", required=False, default="utf-8")
    parser.add_argument("--delete", help="delete these fhir resources")
    
    args = parser.parse_args()
    return args


def open_csv_file(filename, delimiter=";", encoding="utf-8"):
    """
    Opens a CSV file and returns a DictReader object.
    """
    try:
        file = open(filename, "r", encoding=encoding)
        return csv.DictReader(file, delimiter=delimiter)
    except FileNotFoundError:
        print(f"File {filename} not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error opening file {filename}: {e}")
        sys.exit(1)



def main():
    """main turns csv from file to fhir."""
    args = parseargs()

    # read from stdin
    #reader = csv.DictReader(open(args.incsv, "r"), delimiter=args.d)
    # rows = [row for row in reader]

    #file = open(args.incsv, "r")

    delimiter = ";"
    if args.d != None:
        delimiter = args.d
    
    dict_reader = open_csv_file(args.incsv, delimiter=delimiter, encoding=args.e)
   

    match args.type:
        case "observation":
            entries = csv_to_observation(dict_reader, args.delim_cmp)
        case "specimen":
            entries = csv_to_specimen(dict_reader)
        case "patient":
            entries = csv_to_patient(dict_reader)
        case _:
            print(f"Unknown type: {args.type}")
            sys.exit(1)
    # build observations or specimen
    # write fhir observation files
    # print(f"type: {entries}")

    bundles = bundle(entries, 10)
    writeout(bundles, args.outdir, args.type)

# kick off program
sys.exit(main())
