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

def csv_to_specimen_str(file) -> str:
    """csv_to_specimen_str turns csv file to fhir string."""

    # should it return array of objects or string?

    return json.dumps(csv_to_specimen(file))


def add_bundle(entries: dict[str, list]) -> dict:
    """add_bundle does what?"""
    
    result = {}
    for subject_id, specimens in entries.items():
        # create a bundle for each subject_id
        bundle = fhir_bundle(specimens)
        result[subject_id] = bundle

    return result

# csv_to_specimen turns csv file into an array of fhir objects
def csv_to_specimen(reader: csv.DictReader):

    entries = []
    for row in reader:
        entries.append(row_to_specimen(row))

    return entries

# csv_to_patient turns csv file into array of patient fhir objects
def csv_to_patient(reader: csv.DictReader) -> list[dict]:

    entries = []
    for i, row in enumerate(reader):
        entries.append([row_to_patient(row, i)])

    return entries

# dataframe_to_specimen turns a dataframe to fhir
def dataframe_to_specimen(df):
    out = []
    for row in df:
        out.append(fhir_bundle([row_to_specimen(row)]))
    return out


def extract_identifiers(row: dict, prefix: str = "idc_") -> list:
    """
    Extracts identifiers from a row dictionary.
    Identifiers are expected to be prefixed with 'idc_'.
    Returns a list of tuples (type, value).
    """
    identifiers = []
    for key in row.keys():
        if key.startswith(prefix):
            key_without_idc_prefix = key.removeprefix(prefix)
            # Check if the value is not None before appending
            if row[key] is not None:
                identifiers.append((key_without_idc_prefix, row[key]))
  #  print(identifiers)  # Debugging output
    return identifiers

# row_to_fhir turns a csvrow to fhir
def row_to_specimen(row:dict) -> dict:
    entry = None

    row = DictPath(row)    # common

    # Generate or use provided FHIR ID
    fhirid = row.get('fhirid')
    if fhirid is None or fhirid == '':
        # Use SAMPLEID or another appropriate identifier to generate a deterministic ID
        id_source = row.get('idcs_SAMPLEID')  # Assuming SAMPLEID is the identifier for the sample
        if id_source is None:
            # Try to find any identifier that could be used
            for key in row.keys():
                if key.startswith('idcs_'):
                    id_source = row[key]
                    break
        fhirid = genfhirid(id_source)

    received_date = panda_timestamp(row['received_date'])

    if row['category'] == "ALIQUOTGROUP":
        entry = fhir_aliquotgroup(organization_unit=row['organization_unit'], type=row['type'], subject_id=row['subject_id'], received_date=received_date, parent_sampleid=row['parent_sampleid'], fhirid=fhirid) # todo pass args

    elif row['category'] == "MASTER" or row['category'] == "DERIVED":

        # identifiers
        raw_identifiers = extract_identifiers(row, prefix="idcs_")

        identifiers = []
        for type, value in raw_identifiers:
            try:
                identifiers.append(fhir_identifier(code=type, value=value))
            except ValueError as e:
                print(f"Error processing identifier {type}: {e}")   

        initial_amount = None      
        if row['initial_amount']:
            initial_amount = fhir_quantity(value=float(row['initial_amount']), unit=row['initial_unit'])
        rest_amount = None
        if row['rest_amount']:
            rest_amount = fhir_quantity(value=float(row['rest_amount']), unit=row['rest_unit'])


        # convert dates specific to primary or aliquot (not in aliquotgroup)
        # received_date done before
        collection_date = panda_timestamp(row['collection_date'])
        derival_date = panda_timestamp(row['derival_date'])        
        reposition_date = panda_timestamp(row['reposition_date'])
        derival_date = panda_timestamp(row['derival_date'])        # build entry
        collection_date = panda_timestamp(row['collection_date'])
        entry = fhir_sample(category=row['category'], fhirid=fhirid, collected_date=collection_date, reposition_date=reposition_date, location_path=row['location_path'], organization_unit=row['organization_unit'], derival_date=derival_date, identifiers=identifiers, type=row['type'], subject_id=row['subject_id'], subject_idcontainer=row['subject_idcontainer'], received_date=received_date, parent_fhirid=row['parent_fhirid'], initial_amount=initial_amount, rest_amount=rest_amount, xposition=intornone(row['xpos']), yposition=intornone(row['ypos']), receptacle=row['receptacle'])
    else:
        # error
        print("row needs category column with MASTER, DERIVED or ALIQUOTGROUP")
    
    return entry

