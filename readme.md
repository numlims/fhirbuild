# fhirbuild

build fhir jsons from code or csv.

usage: fhirbuild <observation|specimen|patient> <in csv> <out dir>

example: fhirbuild observation GSA_prep\out\gsa-korr.csv tmp-dir

## column names

csv input column names for building an primary (master) or aliquot
(derived) specimen:

```
category: [MASTER|DERIVED]    is the sample primary (MASTER) or
                              aliquot (DERIVED)?
collection_date               the collection date (entnahmedatum)
concentration                 the concentration
concentration_unit            the unit of the concentration
container                     ORG for primary, NUM_AliContainer for aliquot?
derival_date                  the derival date (aufteilungsdatum) is the
                              same as "datum der ersten einlagerung"
fhirid                        the identifier specific to fhir
id_[SAMPLEID|EXTSAMPLEID|...] one or more ids
initial_amount                the initial amount
initial_unit                  the initial unit
location_path                 the location path
organization_unit             the organization unit
parent_fhirid                 for an aliquot, link to the fhirid
                              of the parent aliquotgroup
received_date                 the received date (eingangsdatum)
reposition_date               the reposition date (einlagerungsdatum)
rest_amount                   the rest amount
rest_unit                     the unit of the rest amount
subject_limspsn               the limspsn of the patient
type                          the sample's type (material, CIT etc)
xpos                          the x position on the rack
ypos                          the y position on the rack
```

csv input column names for aliquotgroup:

```
category: ALIQUOTGROUP        the category of the sample
fhirid                        the identifier specific to fhir
organization_unit             the organization unit
parent_sampleid               for an aliquotgroup, link to the sampleid
                              of the group's parent primary sample
received_date                 the received date (eingangsdatum)
subject_limspsn               the limspsn of the patient
type                          the sample's type (material, CIT etc)
```

todo centrifugation values

csv input column names for observation:

```
cmp_[...]            put your messwerte codes here, one column per code, each prefixed with 'cmp_' (for component field in fhir)
effective_date_time           sollte das datetime heissen?
id_[SAMPLEID|EXTSAMPLEID|...]  a sample id
methodname            the messprofile name
method                the messprofile code
sender                the EINS_CODE
subject_psn           a patient id
```

csv input columns for patient:

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


## dev

fhir examples for master (primary), aliquotgroup and derived (aliquot)
are in in example.md.


## todo

patient building with id and studienzugeheorigkeit

primary to child relationship
