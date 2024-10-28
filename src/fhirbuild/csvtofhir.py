# csvtofhir.py converts a csv with sample info to fhir json

# to build observations see csvtofhirobs.py

# it takes the following column names:

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

from fhirbuild import *
#from dict_path import DictPath
from dict_path import DictPath
import csv
import json
import pandas as pd
import sys
from buildhelp import *

#sys.path.append(r'G:\environment\source\csv_tecan_fhir_import\.env\lib\site-packages')


# csv_to_fhir_str turns csv text to fhir string
# should it return array of objects or string?
def csv_to_fhir_str(text) -> str:
    return json.dumps(csv_to_fhir(text))

# csv_to_fhir turns csv text into an array of fhir objects
def csv_to_fhir(text):
    reader = csv.dictreader(text, delimiter=",")
    rows = list(reader)

    out = []
    for row in rows:
        out.append(row_to_fhir(row))

    return out

# dataframe_to_fhir turns a dataframe to fhir
def dataframe_to_fhir(df):
    out = []
    for row in df:
        out.append(row_to_fhir(row))
    return out

# row_to_fhir turns a csvrow to fhir
def row_to_fhir(row:dict):
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




# __main__ turns csv from stdin to fhir
if __name__ == "__main__":
    print(csv_to_fhir(open(0, "r").read()))


