# csvtofhirobs.py builds fhir observations from a csv file
# maybe it should be merged with csvtofhir.py, for now it's seperate

# usage: cat <in csv> | python csvtofhirobs.py <outdir>

# it takes the following column names:

# comp_[...]            put your messwerte codes here, one column per code, each prefixed with 'comp_'
# effective_date_time           sollte das datetime heissen?
# id_[sampleid|extsampleid...]  a sample id
# methodname            the messprofile name
# method                the messprofile code
# sender                the EINS_CODE
# subject_psn           a patient id


from fhirbuild import *
import re
import csv
import json
from dict_path import DictPath
import sys
from datetime import datetime
import os
from buildhelp import *

# row_to_fhir turns a csv row to fhir
def row_to_fhir(row:dict, i):
    entry = None

    row = DictPath(row)

    # gather the components (columns prefixed by 'comp_') and sampleids (columns prefixed by 'id_') for this row into one array each
    comps = [] # array of key value pairs
    ids = [] # array of key value pairs
    for key in row.keys():
        # are we at a component column
        if re.match("^comp_", key):
            # strip the comp_ prefix and remember
            withoutprefix = re.sub(r"^comp_", "", key)
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

# csv_to_fhir_obs turns rows seperate fhir files
def csv_to_fhir_obs(rows):

    # todo check that only the specified columns are in csv

    out = []
    i = 0 # tmp, for fhirid
    for row in rows:
        # todo put more than one entry in bundle
        out.append(fhir_bundle([row_to_fhir(row, i)]))
        i+=1

    return out

# writeout writes an array of fhir observations to files in outdir
def writeout(entries, outdir):
    gen_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    c = 1
    for e in entries:
        f = gen_time + "_Observation_p" + str(c) + ".json"
        path = os.path.join(outdir, f)
        with open(path, 'w') as outf:
            json.dump(e, outf, indent=4)
        c += 1

# __main__ turns csv from stdin to fhir
if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("usage: cat <in csv> | python csvtofhirobs.py <outdir>")
        exit

    outdir = sys.argv[1]

    # read from stdin
    reader = csv.DictReader(open(0, "r"), delimiter=",")
    rows = [row for row in reader]
    entries = csv_to_fhir_obs(rows)

    # or:
    #df = pd.read_csv(open(0, "r"), sep=",")
    #entries = csv_to_fhir_obs(df.to_dict())

    # write fhir observation files
    writeout(entries, outdir)
