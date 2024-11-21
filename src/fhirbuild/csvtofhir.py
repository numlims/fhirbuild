# csvtofhir.py converts a csv with sample info to fhir json

# specimen building takes the following column names:

# category: [ALIQUOTGROUP|MASTER|DERIVED]
# collection_date
# concentration
# concentration_unit
# derival_date
# fhirid
# idc_[sampleid|extsampleid|...]
# initial_amount
# initial_unit
# location_path
# organization_unit
# parent_fhirid
# parent_sampleid
# received_date
# reposition_date
# rest_amount
# rest_unit
# subject_limspsn
# type
# xpos
# ypos

# todo centrifugation values

# observation building takes the following column names:

# cmp_[...]            put your messwerte codes here, one column per code, each prefixed with 'cmp_' (for component field in fhir)
# effective_date_time           sollte das datetime heissen?
# id_[sampleid|extsampleid...]  a sample id
# methodname            the messprofile name
# method                the messprofile code
# sender                the EINS_CODE
# subject_psn           a patient id

from fhirbuild import *
from datetime import datetime
from dict_path import DictPath
import csv
import json
import pandas as pd
import re
import os
from fhirbuild.buildhelp import *

# csv_to_specimen_str turns csv text to fhir string
# should it return array of objects or string?
def csv_to_specimen_str(text) -> str:
    return json.dumps(csv_to_specimen(text))

# csv_to_specimen turns csv text into an array of fhir objects
def csv_to_specimen(text):
    reader = csv.dictreader(text, delimiter=",")
    rows = list(reader)

    out = []
    for row in rows:
        out.append(row_to_specimen(row))

    return out

# dataframe_to_specimen turns a dataframe to fhir
def dataframe_to_specimen(df):
    out = []
    for row in df:
        out.append(row_to_specimen(row))
    return out

# row_to_fhir turns a csvrow to fhir
def row_to_specimen(row:dict):
    entry = None

    row = DictPath(row)

    # common
    received_date = panda_timestamp(row['received_date'])

    if row['category'] == "ALIQUOTGROUP":
        entry = fhir_aliquotgroup(organization_unit=row['organization_unit'], code=row['code'], subject_limspsn=row['subject_limspsn'], received_date=received_date, parent_sampleid=row['parent_sampleid'], fhirid=row['fhirid']) # todo pass args

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
        sampleid = fhir_identifier(code="SAMPLEID", value=row['idc_sampleid'])
        
        initial_amount = None
        if row['initial_amount'] != None:
            initial_amount = fhir_quantity(value=int(row['initial_amount']), unit=row['initial_unit'])
        rest_amount = None
        if row['rest_amount'] != None:
            rest_amount = fhir_quantity(value=int(row['rest_amount']), unit=row['rest_unit'])

        # convert dates
        reposition_date = panda_timestamp(row['reposition_date'])
        derival_date = panda_timestamp(row['derival_date'])

        # build entry
        entry = fhir_sample(category=row['category'], fhirid=row['fhirid'], reposition_date=reposition_date, location_path=row['location_path'], organization_unit=row['organization_unit'], derival_date=derival_date, identifiers=[sampleid], type=row['type'], subject_limspsn=row['subject_limspsn'], received_date=received_date, parent_fhirid=row['parent_fhirid'], initial_amount=initial_amount, rest_amount=rest_amount, xposition=intornone(row['xpos']), yposition=intornone(row['ypos']))
    
    return entry

# intornone parses a string to int and doesn't cry when it receives none
def intornone(s:str):
    if s == None:
        return None
    return int(s)

# writeout writes an array of fhir observations to files in outdir
def writeout(entries, outdir, type):
    gen_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    c = 1
    for e in entries:
        f = gen_time + "_Observation_p" + str(c) + ".json"
        path = os.path.join(outdir, f)
        with open(path, 'w') as outf:
            json.dump(e, outf, indent=4)
        c += 1

# row_to_observation turns a csv row to fhir
def row_to_observation(row:dict, i):
    entry = None

    row = DictPath(row)

    # gather the components (columns prefixed by 'comp_') and sampleids (columns prefixed by 'id_') for this row into one array each
    comps = [] # array of key value pairs
    ids = [] # array of key value pairs
    for key in row.keys():
        # are we at a component column
        if re.match("^cmp_", key):
            # strip the comp_ prefix and remember
            withoutprefix = re.sub(r"^cmp_", "", key)
            comps.append((withoutprefix, row[key]))
        # are we at a sampleid column
        if re.match("^id_", key):
            # strip the idc_ prefix and remember
            withoutprefix = re.sub(r"^id_", "", key)
            ids.append((withoutprefix, row[key]))

    effectivedate = panda_timestamp(row["effective_date_time"])

    # build the entry
    entry = fhir_obs(component=comps, effective_date_time=effectivedate, fhirid=str(i), identifiers=ids, method=row['method'], methodname=row['methodname'], sender=row['sender'], subject_psn=row['subject_psn'])

    return entry

# csv_to_observation turns rows seperate fhir files
def csv_to_observation(rows):

    # todo check that only the specified columns are in csv

    out = []
    i = 0 # tmp, for fhirid
    for row in rows:
        # todo put more than one entry in bundle
        out.append(fhir_bundle([row_to_observation(row, i)]))
        i+=1

    return out


# __main__ turns csv from stdin to fhir
#if __name__ == "__main__":
#    print(csv_to_specimen(open(0, "r").read()))


