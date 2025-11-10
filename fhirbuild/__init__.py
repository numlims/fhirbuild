# fhirbuild builds fhir

# vielleicht ist fhir-building aber schon besser wo anders geloest,
# da muessten wir mal suchen, https://www.google.com/search?q=python+fhir+frameworks  
# vielleicht z.b. hier https://pypi.org/project/fhir.resources/

from datetime import date, datetime, timezone, timedelta
import uuid

from tr import Sample, Identifier, Patient, Amount, Finding
from tr import Rec, BooleanRec, NumberRec, StringRec, DateRec, MultiRec, CatalogRec
import os
import math
import json



def write_patients(pats:list, dir:str, batchsize:int, wrap:bool=False, should_print:bool=False):
    """write_patients writes fhir resources of patients and returns a list containing the written directory."""

    # get the entries
    entries = []
    i = 0
    for pat in pats:
        entries.append(fhir_patient(pat, fhirid=str(i))) 
        i += 1

    # bundles the entries #bm
    bundles = bundle(entries, batchsize)

    # if print is set, print
    if should_print:
        print(json.dumps(bundles, indent=4))    

    # write the bundles
    return writeout(bundles, dir, "patient", wrap=wrap)

def write_samples(samples:list, dir:str, batchsize:int, wrap:bool=False, should_print:bool=False) -> list:
    """write_samples writes fhir resources of samples and returns a list containing the written directory."""

    # get the entries
    entries = []
    i = 0
    for sample in samples:
        entries.append(fhir_sample(sample, fhirid=str(i))) 
        i += 1
        
    # bundles the entries
    bundles = bundle(entries, batchsize)

    # if print is set, print
    if should_print:
        print(json.dumps(bundles, indent=4))
        
    # write the bundles
    return writeout(bundles, dir, "sample", wrap=wrap)

def write_observations(findings:list, dir:str, batchsize:int, wrap:bool=False, should_print:bool=False) -> list:
    """write_observations writes fhir resources of observations and returns a list containing the written directory.""" 

    # get the entries
    entries = []
    i = 0
    for finding in findings:
        entries.append(fhir_obs(finding, fhirid=i))
        i += 1

    # bundles the entries
    bundles = bundle(entries, batchsize)

    # if print is set, print
    if should_print:
        print(json.dumps(bundles, indent=4))


    # write the bundles
    return writeout(bundles, dir, "obs", wrap=wrap)


def bundle(entries, n) -> list:
    """bundle puts n entries in a bundle each."""

    bundles = []
    batch = []

    for i, entry in enumerate(entries):
        # after each n entries
        if i > 0 and i % n == 0:
            # append a bundle of the full batch
            bundles.append(fhir_bundle(batch))            
            # reset the batch
            batch = []
        # add to the batch
        batch.append(entry)

    # append the last batch
    bundles.append(fhir_bundle(batch))

    return bundles
    
    
