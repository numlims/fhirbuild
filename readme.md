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

### specimen

csv input column names for building an primary (master) or aliquot
(derived) specimen.

referencing parent aliquotgroups: aliquotgroups don't come with a
sampleid. aliquots can reference their parent aliquotgroups either by
fhirid or by the aliquotgroup's index in the csv file.

primary and derived csv columns:

| csv column | comment |
| --- | --- |
| category | MASTER or DERIVED. is the sample primary (MASTER) or aliquot (DERIVED)? |
| collection_date | the collection date (entnahmedatum) |
| concentration | the concentration |
| concentration_unit | the unit of the concentration |
| derival_date | the derival date (aufteilungsdatum) is the same as "datum der ersten einlagerung" |
| fhirid | the identifier specific to fhir |
| sidc_[SAMPLEID\|EXTSAMPLEID\|...] | sample ids specified by idcontainers |
| pidc_[LIMSPSN\|MPI\|...] | one patientid of given idcontainer |
| initial_amount | the initial amount |
| initial_unit | the initial unit |
| location_path | the location path |
| mainidc | the sample idcontainer from which the fhirid is built, can be left out if there is only one idcontainer given |
| organization_unit | the organization unit |
| parent_fhirid | optional. if aliquots reference their aliquotgroups by fhirid, use this field. |
| parent_index | optional. if aliquots reference their parent aliquotgroups by index in the csv file, use this field. |
| received_date | the received date (eingangsdatum) |
| receptacle |  the receptacle (probenbehaelter), becomes container |
| reposition_date | the reposition date (einlagerungsdatum)
| rest_amount | the rest amount |
| rest_unit | the unit of the rest amount |
| type | the sample's type (material: EDTA, CIT etc) |
| xpos | the x position on the rack |
| ypos | the y position on the rack |

aliquotgroups are created with a subset of the columns for primary and
derived samples.

since aliquotgroups don't have a sampleid, child aliquots reference their
aliquotgroup parent by fhirid or the index of the aliquotgroup in the
csv file.

aliqotgroup csv columns:

| csv column | comment |
| --- | --- |
| category | = ALIQUOTGROUP. the category of the sample. |
| fhirid | optional. the fhirid of this aliquotgroup. use fhirid or index to reference aliquotgroups by their child aliquots. |
| pidc_[LIMSPSN\|MPI\|...] | one patientid of given idcontainer |
| index | optional. the index of this aliquotgroup in the csv file. use index or fhirid to reference aliquotgroups by their child aliquots. |
| organization_unit | the organization unit |
| parent_sampleid | reference the aliquotgroup's primary sample by sampleid. |
| parent_idc | the idcontainer of parent_sampleid. |
| received_date | the received date (eingangsdatum) |
| type | the sample's type (material: EDTA, CIT etc) |

### observation

csv input column names for observation.

additionally pass the --delim-cmp flag for the delimiter 
of the MULTI and CATALOG cmp_* value lists.

| csv column | comment |
| --- | --- |
| cmp_t_CODE | the type of the messparam with code CODE. can be BOOL, NUMBER, STRING, DATE, MULTI, CATALOG. |
| cmp_v_CODE | the value of the messparam with code CODE. |
| effective_date_time | sollte das datetime heissen? |
| sidc_[SAMPLEID\|EXTSAMPLEID\|...] | sample ids specified by idcontainers |
| pidc_[LIMSPSN\|MPI\|...] | one patientid of given idcontainer |
| methodname | the messprofile name |
| method | the messprofile code |
| sender | the EINS_CODE |

### patient

csv input columns for patient.

| csv column | comment |
| --- | --- |
| mainidc | the idcontainer from which the fhirid is built, can be left out if there is only one idcontainer given |
| pidc_[PSN\|LIMSPSN...] | patient ids specified by idcontainers |
| fhirid | a fhirid for the patient |
| organization_unit | the organization unit of the patient |
| study | the trial the patient is in |


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
