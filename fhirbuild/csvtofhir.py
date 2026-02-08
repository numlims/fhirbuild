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
from fhirbuild.help import intornone, is_nullish

def csv_to_samples(reader: csv.DictReader, mainidc:str=None):
    """csv_to_samples turns a csv file into a list of Sample instances. mainidc can be given as argument or csv column. fhirids are taken if given, but not generated."""

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
    """row_to_sample turns a csv row to a Sample instance. mainidc can be passed as parameter or csv column. aliquots can reference their parent aliquotgroups by fhirid or index in the csv file, a "fhirid" or "index" Identifier is written to the Sample accordingly. fhirids need to be generated later with _fill_in_fhirids"""
    entry = None

    row = DictPath(row)    # common

    # get the ids without sidc_ prefix
    raw_identifiers, mainidc = extract_and_resovle_identifiers(row, prefix="sidc_", mainidc=mainidc)

    # make an array of Identifier instances for each sidc_
    identifiers = []
    for type, value in raw_identifiers.items():
        try:
            identifiers.append(Identifier(code=type, id=value))
        except ValueError as e:
            print(f"Error processing identifier {type}: {e}")   

    # if there's a fhirid, add it as identifier
    if row["fhirid"] is not None:
        identifiers.append(Identifier(code="fhirid", id=row["fhirid"]))

    # if there's a index, add it as identifier
    if row["index"] is not None:
        identifiers.append(Identifier(code="index", id=row["index"]))

    ids = Idable(ids=identifiers, mainidc=mainidc)        
        
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

    # make a parent Idable from parent_fhirid or parent_index
    pids = []
    
    # for aliquots referencing aliquotgroups:
    # notify if no parent reference given
    if row["category"] == "DERIVED" and row["parent_fhirid"] is None and row["parent_index"] is None:
        print(f"no parent_fhirid or parent_index for derived sample {ids.id()} given.")
    # make Identifiers
    if row["parent_fhirid"] is not None:
        pids.append(Identifier(id=row["parent_fhirid"], code="fhirid"))
    if row["parent_index"] is not None:
        pids.append(Identifier(id=row["parent_index"], code="index"))
        
    # for aliquotgroups referencing samples:
    # make Identifiers
    if row["parent_sampleid"] is not None:
        pids.append(Identifier(id=row["parent_sampleid"], code=row["parent_idc"]))
        
    parent = None
    if len(pids) > 0:
        # print("mainidc: " + mainidc)
        parent = Idable(ids=pids, mainidc=row["parent_idc"])

    # make a patient identifier
    # get the patient id without pidc_ prefix
    patid_raw = extract_identifiers(row, prefix="pidc_")
    # there is only one patient id allowed
    if len(patid_raw) > 1:
        print(f"error: more than one patient id for sample {ids.id()} given.")
    patids = []
    for type, value in patid_raw.items():
        patids.append(Identifier(code=type, id=value))
    
        
    # make a sample instance from the row
    sample = Sample(
        category=row['category'],
        samplingdate=collection_date,
        repositiondate=reposition_date,
        locationpath=row['location_path'],
        orga=row['organization_unit'],
        derivaldate=derival_date,
        ids=ids,
        type=row['type'],
        parent=parent,
        patient=Idable(ids=patids, mainidc=patids[0].code),
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
    raw_identifiers, mainidc = extract_and_resovle_identifiers(row, prefix="pidc_", mainidc=mainidc)

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

    # gather the components (columns prefixed by 'cmp_t_' and 'cmp_v_' for type and value respectively)
    comps = {} # map indexed by component code.
    for key in row.keys():
        # are we at a component column
        if re.match("^cmp_", key):
            # each component comes with a type (t) and value (v) column:
            # cmp_t_CODE cmp_v_CODE
            # for the field names see the observation section in readme.md.
            
            # is it type or value?
            a = key.split("_")
            typeorval = a[1]

            # what's the code of the component?
            code = re.sub(r"^cmp_(t|v)_", "", key)
            
            # is this component new? add it.
            if not code in comps:
                comps[code] = {}

            # put what's in the row at this key either into the component type or value
            if typeorval == "t":
                comps[code]["type"] = row[key]
            elif typeorval == "v":
                comps[code]["value"] = row[key]
            else:
                print("error: each component needs a cmp_t_CODE and cmp_v_CODE column, see the fhirbuild readme.")

    comprecs = {}
    # make recs from each component.
    for code, comp in comps.items():
        rec = None
        if comp["type"] == "BOOLEAN":
            rec = BooleanRec(rec=comp["value"])
        elif comp["type"] == "NUMBER":
            rec = NumberRec(rec=comp["value"])
        elif comp["type"] == "DATE":
            rec = DateRec(rec=comp["value"]) # parse?
        elif comp["type"] == "STRING":
            rec = StringRec(rec=comp["value"])
        elif comp["type"] == "MULTI":
            # split the value
            values = comp["value"].split(delim_cmp)
            rec = MultiRec(rec=values)
        elif comp["type"] == "CATALOG":
            # split
            values = comp["value"].split(delim_cmp)
            rec = CatalogRec(rec=values)
            
        comprecs[code] = rec
        
    # gather the sampleids (columns prefixed by 'sidc_') 
    raw_identifiers = extract_identifiers(row, prefix="sidc_")
    # make identifiers from them
    sids = [] # array of Identifiers
    for key, val in raw_identifiers.items():
        sids.append(Identifier(id = val, code = key))

    # get the patient id
    patid_raw = extract_identifiers(row, prefix="pidc_")
    # there is only one patient id allowed
    if len(patid_raw) > 1:
        print(f"error: more than one patient id for sample {ids.id()} given.")
    patids = []
    for type, value in patid_raw.items():
        patids.append(Identifier(code=type, id=value))

    effectivedate = fbh.fromisoornone(row["effective_date_time"])

    # build the finding
    finding = Finding(findingdate=effectivedate,
                      method=row['method'],
                      methodname=row['methodname'],
                      patient=Idable(ids=patids, mainidc=patids[0].code),
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
    identifiers are to be prefixed with 'sidc_' or 'pidc_' for sample and patient, respectively.
    returns a dict keyed by idc code.
    """
    out = {}
    for key in row.keys():
        if key.startswith(prefix):
            strippedkey = key.removeprefix(prefix)
            # Check if the value is not None before appending
            if row[key] is not None:
                out[strippedkey] = row[key]
    #print("extract identifiers row:")
    #print(row)  # Debugging output
    return out

def extract_and_resovle_identifiers(row: dict, prefix: str, mainidc: str) -> tuple:
    """
    Extract the identifiers from a row dictionary, resolves the mainidc if not given and 
    checks that there is a mainidc in the row 
    Uses only those idc's that have a non-nullish value in the row. 
    To identifiy the column has to be prefixed with 'sidc_' or 'pidc_' for sample and patient, respectively.
    If no mainidc is provided as argument, the function tries to find the mainidc by checking
    if there is only one identfier in the row, or if there is a column named "mainidc".

    Args:
        row (dict): The row dictionary to extract identifiers from.
        prefix (str): The prefix to identify identifier columns.
        mainidc (str): The main identifier code to check for.
    Returns:
        tuple: A tuple containing a dictionary of extracted identifiers, keyed by idc code, and the mainidc string.
    Raises:
        ValueError: If no identifiers with the specified prefix are found in the row.
        ValueError: If mainidc is not provided and cannot be determined from the row.
        ValueError: If the mainidc specified does not have a corresponding column or the value is nullish in the row
        ValueError: If the prefix is not 'sidc_' or 'pidc_'
    """
    resolved_mainidc  = mainidc 

    if prefix not in ["sidc_", "pidc_"]:
        raise ValueError("prefix must be either 'sidc_' or 'pidc_'")
    # get only identfieres with a non-nullish value and remove the prefix from the keys
    extracted_identifiers = {
        k: v for k, v in extract_identifiers(row, prefix=prefix).items()
        if not is_nullish(v)
    }

    if len(extracted_identifiers) == 0:
        raise ValueError(f"no none-nullish identifiers with prefix '{prefix}' found in row.")

    # try to determine mainidc if not given as argument: if there is only one identifier, take that. 
    # else look for a column "mainidc" in the row.
    if not resolved_mainidc:
        if len(extracted_identifiers) == 1:
            resolved_mainidc = list(extracted_identifiers.keys())[0]
        elif "mainidc" in row:
            resolved_mainidc = row["mainidc"]
        else:
            raise ValueError("mainidc not provided and cannot be determined from the row, please provide mainidc as argument or add a column 'mainidc' to the csv with the idc code of the main identifier for each row.")
    
    if resolved_mainidc not in extracted_identifiers:
        raise ValueError(f"there is an nullish value or no column for mainidc {resolved_mainidc}, please check csv data and add a column for mainidc")
    
    return extracted_identifiers, resolved_mainidc