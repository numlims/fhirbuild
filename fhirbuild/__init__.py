# fhirbuild builds fhir

# vielleicht ist fhir-building aber schon besser wo anders geloest,
# da muessten wir mal suchen, https://www.google.com/search?q=python+fhir+frameworks  
# vielleicht z.b. hier https://pypi.org/project/fhir.resources/

from datetime import date, datetime

from tram import Sample, Identifier, Patient, Amount, Finding
from tram import Rec, BooleanRec, NumberRec, StringRec, DateRec, MultiRec, CatalogRec
import os
import math
import json
import jsonpickle
from fhirbuild.help import datestring, genfhirid


def write_patients(pats:list, dir:str, batchsize:int, wrap:bool=False, should_print:bool=False, cxx:int=3):
    """write_patients writes fhir resources of patients and returns a list containing the written directory."""

    # get the entries
    entries = []
    for pat in pats:
        # make a fhirid that depends on the limspsn, the fhirid is  
        entries.append(fhir_patient(pat))

    # bundles the entries 
    bundles = bundle(entries, batchsize, restype="Patient", cxx=cxx)

    # if print is set, print
    if should_print:
        print(json.dumps(bundles, indent=4))    

    # write the bundles
    return writeout(bundles, dir, "patient", wrap=wrap)

def write_samples(samples:list, dir:str, batchsize:int, wrap:bool=False, should_print:bool=False, cxx:int=3) -> list:
    """write_samples writes fhir resources of Samples and returns a list containing the written directory. it fills in missing fhirids."""

    # fill in fhirids, taking parent-child relations into account.
    _fill_in_fhirids(samples)

    # collect the entries
    entries = [ ]
    for sample in samples:
        # build aliquot group or standard sample
        if sample.category == "ALIQUOTGROUP":
            entry = fhir_aliquotgroup(sample)
        elif sample.category == "MASTER" or sample.category == "DERIVED":
            entry = fhir_specimen(sample)
        else:
            raise Exception(f"sample category {sample.category} is not allowed.")

        # append the entry
        entries.append(entry)

    # bundles the entries
    bundles = bundle(entries, batchsize, restype="Sample", cxx=cxx)

    # if print is set, print
    if should_print:
        print(json.dumps(bundles, indent=4))
        
    # write the bundles
    return writeout(bundles, dir, "sample", wrap=wrap)


def _fill_in_fhirids(samples):
    """_fill_in_fhirids fills in missing fhirids for Sample instances.  assumes sorted input, parents followed by children.  the fhirids are generated from each Sample's id.  for aliquotgroups, the fhirid is generated from the parent sampleid and the material of the aliquotgroup.  child samples should referenence their parents via the .parent:Idiable field.  for aliquotgroups .parent should contain an Identifier referencing the primary parent with either 'fhirid' or main idc code, for aliquots .parent should contain an Identifier referencing the parent aliquotgroup with either 'fhirid' or 'index' code, since aliquotgroups don't come with sampleids."""

    # remember the fhirids by oid
    fhiridbyoid = {}
    # remember the fhirids by index
    fhiridbyindex = {}

    # collect the entries
    i = 0
    for sample in samples:
        #print(f"i: {i}")
        #print(jsonpickle.encode(sample, unpicklable=False, indent=4))
        #print(sample.parent.ids[0].code + ", " + sample.parent.ids[1].code)
        # take the fhirid if passed
        fhirid = sample.id("fhirid")
        
        # if no fhirid, generate a fhirid
        if fhirid is None:
            # if it's an aliquotgroup, generate a fhirid based on the parent id and aliquotgroup type.
            if sample.category == "ALIQUOTGROUP":
                fhirid = genfhirid(sample.parent.id() + sample.type)
            else:
                # else generate the fhirid from the sampleid
                fhirid = genfhirid(sample.id())
                
            sample.ids.append( Identifier(code="fhirid", id=fhirid) )

        # remember the fhirid of this aliquotgroup for later use by its children to reference it.
        # if the sample comes with an oid, remember the fhirid by oid.
        # if the sample comes with an index, remember the fhirid by index.
        # if it comes with neither, we assume that the fhirid references are already complete and we don't need to set anything 
        if sample.id("oid") is not None:
            fhiridbyoid[sample.id("oid")] = fhirid
        if sample.id("index") is not None:
            fhiridbyindex[sample.id("index")] = fhirid

        # the references of aliquotgroups to primary samples should be ok, cause primaries can be referenced via sampleid.

        # the references of aliquots to parent aliquotgroups probably need to be set here, cause aliquotgroups are referenced by that fhirids were just generated (except if all fhirids and references were passed to the function)

        # are we a derived?
        if sample.category == "DERIVED":
            parent = sample.parent
            if parent is None:
                print(f"error: derived sample {sample.id()} has no parent.")
                # abort?

            # do we need a fhirid of the parent?
            if parent.id("fhirid") is None:
                pfhirid = None

                # get the remembered fhirid of the parent via oid or index
                poid = parent.id("oid")
                pindex = parent.id("index")
                if poid is not None and poid in fhiridbyoid:
                    pfhirid = fhiridbyoid[poid]
                elif pindex is not None and pindex in fhiridbyindex:
                    pfhirid = fhiridbyindex[pindex]

                # error if we didn't find a fhirid
                if pfhirid is None:
                    print(f"error: can't find fhirid for parent aliquotgroup of aliquot {sample.id()}.  does it come before the sample and is it referenced properly via oid or index?")
                    # abort?

            # add the remembered fhirid for the parent
            if pfhirid is not None:
                sample.parent.ids.append( Identifier(id=pfhirid, code="fhirid") )

        # increase the index
        i += 1


