# buildhelp offers helper functions for csvtofhir and csvtofhirobs

# maybe instead put functions from csvtofhir and csvtofhirobs in one file, then buildhelp could also go there

import pandas as pd

# panda_timestamp converts a date string to panda
def panda_timestamp(date_string):

    # eventuell fehler checken in dieser funktion

    if date_string is None or date_string == "" or date_string == "NULL":
        return None

    # Überprüfen, ob es sich um einen leeren Wert handelt
    if pd.isna(date_string):
        return None
    
    # Wenn es sich bereits um ein Pandas-Timestamp-Objekt handelt, können wir es direkt formatieren
    if isinstance(date_string, pd.Timestamp):
        dt = date_string
    else:
        # Andernfalls konvertieren wir die Zeichenfolge in ein Pandas-Timestamp-Objekt
        dt = pd.to_datetime(date_string, infer_datetime_format=True, dayfirst=True)

    return dt.tz_localize('Europe/Berlin')