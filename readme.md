# fhirbuild

build fhir jsons from code or csv.

usage: fhirbuild <observation|specimen|patient> <in csv> <out dir>

example: fhirbuild observation GSA_prep\out\gsa-korr.csv tmp-dir

## column names

specimen building takes the following column names:

```
category: [ALIQUOTGROUP|MASTER|DERIVED]   the category of the sample
collection_date               the collection date
concentration                 the concentration
concentration_unit            the unit of the concentration
derival_date                  the date on which the sample was derived, german?
fhirid                        the fhirid, what's that?
id_[SAMPLEID|EXTSAMPLEID|...] one or more ids
initial_amount                the initial amount
initial_unit                  the initial unit
location_path                 the location path
organization_unit             the organization unit
parent_fhirid                 the fhirid of the sample's parent
parent_sampleid               the sampleid of the parent
received_date                 the received date
reposition_date               the reposition date
rest_amount                   the rest amount
rest_unit                     the unit of the rest amount
subject_limspsn               the patient's limspsn
type                          the sample's type
xpos                          the x position on the rack
ypos                          the y position on the rack
```

todo centrifugation values

observation building takes the following column names:

```
cmp_[...]            put your messwerte codes here, one column per code, each prefixed with 'cmp_' (for component field in fhir)
effective_date_time           sollte das datetime heissen?
id_[SAMPLEID|EXTSAMPLEID|...]  a sample id
methodname            the messprofile name
method                the messprofile code
sender                the EINS_CODE
subject_psn           a patient id
```

patient columns:

```
id_[PSN|...]
study
organization_unit
```


## build and install

build:

```
pip install build
python3 -m build
```

install:

```
pip install dist/fhirbuild-<current-version>.whl
```


## todo

patient building with id and studienzugeheorigkeit

primary to child relationship
