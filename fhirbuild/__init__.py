# fhirbuild: versuch, ein paar fhir funktionen zu skizzieren.
# usage: fhirbuild [specimen|observation|patient] in.csv outdir

# vielleicht ist fhir-building aber schon besser wo anders geloest,
# da muessten wir mal suchen, https://www.google.com/search?q=python+fhir+frameworks  
# vielleicht z.b. hier https://pypi.org/project/fhir.resources/

from datetime import date
import pandas as pd

# dateString returns fhir-compatible date string of date
def datestring(d: pd.Timestamp):
    if d == None: 
        return None
    date_str_format = d.strftime("%Y-%m-%dT%H:%M:%S%z")
    date_parts = date_str_format.split("+")
    date_part_tz = date_parts[1][0:2] + ":" + date_parts[1][2:4]
    result = date_parts[0] + "+" + date_part_tz
    return result

# fhirIdentifier returns a fhir identifier
def fhir_identifier(code:str=None, value:str=None, system:str="urn:centraxx"):
    return {
        "type": {
            "coding": [
                {
                    "system": system,
                    "code": code
                }
            ]
        },
        "value": value
    }

# fhir_extension returns a extension with url and puts everything from dict d in it
def fhir_extension(url:str, d):
    ext = {"url": url}
    for key in d:
        ext[key] = d[key]
    return ext


# use it:
# sampleid = fhirIdentifier(code: "SAMPLEID", value: sampleid)
# extsampleid = fhirIdentifier(code: "EXTSAMPLEID", value: extsampleid)
# fhirAliquot(..., identifiers: [sampleid, extsampleid], ...)

# fhir_sample builds a fhir aliquot. all arguments are named arguments.
def fhir_sample(
        category:str=None,
        collected_date:pd.Timestamp=None,
        concentration=None,
        container:str=None,
        derival_date:pd.Timestamp=None,
        fhirid=None,
        identifiers=None,
        initial_amount=None,
        location_path:str=None,
        organization_unit=None,        
        parent_fhirid=None,
        received_date:pd.Timestamp=None,
        reposition_date:pd.Timestamp=None,
        rest_amount=None,
        subject_limspsn=None,
        type=None,
        xposition:int=None,
        yposition:int=None,
):
    entry = {
        "fullUrl": f"Specimen/{fhirid}",
        "resource": {
            "resourceType": "Specimen",
            "id": f"{fhirid}",
            "extension": [
                fhir_extension(
                    "https://fhir.centraxx.de/extension/updateWithOverwrite",
                    { "valueBoolean": False }
                ),
                # reposition date added later
                # location path added later
                fhir_extension(
                    "https://fhir.centraxx.de/extension/sample/organizationUnit",
                    {
                        "valueReference": {
                        "identifier": {
                            "value": organization_unit
                        }
                    }
                }),
                fhir_extension(
                    "https://fhir.centraxx.de/extension/sample/derivalDate",
                    { "valueDateTime": datestring(derival_date) }
                ),
                fhir_extension(
                    "https://fhir.centraxx.de/extension/sampleCategory",
                    {
                        "valueCoding": {
                            "system": "urn:centraxx",
                            "code": category
                        }
                    }
                )
            ],
            "identifier": identifiers, # todo correct?
            "status": "available",
            "type": {
                "coding": [
                    # type (material) added later
                ]
            },
            "subject": {
                "identifier": fhir_identifier(code="LIMSPSN", value=subject_limspsn)
            },
            #"receivedTime": received_time # wird unten gesetzt
            "parent": [
                {
                    "reference": f"Specimen/{parent_fhirid}"
                }
            ],
            "collection": {
                # "collectedDateTime": collected_date, # wird unten gesetzt
                # "quantity": initial_amount # wird unten gesetzt
            },
            "container": [ 
                {
                    "identifier": [
                        {
                            "system": "urn:centraxx",
                            "value": container
                        }
                    ],
                    # "capacity": capacity, # wird nicht gesetzt, hat keinen einfluss auf cxx
                    # "specimenQuantity": rest_amount # wird unten gesetzt
                }
            ]
        },
        "request": {
            "method": "POST",
            "url": f"Specimen/{fhirid}",
        }
    }

    if xposition != None:
        for ext in entry['resource']['extension']:
            if ext.get("url") == "https://fhir.centraxx.de/extension/sample/sampleLocation":
                # Füge xpos am Anfang ein
                ext['extension'].insert(1, fhir_extension("https://fhir.centraxx.de/extension/sample/xPosition", { "valueInteger": xposition })) 

    if yposition != None:
        for ext in entry['resource']['extension']:
            if ext.get("url") == "https://fhir.centraxx.de/extension/sample/sampleLocation":
                # Füge ypos als zweites ein
                ext['extension'].insert(2, fhir_extension("https://fhir.centraxx.de/extension/sample/yPosition", { "valueInteger": yposition })) 

    # none checks for values
    
    if concentration is not None:
        entry["resource"]["extension"].append(fhir_extension(
            "https://fhir.centraxx.de/extension/sample/concentration",
            {"valueQuantity": concentration } 
        ))

    if location_path is not None:
        entry["resource"]["extension"].append(
            fhir_extension(
                    "https://fhir.centraxx.de/extension/sample/sampleLocation",
                    { "extension": [
                        fhir_extension(
                            "https://fhir.centraxx.de/extension/sample/sampleLocationPath",
                            {"valueString": location_path }
                        )
                    ]}
                )
        )
    
    if reposition_date is not None:
        entry["resource"]["extension"].append(fhir_extension(
            "https://fhir.centraxx.de/extension/sample/repositionDate",
            { "valueDateTime": f"{datestring(reposition_date)}" }
        ))

    if received_date is not None:
        entry["resource"]["receivedTime"] = datestring(received_date)

    print("collected_date: " + str(collected_date))
    if collected_date is not None:
        entry["resource"]["collection"]["collectedDateTime"] = datestring(collected_date)

    if initial_amount is not None:
        entry["resource"]["collection"]["quantity"] = initial_amount

    if rest_amount is not None:
        entry["resource"]["container"][0]["specimenQuantity"] = rest_amount

    if type is not None:
        entry["resource"]["type"]["coding"].append(
            {
                "system": "urn:centraxx",
                "code": type # material
            }
        )

    return entry