def write_observations(findings:list, dir:str, batchsize:int, wrap:bool=False, should_print:bool=False, cxx=3) -> list:
    """write_observations writes fhir resources of observations and returns a list containing the written directory.""" 

    # get the entries
    entries = []
    i = 0
    for finding in findings:
        # make a fhirid from sampleid and method code
        #print("sampleid: " + finding.sample.id())
        #print("method: " + finding.method)
        fhirid = genfhirid(finding.sample.id() + finding.method)
        entries.append(fhir_obs(finding, fhirid=fhirid))
        i += 1

    # bundles the entries
    bundles = bundle(entries, batchsize, restype="Observation", cxx=3)

    # if print is set, print
    if should_print:
        print(json.dumps(bundles, indent=4))

    # write the bundles
    return writeout(bundles, dir, "obs", wrap=wrap)


def bundle(entries, n, restype:str=None, cxx:int=None) -> list:
    """bundle puts n entries in a bundle each."""

    bundles = []
    batch = []

    for i, entry in enumerate(entries):
        # after each n entries
        if i > 0 and i % n == 0:
            # append a bundle of the full batch
            bundles.append(fhir_bundle(batch, restype=restype, cxx=cxx))
            # reset the batch
            batch = []
        # add to the batch
        batch.append(entry)

    # append the last batch
    bundles.append(fhir_bundle(batch, restype=restype, cxx=cxx))

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



def fhir_identifier(identifier:Identifier, system:str="urn:centraxx"):
    """ fhirIdentifier returns a fhir identifier."""

    if identifier is None:
        return None
    if identifier.code is None:
        raise ValueError("identifier or code for fhir identifier is None")

    id = identifier.id
    # why also exclude 'NULL'?    
    #if  id is None or id == "" or id == "NULL":
    # why error on missing values? is it because fhirimport doesn't take no null values? but that's not quite in the scope of fhirbuild to know, is it?
    if id is None or id == "":    
        raise ValueError(f"id for fhir identifier {identifier.code} is '{id}'")
    
    # set the id to None if 'NULL' was given? 
    if id == 'NULL':
        id = None
        
    return {
        "type": {
            "coding": [
                fhir_coding(system=system, code=identifier.code)
            ]
        },
        "value": identifier.id
    }

def fhir_coding(code:str=None, system:str="urn:centraxx"):
    """fhir_coding returns a fhir coding with code and system."""
    return {
        "system": system,
        "code": code
    }

def fhir_extension(url:str, d):
    """fhir_extension returns a extension with url and puts everything from dict d in it."""
    ext = {"url": url}
    for key in d:
        ext[key] = d[key]
    return ext


