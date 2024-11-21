# fhirbuild

build fhir jsons from code or csv.

usage: fhirbuild <observation|specimen> <in csv> <out dir>

example: fhirbuild observation GSA_prep\out\gsa-korr.csv tmp-dir

build:

python3 -m build

install:

pip install dist/*.whl