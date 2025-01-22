# fhirbuild

build fhir jsons from code or csv.

usage: fhirbuild <observation|specimen|patient> <in csv> <out dir>

example: fhirbuild observation GSA_prep\out\gsa-korr.csv tmp-dir

## column names

specimen building takes the following column names:

```
category: [ALIQUOTGROUP|MASTER|DERIVED]
collection_date
concentration
concentration_unit
derival_date
fhirid
id_[SAMPLEID|EXTSAMPLEID|...]
initial_amount
initial_unit
location_path
organization_unit
parent_fhirid
parent_sampleid
received_date
reposition_date
rest_amount
rest_unit
subject_limspsn
type
xpos
ypos
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
python3 -m build
```

install:

```
pip install dist/fhirbuild-<current-version>.whl
```


## todo

patient building with id and studienzugeheorigkeit

primary to child relationship