# fhir_quantity would build a fhir quantity
def fhir_quantity(value=None, unit=None, system: str="urn:centraxx"):
    # convert value to number
    if type(value) is str:
        value = float(value)
    quant = {
        "value": value,
        "unit": unit,
        "system": system
    }
    return quant

# fhir_aliquotgroup would build an aliquotgroup
def fhir_aliquotgroup(
        fhirid=None,        
        organization_unit=None,
        parent_sampleid=None,
        received_date=None,
        subject_limspsn=None,
        type=None
):
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
                "identifier": fhir_identifier(code="LIMSPSN", value=subject_limspsn)
            },
            #"receivedTime": wird speater befuellt
            "parent": [
                {
                    "identifier": fhir_identifier(code="SAMPLEID", value=parent_sampleid)
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

# genfhirid generates a fhirid from given string (e.g. sampleid)
def genfhirid(fromstr:str):
    # what does this need to do?
    #return pd.to_numeric((fromstr.factorize()[0] + 1 ) + 9999)
    return None

# fhir_bundle packs a list of entries into a fhir bundle
def fhir_bundle(entries:list):
    bundle = {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": entries
    }
    return bundle

# fhir_obs builds one fhir observation
def fhir_obs(
        component=[],
        delete:bool=False,
        effective_date_time:pd.Timestamp=None,
        fhirid:str=None,
        identifiers=[],
        method=None,
        methodname=None,
        sender:str=None,
        subject_psn:str=None
):

    #print("identifiers: " + str(identifiers))
    sampleid = None
    # get the sampleid
    for key, val in identifiers:
        if key == "SAMPLEID":
            sampleid = val
    if sampleid is None:
        print("error: no sample id")
        exit()

    # if no fhirid given, generate
    if fhirid is None:
        fhirid = genfhirid(sampleid)

    # if delete is set to true, change method to delete
    method = "POST" # write observation
    if delete == True:
        method = "DELETE"

    entry = {              
        "fullUrl": f"Observation/{fhirid}",
        "request": {
            "method": f"{method}",
            "url": f"Observation/{fhirid}"
        },
        "resource": {
            "resourceType": "Observation",
            "id": fhirid,
            "extension": [
            {
                "url": "https://fhir.centraxx.de/extension/updateWithOverwrite",
                "valueBoolean": True
            }
            ],
                
            "status": "unknown",
            "code": {
                "coding": [
                    {
                        "system": "urn:centraxx",
                        "code": methodname
                    }
                ]
            },
            "subject": {
                "identifier": {
                    "type": {
                        "coding": [
                            {
                                "system": "urn:centraxx",
                                "code": "LIMSPSN"
                            }
                        ]
                    },
                    "value": subject_psn
                }
            },
            "effectiveDateTime": datestring(effective_date_time),
            "method": {
                "coding": [
                    {
                        "system": "urn:centraxx",
                        "version": "1",
                        "code": method
                    }
                ]
            },
            "specimen": {
                "identifier": {
                    "type": {
                        "coding": [
                            {
                                "system": "urn:centraxx",
                                "code": "SAMPLEID"
                            }
                        ]
                    },
                    "value": sampleid
                }
            },
            "component": []
        }
    }

    # die messparameter landen in components
    for code, value in component:
        # don't put in empty values
        if value == "" or value is None:
            continue
        comp = {
            "code": {
                "coding": [
                    {
                        "system": "urn:centraxx",
                        "code": code
                    }
                ]
            },
            "valueString": value
        }
        entry["resource"]["component"].append(comp)


    entry["resource"]["component"].append({
    "code": {
        "coding": [
            {
                "system": "urn:centraxx",
                "code": "EINS_CODE"
            }
        ]
    },
    "valueString": sender
    })

    return entry



# fhir_patient baut einen patienten fhir aus werten
def fhir_patient(psn:str=None, study:str=None, organization_unit:str=None, fhirid:str=None):

    entry = {
   "resourceType": "Bundle",
   "type": "transaction",
   "entry": [ {
    "fullUrl": f"Patient/{fhirid}",
    "resource": {
      "resourceType": "Patient",
      "id": fhirid,
      "extension": [
        fhir_extension(
            "https://fhir.centraxx.de/extension/sample/organizationUnit",
            {
                "valueReference": {
                "identifier": {
                    "value": organization_unit
                }
            }
        })],
       "identifier": [ {
          "type": {
            "coding": [ {
              "system": "urn:centraxx",
              "code": "MPI"
            } ]
          },
        "value": psn
       } ],
       "generalPractitioner": [ {
         "identifier": {
          "value": study # study?
         }
        } ]
        },
        "request": {
        "method": "POST",
        "url": f"Patient/{fhirid}"
        }
    } ]
    }
    
    return entry