def fhir_specimen(sample:Sample=None,
                update_with_overwrite:bool=False ): 
    """fhir_specimen builds a fhir specimen. pass the sample's fhirid as an Identifier with code 'fhirid' for the sample, and, for deriveds, the fhirid of its parent aliquotgroup as an Identifier with code 'fhirid' of sample.parent. by tying the fhirids directly to the sample, calling methods can receive fhirids for lists of Samples e.g. from csv without having to sneak them in via an extra argument."""

    # todo also build aliquotgroups?
    
    # print(f"fhir_specimen: {sample.category} {fhirid} {sample.collected_date} {sample.xposition} {sample.yposition}")
    
    entry = {
        "fullUrl": f"Specimen/{sample.id('fhirid')}",
        "resource": {
            "resourceType": "Specimen",
            "id": f"{sample.id('fhirid')}",
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
                        "valueCoding": fhir_coding(code=str(sample.category)) 
                    }
                )
            ],
            "identifier": [], # filled later
            "status": "available",
            "type": {
                "coding": [
                    # type (material) added later
                ]
            },
            "subject": {
                "identifier": fhir_identifier(sample.patient.identifier())
            },
            # "receivedTime": # added later
            # "parent": [ ], # filled later
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
            "url": f"Specimen/{sample.id('fhirid')}",
        }
    }

    # fill the identifiers.  skip the oid for now
    for id in sample.ids:
         if id.code != "oid" and id.code != "fhirid" and id.code != "index": # todo move the filtering into _fill_fhirid method?
             entry["resource"]["identifier"].append(fhir_identifier(id))
    
    # bundle the values that end up in the sprec extension

    sprecext = {
        "url": "https://fhir.centraxx.de/extension/sprec",
        "extension": [
            {
                "url": "https://fhir.centraxx.de/extension/sprec/useSprec",
                "valueBoolean": True
            }
        ]
    }

    # none checks for values.
    # the fhir importer apparently doesn't import null values, so only put in values if they aren't none.
    # this would make deleting values impossible at the moment.
    # does cxx4 fhir import accept null values?


    # first stock processing (centrifugation)
    
    if sample.stockprocessing is not None:
        # append the stock processing sprec
        sprecext["extension"].append( fhir_extension(
            "https://fhir.centraxx.de/extension/sprec/stockProcessing",
            { "valueCoding": fhir_coding(code=sample.stockprocessing) }
        ))

    if sample.stockprocessingdate is not None:
        # append the stock processing date sprec
        sprecext["extension"].append( fhir_extension(
            "https://fhir.centraxx.de/extension/sprec/stockProcessingDate",
            { "valueDateTime": datestring(sample.stockprocessingdate) }
        ))

    # second stock processing (centrifugation)
    
    if sample.secondprocessing is not None:
        # append the second processing sprec
        sprecext["extension"].append( fhir_extension(
            "https://fhir.centraxx.de/extension/sprec/secondProcessing",
            { "valueCoding": fhir_coding(code=sample.secondprocessing) }
        ))

    if sample.secondprocessingdate is not None:
        # append the second processing date sprec
        sprecext["extension"].append( fhir_extension(
            "https://fhir.centraxx.de/extension/sprec/secondProcessingDate",
            { "valueDateTime": datestring(sample.secondprocessingdate) }
        ))
        
                
    # add the sprec extension to the extensions
    entry["resource"]["extension"].append(sprecext)


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

            if ext.get("url") == "https://fhir.centraxx.de/extension/sample/sampleLocation":
                # füge xpos am Anfang ein
                # print(f"xpos found, inserting xposition {xposition}")
                ext['extension'].insert(1, fhir_extension("https://fhir.centraxx.de/extension/sample/xPosition", { "valueInteger": int(sample.xposition) })) 

    if sample.yposition != None:
        for ext in entry['resource']['extension']:
            if ext.get("url") == "https://fhir.centraxx.de/extension/sample/sampleLocation":
                # füge ypos als zweites ein
                # print(f"ypos found, inserting yposition {yposition}")
                ext['extension'].insert(2, fhir_extension("https://fhir.centraxx.de/extension/sample/yPosition", { "valueInteger": int(sample.yposition) })) 


    # if the parent's fhirid is given, use it to reference the parent, else use the sampleid of the parent.
    if sample.parent is not None:
        entry["resource"]["parent"] = []

    if sample.parent is not None and sample.parent.id('fhirid') is not None:
        entry["resource"]["parent"].append(
            {
                "reference": f"Specimen/{sample.parent.id('fhirid')}"
            }
        )
    elif sample.parent is not None: # todo check it's not none?
        entry["resource"]["parent"].append(
            {
                "identifier": fhir_identifier(sample.parent.identifier())
            }
        )

    if sample.concentration is not None:
        entry["resource"]["extension"].append(fhir_extension(
            "https://fhir.centraxx.de/extension/sample/concentration",
            {"valueQuantity": str(sample.concentration) } 
        ))

    if sample.samplingdate is not None:
        entry["resource"]["collection"]["collectedDateTime"] = datestring(sample.samplingdate)
  
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
        entry["resource"]["type"]["coding"].append( fhir_coding(code=str(sample.type)) ) # material

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
        sample:Sample=None,
        fhirid:str=None,
        parent_fhirid:str=None,
        update_with_overwrite:bool=False
):
    """fhir_aliquotgroup builds a fhir aliquotgroup from a Sample. pass fhirids as Identifiers with code "fhirid" of sample and sample.parent."""
    entry = {
        "fullUrl": f"Specimen/{sample.id('fhirid')}",
        "resource": {
            "resourceType": "Specimen",
            "id": f"{sample.id('fhirid')}",
            "extension": [
                {
                    "url": "https://fhir.centraxx.de/extension/updateWithOverwrite",
                    "valueBoolean": update_with_overwrite
                },
                {
                    "url": "https://fhir.centraxx.de/extension/sample/organizationUnit",
                    "valueReference": {
                        "identifier": {
                            "value": str(sample.orga)
                        }
                    }
                },
                {
                    "url": "https://fhir.centraxx.de/extension/sampleCategory",
                    "valueCoding": fhir_coding(code="ALIQUOTGROUP")
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
                    fhir_coding(code=sample.type)
                ]
            },
            "subject": {
                "identifier": fhir_identifier(sample.patient.identifier())
            },
            # "receivedTime": added later
            "parent": [ ], # filled later 

        },
        "request": {
            "method": "POST",
            "url": f"Specimen/{sample.id('fhirid')}"
        }
    }

    # if the parent's fhirid is given, use it to reference the parent, else use the sampleid of the parent

    if sample.parent is not None and sample.parent.id('fhirid') is not None:
        entry["resource"]["parent"].append(
            {
                "reference": f"Specimen/{sample.parent.id('fhirid')}"
            }
        )
    elif sample.parent is not None: 
        entry["resource"]["parent"].append(
            {
                "identifier": fhir_identifier(sample.parent.identifier())
            }
        )


    if sample.receiptdate is not None:
        entry["resource"]["receivedTime"] = datestring(sample.receiptdate)

    return entry



