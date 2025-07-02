# fhir examples

master (primary) sample:

```
{
    "fullUrl": "Specimen/12248",
    "resource": {
      "resourceType": "Specimen",
      "id": "12248",
      "extension": [ {
        "url": "https://fhir.centraxx.de/extension/updateWithOverwrite",
        "valueBoolean": false
      }, {
        "url": "https://fhir.centraxx.de/extension/sample/repositionDate",
        "valueDateTime": "2020-12-22T10:09:00.000+01:00"
      }, {
        "url": "https://fhir.centraxx.de/extension/sample/sampleLocation",
        "extension": [ {
          "url": "https://fhir.centraxx.de/extension/sample/sampleLocationPath",
          "valueString": "NUM --> Klinikum Würzburg --> Ultra-Tiefkühlschrank POP -80°C"
        } ]
      }, {
        "url": "https://fhir.centraxx.de/extension/sample/organizationUnit",
        "valueReference": {
          "identifier": {
            "value": "NUM_W_SUEP"
          }
        }
      }, {
        "url": "https://fhir.centraxx.de/extension/sampleCategory",
        "valueCoding": {
          "system": "urn:centraxx",
          "code": "MASTER"
        }
      }, {
        "url": "https://fhir.centraxx.de/extension/sprec",
        "extension": [ {
          "url": "https://fhir.centraxx.de/extension/sprec/useSprec",
          "valueBoolean": false
        }, {
          "url": "https://fhir.centraxx.de/extension/sprec/stockProcessing",
          "valueCoding": {
            "system": "urn:centraxx",
            "code": "Sprec-B"
          }
        }, {
          "url": "https://fhir.centraxx.de/extension/sprec/stockProcessingDate",
          "valueDateTime": "2020-12-22T11:12:42.000+01:00"
        } ]
      } ],
      "identifier": [ {
        "type": {
          "coding": [ {
            "system": "urn:centraxx",
            "code": "EXTSAMPLEID"
          } ]
        },
        "value": "ST9908777961"
      }, {
        "type": {
          "coding": [ {
            "system": "urn:centraxx",
            "code": "SAMPLEID"
          } ]
        },
        "value": "1067650203"
      } ],
      "status": "unavailable",
      "type": {
        "coding": [ {
          "system": "urn:centraxx",
          "code": "CIT"
        } ]
      },
      "subject": {
        "identifier": {
          "type": {
            "coding": [ {
              "system": "urn:centraxx",
              "code": "LIMSPSN"
            } ]
          },
          "value": "lims_989077906"
        }
      },
      "receivedTime": "2020-12-22T11:11:51+01:00",
      "collection": {
        "quantity": {
          "value": 1.0000,
          "unit": "PC",
          "system": "urn:centraxx"
        }
      },
      "container": [ {
        "identifier": [ {
          "system": "urn:centraxx",
          "value": "ORG"
        } ],
        "capacity": {
          "value": 1.00,
          "unit": "PC",
          "system": "urn:centraxx"
        },
        "specimenQuantity": {
          "value": 0.0000,
          "unit": "PC",
          "system": "urn:centraxx"
        }
      } ]
    },
    "request": {
      "method": "POST",
      "url": "Specimen/12248"
    }
  }
```

aliquotgroup:


