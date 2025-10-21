# fhirbuild

build fhir jsons from code or csv.

usage: 

```
fhirbuild <observation|specimen|patient> <in csv> <out dir> <-d delimiter input> <-e encoding input>
```

example: 

```
fhirbuild observation GSA_prep\out\gsa-korr.csv tmp-dir -d ; -e utf-8-sig
```

## column names

csv input column names for building an primary (master) or aliquot
(derived) specimen:

| csv column | comment |
| --- | --- |
| category | MASTER or DERIVED. is the sample primary (MASTER) or aliquot (DERIVED)? |
| collection_date | the collection date (entnahmedatum) |
| concentration | the concentration |
| concentration_unit | the unit of the concentration |
| derival_date | the derival date (aufteilungsdatum) is the same as "datum der ersten einlagerung" |
| fhirid | the identifier specific to fhir |
| idcs_[SAMPLEID\|EXTSAMPLEID|...] | one or more ids |
| initial_amount | the initial amount |
| initial_unit | the initial unit |
| location_path | the location path |
| organization_unit | the organization unit |
| parent_fhirid | for an aliquot, link to the fhirid of the parent aliquotgroup |
| received_date | the received date (eingangsdatum) |
| receptacle |  the receptacle (probenbehaelter), becomes container |
| reposition_date | the reposition date (einlagerungsdatum)
| rest_amount | the rest amount |
| rest_unit | the unit of the rest amount |
| subject_id | the limspsn of the patient |
| type | the sample's type (material, CIT etc) |
| xpos | the x position on the rack |
| ypos | the y position on the rack |

aliquot groups are created with a subset of the columns of primary and
derived:

| csv column | comment |
| --- | --- |
| category | = ALIQUOTGROUP. the category of the sample |
| fhirid | the identifier specific to fhir |
| organization_unit | the organization unit |
| parent_sampleid | for an aliquotgroup, link to the sampleid of the group's parent primary sample |
| received_date | the received date (eingangsdatum) |
| subject_id | the limspsn of the patient |
| type | the sample's type (material, CIT etc) |

csv input column names for observation:

| csv column | comment |
| --- | --- |
| cmp_[...] | put your messwerte codes here, one column per code, each prefixed with 'cmp_' (for the component field in fhir) |
| effective_date_time | sollte das datetime heissen? |
| idcs_[SAMPLEID\|EXTSAMPLEID|...] | a sample id |
| methodname | the messprofile name |
| method | the messprofile code |
| sender | the EINS_CODE |
| subject_id | a patient id |

csv input columns for patient:

| csv column | comment |
| --- | --- |
| idcp_[PSN\|LIMSPSN...] | |
| fhirid | |
| organization_unit | |
| study | |


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
