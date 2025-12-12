# csvtofhir.py converts a csv with sample info to fhir json

# for the column names for specimen and observation see readme.md

from fhirbuild import *
from datetime import datetime
from dict_path import DictPath
from tram import Sample, Patient, Amount, Finding, Identifier, Idable
from tram import Rec, BooleanRec, NumberRec, StringRec, DateRec, MultiRec, CatalogRec
import csv
import json
import os
import re
import math
import fhirbuild.help as fbh
from fhirbuild.help import intornone

def csv_to_samples(reader: csv.DictReader, mainidc:str=None):
    """csv_to_samples turns csv file into a list of Sample instances. mainidc can be given as argument or csv column."""

    samples = []
    for row in reader:
        samples.append(row_to_sample(row, mainidc=mainidc))

    return samples


def csv_to_patient_fhir(reader: csv.DictReader, mainidc:str=None) -> list[dict]:
    """csv_to_patient_fhir turns csv file into a list of patient fhir entries."""

    entries = []
    for row in reader:
        entries.append([row_to_patient_fhir(row, mainidc=mainidc)])

    return entries


def csv_to_findings(reader: csv.DictReader, delim_cmp:str):
    """csv_to_findings turns csv rows to a list of Finding instances."""

    rows = list(reader)

    # todo check that only the specified columns are in csv
    out = []

    for i, row in enumerate(rows):
        out.append(row_to_finding(row, delim_cmp, i))

    return out


def row_to_sample(row:dict, mainidc:str=None) -> dict:
    """row_to_sample turns a csv row to a Sample instance. mainidc can be passed as parameter or csv column."""
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

    # make identifiers for the sample
    
    raw_identifiers = extract_identifiers(row, prefix="idcs_")

    # overwrite the mainidc argument by the csv column, if given.
    # if there is only one idc, take it as mainidc. else take it from the row.
    if "mainidc" in row:
        mainidc = row["mainidc"]
    if len(raw_identifiers) == 1 and mainidc is None:
        mainidc = raw_identifiers.keys()[0]

    if mainidc is None:
        raise Exception("mainidc needed to specify from which idc to build the fhirid.")
    if not mainidc in raw_identifiers.keys():
        raise Exception(f"there is no column for mainidc {mainidc}, it needs to be in {list(raw_identifiers.keys())}")

    identifiers = []
    for type, value in raw_identifiers.items():
        try:
            identifiers.append(Identifier(code=type, id=value))
        except ValueError as e:
            print(f"Error processing identifier {type}: {e}")   

    # add the fhirid as identifier
    identifiers.append(Identifier(code="fhirid", id=fhirid))

    # convert dates
    received_date = fbh.fromisoornone(row['received_date'])    
    collection_date = fbh.fromisoornone(row['collection_date'])
    derival_date = fbh.fromisoornone(row['derival_date'])        
    reposition_date = fbh.fromisoornone(row['reposition_date'])
    derival_date = fbh.fromisoornone(row['derival_date'])   
    collection_date = fbh.fromisoornone(row['collection_date'])

    # make amounts
    initial_amount = None      
    if row['initial_amount']:
        initial_amount = Amount(value=float(row['initial_amount']), unit=row['initial_unit'])
    rest_amount = None
    if row['rest_amount']:
        rest_amount = Amount(value=float(row['rest_amount']), unit=row['rest_unit'])


    # make a sample instance from the row
    sample = Sample(
        category=row['category'],
        samplingdate=collection_date,
        repositiondate=reposition_date,
        locationpath=row['location_path'],
        orga=row['organization_unit'],
        derivaldate=derival_date,
        ids=Idable(ids=identifiers, mainidc=mainidc),
        type=row['type'],
        patient=Idable([Identifier(id=row['subject_id'], code=row['subject_idcontainer'])]),
        receiptdate=received_date,
        initialamount=initial_amount,
        restamount=rest_amount,
        xposition=intornone(row['xpos']),
        yposition=intornone(row['ypos']),
        receptacle=row['receptacle']
    )

    # return
    return sample

def row_to_patient_fhir(row:dict, mainidc:str=None):
    """row_to_patient_fhir turns a csv row to a patient fhir entry. it lets update_with_overwrite be set for each row."""

    # to avoid errors if keys are missing
    row = DictPath(row)
    
    # todo id_PSN auseinander droeseln in zwei argumente, die id und den idcontainertyp

    update_with_overwrite = get_update_overwrite_flag(row)

    # identifiers
    raw_identifiers = extract_identifiers(row, prefix="idcp_")

    # overwrite the mainidc argument by the csv column, if given.
    # if there is only one idc, take it as mainidc. else take it from the row.
    if "mainidc" in row:
        mainidc = row["mainidc"]
    if len(raw_identifiers) == 1 and mainidc is None:
        mainidc = raw_identifiers.keys()[0]
        
    if mainidc is None:
        raise Exception("mainidc needed to specify from which idc to build the fhirid.")
    if not mainidc in raw_identifiers.keys():
        raise Exception(f"there is no column for mainidc {mainidc}, it needs to be in {list(raw_identifiers.keys())}")
    
    identifiers = []

    for type, value in raw_identifiers.items():
        identifiers.append(Identifier(code=type, id=value))

    # for now, tuck in the fhirid with the identifiers
    identifiers.append(Identifier(code="fhirid", id=row["fhirid"]))

    patient = Patient(ids=Idable(ids=identifiers, mainidc=mainidc),
                      orga=row['organization_unit'])

    p_fhir = fhir_patient(patient, update_with_overwrite=update_with_overwrite)
    
    return p_fhir



def row_to_finding(row:dict, i, delim_cmp, delete=False):
    """row_to_finding turns a csv row to a Finding instance."""
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

    comprecs = {}
    # make recs from each component.
    for i, comp in comps.items():
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
            
        comprecs[comp["code"]] = rec
        
    # gather the sampleids (columns prefixed by 'idcs_') 
    raw_identifiers = extract_identifiers(row, prefix="idcs_")
    # make identifiers from them
    sids = [] # array of Identifiers
    for key, val in raw_identifiers.items():
        sids.append(Identifier(id = val, code = key))

    effectivedate = fbh.fromisoornone(row["effective_date_time"])

    # build the finding
    finding = Finding(findingdate=effectivedate,
                      method=row['method'],
                      methodname=row['methodname'],
                      patient=Idable(id=row['subject_id'], code="LIMSPSN", mainidc="LIMSPSN"),
                      recs=comprecs,
                      sample=Idable(ids=sids, mainidc="SAMPLEID"),
                      sender=row['sender']
    )
    
    # return the finding
    return finding

def get_update_overwrite_flag(row):
    """get_update_overwrite_flag checks if the row has the update_with_overwrite flag set, returns true or false, false if not set."""
    if 'update_with_overwrite' in row.keys():
        update_with_overwrite = row['update_with_overwrite']
    else:
        update_with_overwrite = False
    return update_with_overwrite

def extract_identifiers(row: dict, prefix:str="idc_") -> list:
    """
    extract_identifiers extracts identifiers from a row dictionary.
    identifiers are to be prefixed with 'idcs_' or 'idcp_' for sample and patient, respectively.
    returns a dict keyed by idc code.
    """
    out = {}
    for key in row.keys():
        if key.startswith(prefix):
            strippedkey = key.removeprefix(prefix)
            # Check if the value is not None before appending
            if row[key] is not None:
                out[strippedkey] = row[key]
    #  print(out)  # Debugging output
    return out

