# csvtofhir.py converts a csv with sample info to fhir json

# for the column names for specimen and observation see readme.md

from fhirbuild import *
from datetime import datetime
from dict_path import DictPath
import csv
import json
import pandas as pd
import re
import os
import math
from fhirbuild.buildhelp import *

# csv_to_specimen_str turns csv file to fhir string
# should it return array of objects or string?
def csv_to_specimen_str(file) -> str:
    return json.dumps(csv_to_specimen(file))

# csv_to_specimen turns csv file into an array of fhir objects
def csv_to_specimen(file, delimiter=";"):
    reader = csv.DictReader(file, delimiter=delimiter)
    rows = list(reader)
    #print(rows)

    out = []
    for row in rows:
        #out.append(fhir_bundle([row_to_observation(row, i, delete)]))
        out.append(fhir_bundle([row_to_specimen(row)]))

    return out

# csv_to_patient turns csv file into array of patient fhir objects
def csv_to_patient(file, delimiter=";"):
    reader = csv.DictReader(file, delimiter=delimiter)
    rows = list(reader)

    out = []
    i = 0
    for row in rows:
        out.append(fhir_bundle([row_to_patient(row, i)]))
        i = i+1

    return out



# dataframe_to_specimen turns a dataframe to fhir
def dataframe_to_specimen(df):
    out = []
    for row in df:
        out.append(fhir_bundle([row_to_specimen(row)]))
    return out

# row_to_fhir turns a csvrow to fhir
def row_to_specimen(row:dict):
    entry = None

    row = DictPath(row)

    # common
    received_date = None
    if row['received_date'] != "":
      received_date = panda_timestamp(row['received_date'])

    if row['category'] == "ALIQUOTGROUP":
        entry = fhir_aliquotgroup(organization_unit=row['organization_unit'], type=row['type'], subject_limspsn=row['subject_limspsn'], received_date=received_date, parent_sampleid=row['parent_sampleid'], fhirid=row['fhirid']) # todo pass args

    elif row['category'] == "MASTER" or row['category'] == "DERIVED":

        # build fhir sub-structures
        # todo: use any string after 'idc_' as code for a sampleid
        """
        # extract different id containers from keys in row
        idcs = [] # array of strings
        for key in row.keys():
          if re.match("^idc_", key):
            idcs.append(re.remove("^idc_", key)
        ids = [] # array of fhir objects
        """
        sampleid = fhir_identifier(code="SAMPLEID", value=row['id_SAMPLEID'])
        
        initial_amount = None
        if row['initial_amount'] != None:
            initial_amount = fhir_quantity(value=row['initial_amount'], unit=row['initial_unit'])
        rest_amount = None
        if row['rest_amount'] != None:
            rest_amount = fhir_quantity(value=row['rest_amount'], unit=row['rest_unit'])

        # convert dates specific to primary or aliquot (not in aliquotgroup)
        # received_date done before
        collection_date = panda_timestamp(row['collection_date'])
        derival_date = panda_timestamp(row['derival_date'])        
        reposition_date = panda_timestamp(row['reposition_date'])

        # build entry
        entry = fhir_sample(
            category=row['category'],
            collected_date=collection_date,
            container=row["container"],
            derival_date=derival_date,
            identifiers=[sampleid],
            fhirid=row['fhirid'],
            initial_amount=initial_amount,
            location_path=row['location_path'],
            organization_unit=row['organization_unit'],
            parent_fhirid=row['parent_fhirid'],
            received_date=received_date,
            reposition_date=reposition_date,
            rest_amount=rest_amount,
            subject_limspsn=row['subject_limspsn'],
            type=row['type'],
            xposition=intornone(row['xpos']),
            yposition=intornone(row['ypos'])
        )

        #print("entry: " + entry)
    else:
        # error
        print("row needs category column with MASTER, DERIVED or ALIQUOTGROUP")
    
    return entry

# intornone parses a string to int, and letters A,B,C,... to numbers 1,2,3..., and doesn't cry when it receives none
def intornone(s:str):
    if s == None:
        return None
    if re.match(r"^[A-Za-z]$", s):
        #print("match letter")
        # convert to lower, so that you can subtract 96 from lower case 'a' and land at 1
        s = s.lower()
        # get the ascii number for the letter with ord() and subtract 96
        num = ord(s) - 96
        return num
    #print(f"not match letter: '{s}'")
    return int(s)

# writeout writes an array of fhir observations to files in outdir
def writeout(entries, outdir, type):
    gen_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # how broad should the zero-place holder for the pagenumber be? (eg for 999 pages 3, for 1000 pages 4)
    page_num_width = str(int(math.log10(len(entries))) + 1)
    #print("pnw: " + page_num_width)
    c = 1
    for e in entries:
        fstring = "%s_%s_p%0" + page_num_width + "d.json"
        f = fstring % (gen_time, type, c)
        path = os.path.join(outdir, f)
        with open(path, 'w') as outf:
            json.dump(e, outf, indent=4)
        c += 1

# row_to_observation turns a csv row to fhir
def row_to_observation(row:dict, i, delete=False):
    entry = None

    row = DictPath(row)

    # gather the components (columns prefixed by 'cmp_') and sampleids (columns prefixed by 'id_') for this row into one array each
    comps = [] # array of key value pairs
    ids = [] # array of key value pairs
    for key in row.keys():
        # are we at a component column
        if re.match("^cmp_", key):
            # strip the cmp_ prefix and remember
            withoutprefix = re.sub(r"^cmp_", "", key)
            comps.append((withoutprefix, row[key]))
        # are we at a sampleid column
        if re.match("^id_", key):
            # strip the idc_ prefix and remember
            withoutprefix = re.sub(r"^id_", "", key)
            ids.append((withoutprefix, row[key]))

    effectivedate = panda_timestamp(row["effective_date_time"])

    # build the entry
    entry = fhir_obs(component=comps, effective_date_time=effectivedate, fhirid=str(i), identifiers=ids, method=row['method'], methodname=row['methodname'], sender=row['sender'], subject_psn=row['subject_psn'], delete=delete)

    return entry


# row_to_patient turns the row of a csv to fhir patient
def row_to_patient(row:dict, i):
    # todo id_PSN auseinander droeseln in zwei argumente, die id und den idcontainertyp
    entry = fhir_patient(psn=row['id_PSN'], organization_unit=row['organization_unit'], study=row['study'], fhirid=str(i))
    return entry

# csv_to_observation turns rows seperate fhir files
def csv_to_observation(file, delimiter, delete=False):

    # do not use named argument, cause none could be parsed via argparse.
    # is this a good pattern or should something like this be catched before?
    # but if you catch it before, you'd have to make it at any place where delimiter could be passed from args
    if delimiter == None:
        delimiter = ";"

    reader = csv.DictReader(file, delimiter=";") # todo pass delimiter
    rows = list(reader)
        
    # todo check that only the specified columns are in csv

    out = []
    i = 0 # tmp, for fhirid
    for row in rows:
        # todo put more than one entry in bundle
        out.append(fhir_bundle([row_to_observation(row, i, delete)]))
        i+=1

    return out




# __main__ turns csv from stdin to fhir
#if __name__ == "__main__":
#    print(csv_to_specimen(open(0, "r").read()))