```
  {
    "fullUrl": "Specimen/12254",
    "resource": {
      "resourceType": "Specimen",
      "id": "12254",
      "extension": [ {
        "url": "https://fhir.centraxx.de/extension/updateWithOverwrite",
        "valueBoolean": false
      }, {
        "url": "https://fhir.centraxx.de/extension/sample/sampleLocation",
        "extension": [ {
          "url": "https://fhir.centraxx.de/extension/sample/sampleLocationPath",
          "valueString": "NUM --> Klinikum Würzburg --> Ultra-Tiefkühlschrank POP -80°C"
        } ]
      }, {
        "url": "https://fhir.centraxx.de/extension/sample/organizationUnit",
        "valueReference": {
          "identifier": {
            "value": "NUM_W_SUEP"
          }
        }
      }, {
        "url": "https://fhir.centraxx.de/extension/sampleCategory",
        "valueCoding": {
          "system": "urn:centraxx",
          "code": "ALIQUOTGROUP"
        }
      }, {
        "url": "https://fhir.centraxx.de/extension/sprec",
        "extension": [ {
          "url": "https://fhir.centraxx.de/extension/sprec/useSprec",
          "valueBoolean": false
        }, {
          "url": "https://fhir.centraxx.de/extension/sprec/stockProcessing",
          "valueCoding": {
            "system": "urn:centraxx",
            "code": "Sprec-B"
          }
        } ]
      } ],
      "status": "unavailable",
      "type": {
        "coding": [ {
          "system": "urn:centraxx",
          "code": "CIT"
        } ]
      },
      "subject": {
        "identifier": {
          "type": {
            "coding": [ {
              "system": "urn:centraxx",
              "code": "LIMSPSN"
            } ]
          },
          "value": "lims_989077906"
        }
      },
      "receivedTime": "2020-12-22T11:11:51+01:00",
      "parent": [ {
        "identifier": {
          "type": {
            "coding": [ {
              "code": "SAMPLEID"
            } ]
          },
          "value": "1067650203"
        }
      } ],
      "collection": {
        "quantity": {
          "system": "urn:centraxx"
        }
      },
      "container": [ {
        "specimenQuantity": {
          "system": "urn:centraxx"
        }
      } ]
    },
    "request": {
      "method": "POST",
      "url": "Specimen/12254"
    }
  }
```

aliquot (derived):

```
{
    "fullUrl": "Specimen/12255",
    "resource": {
      "resourceType": "Specimen",
      "id": "12255",
      "extension": [ {
        "url": "https://fhir.centraxx.de/extension/updateWithOverwrite",
        "valueBoolean": false
      }, {
        "url": "https://fhir.centraxx.de/extension/sample/repositionDate",
        "valueDateTime": "2020-12-22T13:06:08.000+01:00"
      }, {
        "url": "https://fhir.centraxx.de/extension/sample/sampleLocation",
        "extension": [ {
          "url": "https://fhir.centraxx.de/extension/sample/sampleLocationPath",
          "valueString": "NUM --> Klinikum Würzburg --> Ultra-Tiefkühlschrank POP -80°C"
        } ]
      }, {
        "url": "https://fhir.centraxx.de/extension/sample/organizationUnit",
        "valueReference": {
          "identifier": {
            "value": "NUM_W_SUEP"
          }
        }
      }, {
        "url": "https://fhir.centraxx.de/extension/sample/derivalDate",
        "valueDateTime": "2020-12-22T11:40:01.000+01:00"
      }, {
        "url": "https://fhir.centraxx.de/extension/sampleCategory",
        "valueCoding": {
          "system": "urn:centraxx",
          "code": "DERIVED"
        }
      }, {
        "url": "https://fhir.centraxx.de/extension/sprec",
        "extension": [ {
          "url": "https://fhir.centraxx.de/extension/sprec/useSprec",
          "valueBoolean": false
        }, {
          "url": "https://fhir.centraxx.de/extension/sprec/stockProcessing",
          "valueCoding": {
            "system": "urn:centraxx",
            "code": "Sprec-B"
          }
        } ]
      } ],
      "identifier": [ {
        "type": {
          "coding": [ {
            "system": "urn:centraxx",
            "code": "SAMPLEID"
          } ]
        },
        "value": "4051960071"
      } ],
      "status": "available",
      "type": {
        "coding": [ {
          "system": "urn:centraxx",
          "code": "CIT"
        } ]
      },
      "subject": {
        "identifier": {
          "type": {
            "coding": [ {
              "system": "urn:centraxx",
              "code": "LIMSPSN"
            } ]
          },
          "value": "lims_989077906"
        }
      },
      "parent": [ {
        "reference": "Specimen/12254"
      } ],
      "collection": {
        "quantity": {
          "value": 350.0000,
          "unit": "MICL",
          "system": "urn:centraxx"
        }
      },
      "container": [ {
        "identifier": [ {
          "system": "urn:centraxx",
          "value": "NUM_AliContainer"
        } ],
        "capacity": {
          "value": 350.00,
          "unit": "MICL",
          "system": "urn:centraxx"
        },
        "specimenQuantity": {
          "value": 350.0000,
          "unit": "MICL",
          "system": "urn:centraxx"
        }
      } ]
    },
    "request": {
      "method": "POST",
      "url": "Specimen/12255"
    }
  }
```