def writeout(bundles:list, dir:str, type:str, wrap:bool=False):
    """writeout writes fhir bundles into a directory as seperate files, wrapping them into a timestamped directory if wrap is True."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # wrap the output into a timestamped directory if wished
    outdir = None
    if wrap:
        outdir = os.path.join(dir, timestamp)
    else:
        outdir = dir

    # create the output directory
    os.makedirs(outdir, exist_ok=True)    
    
    # how broad should the zero-place holder for the pagenumber in the filenames be? (eg for 999 pages 3, for 1000 pages 4)
    page_num_width = str(int(math.log10(len(bundles))) + 1)

    # write each bundle in a seperate file, using the same timestamp and increasing page numbers.
    for i, bundle in enumerate(bundles):
        fstring = "%s_%s_p%0" + page_num_width + "d.json"
        filename = fstring % (timestamp, type, i)
        # filename = timestamp + "_" + type + "_p" + str(i) + ".json"
        path = os.path.join(outdir, filename)
        with open(path, 'w', encoding='utf-8') as outf:
            json.dump(bundle, outf, indent=4, ensure_ascii=False)

    # for now, only return the directory path, not the paths of the written files
    return [outdir]


def datestring(d: datetime):
    """datestring returns fhir-compatible date string of date."""    
    if d == None: 
        return None
    # make the date time-zone aware (for utc +00:00 timezone)
    # d = d.replace(tzinfo=timezone.utc)
    # todo only if the date doesn't have a timezone
    # don't use the current timezone, cause the time zone of the sample should be kept, not the time zone where the user runs fhirbuild
    # d = d.replace(tzinfo=datetime.now().astimezone().tzinfo)
    d = d.replace(tzinfo=timezone(timedelta(hours=1)))
    return d.isoformat()

def fhir_identifier(identifier:Identifier, system:str="urn:centraxx"):
    """ fhirIdentifier returns a fhir identifier."""

    if identifier is None:
        return None
    if identifier.code is None:
        raise ValueError("identifier or code for fhir identifier is None")
    if  identifier.value is None or identifier.value == "" or identifier.value == "NULL":
        raise ValueError(f"value for fhir identifier {identifier.code} is '{identifier.value}'")
    return {
        "type": {
            "coding": [
                {
                    "system": system,
                    "code": identifier.code
                }
            ]
        },
        "value": identifier.value
    }

def fhir_extension(url:str, d):
    """fhir_extension returns a extension with url and puts everything from dict d in it."""
    ext = {"url": url}
    for key in d:
        ext[key] = d[key]
    return ext


def fhir_sample(sample:Sample=None,
                fhirid:str=None,
                update_with_overwrite:bool=False ): 
    """fhir_sample builds a fhir sample."""
    
    # print(f"fhir_sample: {sample.category} {fhirid} {sample.collected_date} {sample.xposition} {sample.yposition}")
    
    entry = {
        "fullUrl": f"Specimen/{fhirid}",
        "resource": {
            "resourceType": "Specimen",
            "id": f"{fhirid}",
            "extension": [
                fhir_extension(
                    "https://fhir.centraxx.de/extension/updateWithOverwrite",
                    { "valueBoolean": update_with_overwrite }
                ),
                # reposition date added later
                # location path added later
                fhir_extension(
                    "https://fhir.centraxx.de/extension/sample/organizationUnit",
                    {
                        "valueReference": {
                        "identifier": {
                            "value": str(sample.orga)
                        }
                    }
                }),
                fhir_extension(
                    "https://fhir.centraxx.de/extension/sampleCategory",
                    {
                        "valueCoding": {
                            "system": "urn:centraxx",
                            "code": str(sample.category)
                        }
                    }
                )
            ],
            "identifier": [ fhir_identifier(id) for id in sample.ids ],
            "status": "available",
            "type": {
                "coding": [
                    # type (material) added later
                ]
            },
            "subject": {
                "identifier": fhir_identifier(sample.patientid)
            },
            # "receivedTime": # added later
            "collection": {
                # "collectedDateTime": collected_date, # added later
                # "quantity": initial_amount # added later
            },
            "container": [ 
                {
                    "identifier": [
                        {
                            "system": "urn:centraxx",
                            "value": str(sample.receptacle)
                        }
                    ],
                    # "capacity": capacity, # wird nicht gesetzt, hat keinen einfluss auf cxx
                    # "specimenQuantity": # is restamount, added later
                }
            ]
        },
        "request": {
            "method": "POST",
            "url": f"Specimen/{fhirid}",
        }
    }

    if sample.locationpath is not None:
        entry["resource"]["extension"].append(
            fhir_extension(
                    "https://fhir.centraxx.de/extension/sample/sampleLocation",
                    { "extension": [
                        fhir_extension(
                            "https://fhir.centraxx.de/extension/sample/sampleLocationPath",
                            {"valueString": str(sample.locationpath) }
                        )
                    ]}
                )
        )



    if sample.derivaldate:
        entry["resource"]["extension"].append(fhir_extension(
            "https://fhir.centraxx.de/extension/sample/derivalDate",
            { "valueDateTime": datestring(sample.derivaldate) }
        ))

    if sample.xposition != None:
        for ext in entry['resource']['extension']:
    #       print(f"ext: {ext}")
            if ext.get("url") == "https://fhir.centraxx.de/extension/sample/sampleLocation":
                # Füge xpos am Anfang ein
             #   print(f"xpos found, inserting xposition {xposition}")
                ext['extension'].insert(1, fhir_extension("https://fhir.centraxx.de/extension/sample/xPosition", { "valueInteger": int(sample.xposition) })) 

    if sample.yposition != None:
        for ext in entry['resource']['extension']:
       #    print(f"ext: {ext}")
            if ext.get("url") == "https://fhir.centraxx.de/extension/sample/sampleLocation":
                # Füge ypos als zweites ein
              #  print(f"ypos found, inserting yposition {yposition}")
                ext['extension'].insert(2, fhir_extension("https://fhir.centraxx.de/extension/sample/yPosition", { "valueInteger": int(sample.yposition) })) 

    # none checks for values
    
    if sample.parentid is not None:
        entry["resource"]["parent"] = [
            {
                "identifier": fhir_identifier(sample.parentid)
            }
        ]
        
    if sample.concentration is not None:
        entry["resource"]["extension"].append(fhir_extension(
            "https://fhir.centraxx.de/extension/sample/concentration",
            {"valueQuantity": str(sample.concentration) } 
        ))

    if sample.samplingdate is not None:
        entry["resource"]["collection"]["collectedDateTime"] = datestring(sample.samplingdate    )
  
    if sample.receiptdate is not None:
        entry["resource"]["receivedTime"] = datestring(sample.receiptdate)

    if sample.repositiondate is not None:
        entry["resource"]["extension"].append(fhir_extension(
            "https://fhir.centraxx.de/extension/sample/repositionDate",
            { "valueDateTime": f"{datestring(sample.repositiondate)}" }
        ))

    if sample.initialamount is not None:
        entry["resource"]["collection"]["quantity"] = fhir_quantity(sample.initialamount)

    if sample.restamount is not None:
        entry["resource"]["container"][0]["specimenQuantity"] = fhir_quantity(sample.restamount)

    if sample.type is not None:
        entry["resource"]["type"]["coding"].append(
            {
                "system": "urn:centraxx",
                "code": str(sample.type) # material
            }
        )

    return entry

def fhir_quantity(amount:Amount=None, system:str="urn:centraxx"):
    """fhir_quantity builds a fhir quantity."""
    quant = {
        "value": float(amount.value) if amount.value is not None else None,
        "unit": str(amount.unit) if amount.unit is not None else None,
        "system": system
    }
    return quant

def fhir_aliquotgroup(
        fhirid=None,        
        organization_unit=None,
        parent_sampleid=None,
        received_date=None,
        subject_id=None,
        type=None
):
    """fhir_aliquotgroup would build an aliquotgroup."""
    entry = {
        "fullUrl": f"Specimen/{fhirid}",
        "resource": {
            "resourceType": "Specimen",
            "id": f"{fhirid}",
            "extension": [
                {
                    "url": "https://fhir.centraxx.de/extension/updateWithOverwrite",
                    "valueBoolean": False
                },
                {
                    "url": "https://fhir.centraxx.de/extension/sample/organizationUnit",
                    "valueReference": {
                        "identifier": {
                            "value": organization_unit
                        }
                    }
                },
                {
                    "url": "https://fhir.centraxx.de/extension/sampleCategory",
                    "valueCoding": {
                        "system": "urn:centraxx",
                        "code": "ALIQUOTGROUP"
                    }
                },
                {
                    "url": "https://fhir.centraxx.de/extension/sprec",
                    "extension": [{
                        "url": "https://fhir.centraxx.de/extension/sprec/useSprec",
                        "valueBoolean": False
                    }]
                }
            ],
            "status": "unavailable",
            "type": {
                "coding": [
                    {
                        "system": "urn:centraxx",
                        "code": type
                    }
                ]
            },
            "subject": {
                "identifier": fhir_identifier(Identifier(code="LIMSPSN", value=subject_id))
            },
            # "receivedTime": added later
            "parent": [
                {
                    "identifier": fhir_identifier(Identifier(code="SAMPLEID", value=parent_sampleid))
                }
            ],

        },
        "request": {
            "method": "POST",
            "url": f"Specimen/{fhirid}",
        }
    }

    if received_date is not None:
        entry["resource"]["receivedTime"] = datestring(received_date)


    return entry


def genfhirid(fromstr:str):
    """genfhirid generates a fhirid from given string (e.g. sampleid)."""
    # Generate a deterministic ID based on the input string
   
    namespace = uuid.NAMESPACE_DNS  # Use DNS namespace for UUID generation
    if fromstr is None or fromstr == "":
        raise ValueError("fromstr must not be None or empty")

    return str(uuid.uuid5(namespace, fromstr))  # Use uuid5 for deterministic ID generation
    

def fhir_bundle(entries:list):
    """fhir_bundle packs a list of entries into a fhir bundle."""
    bundle = {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": entries
    }
    return bundle


def fhir_obs(
        finding:Finding=None,
        fhirid:str=None,        
        # effective_date_time:datetime=None,
        update_with_overwrite:bool=False,
        delete:bool=False        
):
    """fhir_obs builds one fhir observation."""
    if finding.sampleid is None:
        print("error: no sample id")
        exit()

    # if no fhirid given, generate
    if fhirid is None:
        fhirid = genfhirid(sampleid)

    # if delete is set to true, change method to delete
    fhirmethod = "POST" # write observation
    if delete == True:
        fhirmethod = "DELETE"

    entry = {              
        "fullUrl": f"Observation/{fhirid}",
        "request": {
            "method": f"{fhirmethod}",
            "url": f"Observation/{fhirid}"
        },
        "resource": {
            "resourceType": "Observation",
            "id": str(fhirid),
            "extension": [
            {
                "url": "https://fhir.centraxx.de/extension/updateWithOverwrite",
                "valueBoolean": update_with_overwrite
            }
            ],
                
            "status": "unknown",
            "code": {
                "coding": [
                    {
                        "system": "urn:centraxx",
                        "code": str(finding.methodname)
                    }
                ]
            },
            "subject": {
                "identifier": fhir_identifier(finding.patientid)
            },
            "effectiveDateTime": datestring(finding.creationdate), #  todo right?
            "method": {
                "coding": [
                    {
                        "system": "urn:centraxx",
                        "version": "1",
                        "code": str(finding.method)
                    }
                ]
            },
            "specimen": {
                "identifier": fhir_identifier(finding.sampleid)
            },
            "component": []
        }
    }

    # die messparameter landen in components
    for code, rec in finding.recs.items():
        # don't put in empty values
        if rec is None:
            continue
        comp = {
            "code": {
                "coding": [
                    {
                        "system": "urn:centraxx",
                        "code": str(code)
                    }
                ]
            }
        }
        # put something different depending on the type of the rec
        if type(rec) is BooleanRec:
            comp["valueBoolean"] = bool(rec.value)
        if type(rec) is NumberRec: # are numbers always turned to quantities? # todo
            comp["valueQuantity"] = {
                # shouldn't NumberRec.value already be a float?
                "value": float(rec.value) if rec.value is not None else 0 # todo setting 0 is not right actually, cause the db returns NULL, but None isn't accepted by fhirimporter 
            }
            # set the unit only if it is there
            if rec.unit is not None and "valueQuantity" in comp:
                comp["valueQuantity"]["unit"] = rec.unit # from laborvalue

        if type(rec) is StringRec:
            comp["valueString"] = str(rec.value)
            # somehow strings may not be empty or null, so don't add the component if that's the case? todo how to delete a string?
            if str(rec.value) is None or str(rec.value) == "":
                continue # continue without adding the component
        if type(rec) is DateRec: 
            comp["valueDateTime"] = datestring(rec.value) 
        if type(rec) is MultiRec:
            # collect the values 
            a = []
            for val in rec.values:
                a.append({
                    "system": "urn:centraxx:CodeSystem/UsageEntry-x", # sometimes the x is oid, but doesn't seem to need to be
                    "code": str(val)
                    })
            # put the collected values into the coding field of a value codeable concept
            comp["valueCodeableConcept"] = {
                "coding": a
            }
        if type(rec) is CatalogRec:
            # collect the values 
            a = []
            for val in rec.values:
                a.append({
                    "system": f"urn:centraxx:CodeSystem/ValueList-{rec.catalog}", # here apparently the catalog code is needed
                    "code": str(val)
                    })
            # put the collected values into the coding field of a value codeable concept
            comp["valueCodeableConcept"] = {
                "coding": a
            }
            

        entry["resource"]["component"].append(comp)

    # add the sender
    if finding.sender:
        entry["resource"]["component"].append({
        "code": {
            "coding": [
                {
                    "system": "urn:centraxx",
                    "code": "EINS_CODE"
                }
            ]
        },
        "valueString": str(finding.sender)
        })

    return entry



def fhir_patient(patient:Patient=None,
                 fhirid:str=None,
                 update_with_overwrite:bool=False ):
    """fhir_patient baut einen patienten."""

    entry = {
        "fullUrl": f"Patient/{fhirid}",
        "resource": {
            "resourceType": "Patient",
            "id": fhirid,
            "extension": [{
                "url": "https://fhir.centraxx.de/extension/updateWithOverwrite",
                "valueBoolean": update_with_overwrite
            }],
            "identifier": [ fhir_identifier(id) for id in patient.ids ],
            "generalPractitioner": [ {
                "identifier": {
                    "value": str(patient.orga)
                }
            } ]
        },
        "request": {
            "method": "POST",
            "url": f"Patient/{fhirid}"
        }
    } 
    
    return entry
