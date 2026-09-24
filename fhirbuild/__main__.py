# __main__.py is called on python -m fhirbuild

import sys
import argparse
from fhirbuild.csvtofhir import csv_to_samples, csv_to_findings, csv_to_patients
from fhirbuild import write_samples, write_observations, write_patients, change_request_method
import fhirbuild.help as fbh
import versionflag

def parseargs():
    """parseargs parses command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("type", help="observation|specimen|patient|request_method")
    parser.add_argument("incsv", help="input csv (input dir for request_method)")
    parser.add_argument("outdir", help="fhir json files land here")
    parser.add_argument("-d", help="delimiter (assumed ;)", required=False, default=";")
    parser.add_argument("--delim-cmp", help="delimiter for the cmp value field for the multi-value cmp types MULTI and CATALOG (assumed ,)", required=False, default=",")    
    parser.add_argument("-e", help="encoding (assumed utf-8)", required=False, default="utf-8")
    parser.add_argument("--delete", help="delete these fhir resources")
    parser.add_argument("--cxx", help="cxx version. 3|4")
    parser.add_argument("--mainidc", help="the idcontainer from which the fhirid is built, can be left out if there is only one idcontainer given.")
    parser.add_argument("--db", help="db target")
    parser.add_argument("--load-required", help="db target")
    parser.add_argument("--request-method", help="request method for request_method option. POST|DELETE")
    versionflag.flag(parser, "fhirbuild")
    args = parser.parse_args()
    return args




def main():
    """main turns csv from file to fhir for specimen, patient or observation."""
    args = parseargs()

    delimiter = ";"
    if args.d != None:
        delimiter = args.d

    # read the csv, except for request_method (where it is a dir)
    if args.type != "request_method":
        dict_reader = fbh.open_csv_file(args.incsv, delimiter=delimiter, encoding=args.e)

    # build what's needed
    match args.type:
        case "observation":
            findings = csv_to_findings(dict_reader, args.delim_cmp, db=args.db)
            write_observations(findings, dir=args.outdir, batchsize=10, cxx=3)
        case "specimen":
            samples = csv_to_samples(dict_reader, mainidc=args.mainidc)
            write_samples(samples, dir=args.outdir, batchsize=10, cxx=3)
        case "patient":
            patients = csv_to_patients(dict_reader, mainidc=args.mainidc)
            write_patients(patients, dir=args.outdir, batchsize=10, cxx=3)
        case "request_method":
            change_request_method(args.incsv, args.outdir, request_method=args.request_method)
        case _:
            print(f"Unknown type: {args.type}")
            sys.exit(1)
            

# kick off program
sys.exit(main())


