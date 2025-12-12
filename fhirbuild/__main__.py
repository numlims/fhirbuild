# __main__.py is called on python -m fhirbuild

import sys
import argparse
from fhirbuild.csvtofhir import csv_to_samples, csv_to_findings, csv_to_patient_fhir
from fhirbuild import writeout, write_samples, write_observations, bundle
import fhirbuild.help as fbh

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
    parser.add_argument("--mainidc", help="the idcontainer from which the fhirid is built, can be left out if there is only one idcontainer given.")
    args = parser.parse_args()
    return args




def main():
    """main turns csv from file to fhir for specimen, patient or observation."""
    args = parseargs()

    delimiter = ";"
    if args.d != None:
        delimiter = args.d

    # read the csv
    dict_reader = fbh.open_csv_file(args.incsv, delimiter=delimiter, encoding=args.e)

    # build what's needed
    match args.type:
        case "observation":
            findings = csv_to_findings(dict_reader, args.delim_cmp)
            write_observations(findings, dir=args.outdir, batchsize=10, cxx=3)
        case "specimen":
            samples = csv_to_samples(dict_reader, mainidc=args.mainidc)
            write_samples(samples, dir=args.outdir, batchsize=10, cxx=3)
        case "patient":
            # at the moment don't make Patient instances, cause each csv row carries an updateWithOverwrite field that couldn't be saved directly to Patients at the moment (make a FhirPatient that inherits from Patient? maybe that's a bit overdone). could we pass a --update-with-overwrite flag for all rows, or does it make sense to keep this row-specific?
            entries = csv_to_patient_fhir(dict_reader, mainidc=args.mainidc)
            bundles = bundle(entries, 10, restype="Patient", cxx=3)
            writeout(bundles, args.outdir, args.type)
        case _:
            print(f"Unknown type: {args.type}")
            sys.exit(1)
            

# kick off program
sys.exit(main())