def fhir_bundle(entries:list, restype:str=None, cxx:int=3):
    """fhir_bundle packs a list of entries into a fhir bundle."""
    bundle = {
        "type": "transaction",
        "entry": entries
    }
    # set resource type to bundle for cxx3, to the specific type for cxx4
    if cxx == 3:
        bundle["resourceType"] = "Bundle"
    elif cxx == 4:
        bundle["resourceType"] = restype

    return bundle


def fhir_obs(
        finding:Finding=None,
        fhirid:str=None,
        update_with_overwrite:bool=False,
        delete:bool=False        
):
    """fhir_obs builds a fhir observation from Finding."""
    if finding.sample is None:
        print("error: no sample id")
        exit()

    # if no fhirid given, generate
    if fhirid is None:
        fhirid = genfhirid(finding.sample.id())

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
                    fhir_coding(code=str(finding.methodname))
                ]
            },
            "subject": {
                "identifier": fhir_identifier(finding.patient.identifier())
            },
            "effectiveDateTime": datestring(finding.findingdate), 
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
                "identifier": fhir_identifier(finding.sample.identifier())
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
                    fhir_coding(code=str(code))
                ]
            }
        }
        # put something different depending on the type of the rec
        if type(rec) is BooleanRec:
            comp["valueBoolean"] = bool(rec.rec)
        if type(rec) is NumberRec: # are numbers always turned to quantities? # todo
            comp["valueQuantity"] = {
                # shouldn't NumberRec.value already be a float?
                "value": float(rec.rec) if rec.value is not None else 0 # todo setting 0 is not right actually, cause the db returns NULL, but None isn't accepted by fhirimporter 
            }
            # set the unit only if it is there
            if rec.unit is not None and "valueQuantity" in comp:
                comp["valueQuantity"]["unit"] = rec.unit # from laborvalue

        if type(rec) is StringRec:
            comp["valueString"] = str(rec.rec)
            # somehow strings may not be empty or null, so don't add the component if that's the case? todo how to delete a string?
            if str(rec.rec) is None or str(rec.rec) == "":
                continue # continue without adding the component
        if type(rec) is DateRec: 
            comp["valueDateTime"] = datestring(rec.rec) 
        if type(rec) is MultiRec:
            # collect the values 
            a = []
            for val in rec.rec:
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
            for val in rec.rec:
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
                fhir_coding(code="EINS_CODE")
            ]
        },
        "valueString": str(finding.sender)
        })

    return entry



def fhir_patient(patient:Patient=None, update_with_overwrite:bool=False):
    """fhir_patient baut einen patienten."""

    # if there isn't a fhirid, make it based on the patient's main id
    # the fhirid needs to be unique for the patient, it is also written to the db and patient records can be updated with it
    fhirid = patient.id("fhirid")
    if fhirid is None:
        fhirid = genfhirid(patient.id())

    entry = {
        "fullUrl": f"Patient/{fhirid}",
        "resource": {
            "resourceType": "Patient",
            "id": fhirid,
            "extension": [{
                "url": "https://fhir.centraxx.de/extension/updateWithOverwrite",
                "valueBoolean": update_with_overwrite
            }],
            "identifier": [], # filled later
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

    for id in patient.ids:
        if id.code != "oid" and id.code != "fhirid":
             entry["resource"]["identifier"].append(fhir_identifier(id))

    
    return entry