# intornone parses a string to int, and letters A,B,C,... to numbers 1,2,3..., and doesn't cry when it receives none
def intornone(s:str):
  #  print(f"intornone: {s}")
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

# writeout writes an array of fhir ?entries? to files in outdir
# row_to_observation turns a csv row to fhir
def row_to_observation(row:dict, i, delim_cmp, delete=False):
    entry = None

    row = DictPath(row)

    # gather the components (columns prefixed by 'cmp_N_' for the Nth component)
    comps = {} # map indexed by component index.
    for key in row.keys():
        # are we at a component column
        if re.match("^cmp_", key):
            # each component comes with a index and different fields. 
            # cmp_<index>_<field>
            # for the field names see the observation section in readme.md.
            
            # what's the component's index?
            a = key.split("_")
            icomp = int(a[1])
            
            # is this component new? add it.
            if not icomp in comps:
                comps[icomp] = {}

            # what's the field of the component?
            field = re.sub(r"^cmp_\d+_", "", key)

            # put what's in the row at this key into the specific field for the ith component.
            comps[icomp][field] = row[key]

    comprecs = []
    # make recs from each component.
    for comp in comps:
        rec = None
        if comp["type"] == "BOOLEAN":
            rec = BooleanRec(value=comp["value"])
        elif comp["type"] == "NUMBER":
            rec = NumberRec(value=comp["value"])
        elif comp["type"] == "DATE":
            rec = DateRec(value=comp["value"]) # parse?
        elif comp["type"] == "STRING":
            rec = StringRec(value=comp["value"])
        elif comp["type"] == "MULTI":
            # split the value
            values = comp["value"].split(delim_cmp)
            rec = MultiRec(values=values)
        elif comp["type"] == "CATALOG":
            # split
            values = comp["value"].split(delim_cmp)
            rec = CatalogRec(values=values)
            
        comprecs.append(rec)
        
    # gather the sampleids (columns prefixed by 'id_') 
    ids = [] # array of key value pairs
    for key in row.keys():
        # are we at a sampleid column
        if re.match("^idcs_", key):
            # strip the idcs_ prefix and remember
            withoutprefix = re.sub(r"^idcs_", "", key)
            ids.append((withoutprefix, row[key]))

    effectivedate = panda_timestamp(row["effective_date_time"])

    # build the entry
    entry = fhir_obs(component=comprecs, effective_date_time=effectivedate, fhirid=str(i), identifiers=ids, method=row['method'], methodname=row['methodname'], sender=row['sender'], subject_id=row['subject_id'], delete=delete)

    return entry


# row_to_patient turns the fhir entry of a patient from csv row.
def row_to_patient(row:dict, i):
    # todo id_PSN auseinander droeseln in zwei argumente, die id und den idcontainertyp

    update_with_overwrite = get_update_overwrite_flag(row)

    # identifiers
    print(row)
    raw_identifiers = extract_identifiers(row, prefix="idcp_")  
    
    identifiers = []

    fhir_id = genfhirid(row.get('fhirid', str(i)))

    for type, value in raw_identifiers:
        identifiers.append(fhir_identifier(code=type, value=value))


    entry = fhir_patient(identifiers=identifiers, organization_unit=row['organization_unit'], fhirid=fhir_id, update_with_overwrite=update_with_overwrite)
    return entry


# get_update_overwrite_flag checks if the row has the update_with_overwrite flag set, returns true or false, false if not set
def get_update_overwrite_flag(row):
    if 'update_with_overwrite' in row.keys():
        update_with_overwrite = row['update_with_overwrite']
    else:
        update_with_overwrite = False
    return update_with_overwrite

# csv_to_observation turns rows seperate fhir files
def csv_to_observation(reader: csv.DictReader, delim_cmp:str):

    rows = list(reader)

    # todo check that only the specified columns are in csv

    out = []

    for i, row in enumerate(rows):
        # todo put more than one entry in bundle
        out.append(fhir_bundle([row_to_observation(row, delim_cmp, i)]))


    return out




# __main__ turns csv from stdin to fhir
#if __name__ == "__main__":
#    print(csv_to_specimen(open(0, "r").read()))


