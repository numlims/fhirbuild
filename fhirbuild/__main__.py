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
    parser.add_argument("--cxx", help="cxx version. 3|4")    
    
    args = parser.parse_args()
    return args


def open_csv_file(filename, delimiter=";", encoding="utf-8"):
    """
    open_csv_file opens a CSV file and returns a DictReader object.
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
    """main turns csv from file to fhir for specimen, patient or observation."""
    args = parseargs()

    delimiter = ";"
    if args.d != None:
        delimiter = args.d

    # read the csv
    dict_reader = open_csv_file(args.incsv, delimiter=delimiter, encoding=args.e)

    # build what's needed
    match args.type:
        case "observation":
            findings = csv_to_finding(dict_reader, args.delim_cmp)
            write_observations(findings, dir=args.outdir, batchsize=10, cxx=3)
        case "specimen":
            samples = csv_to_samples(dict_reader)
            write_samples(samples, dir=args.outdir, batchsize=10, cxx=3)
        case "patient":
            entries = csv_to_patient_fhir(dict_reader)
            bundles = bundle(entries, 10, type="Patient", cxx=3)
            writeout(bundles, args.outdir, args.type)
        case _:
            print(f"Unknown type: {args.type}")
            sys.exit(1)
            

# kick off program
sys.exit(main())
