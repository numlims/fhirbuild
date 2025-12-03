from datetime import datetime, timezone, timedelta
import uuid
import re

def intornone(s:str):
    """intornone parses a string to int, and letters A,B,C,... to numbers 1,2,3... if it receives None it returns None."""
    #  print(f"intornone: {s}")
    if s == None:
        return None
    if re.match(r"^[A-Za-z]$", s):
        #print("match letter")
        # convert to lower, so that you can subtract 96 from lower case 'a' and land at 1
        s = s.lower()
        # get the ascii number for the letter with ord() and subtract 96
        num = ord(s) - 96
        return num
    #print(f"not match letter: '{s}'")
    return int(s)


def datestring(d: datetime) -> str:
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

def genfhirid(fromstr:str):
    """genfhirid generates a fhirid from given string (e.g. sampleid)."""
    # Generate a deterministic ID based on the input string
   
    namespace = uuid.NAMESPACE_DNS  # Use DNS namespace for UUID generation
    if fromstr is None or fromstr == "":
        raise ValueError("fromstr must not be None or empty")

    return str(uuid.uuid5(namespace, fromstr))  # Use uuid5 for deterministic ID generation
    

def fromisoornone(s:str):
    """fromisoornone returns a date from iso or none"""

    if s is None:
        return None
    return datetime.fromisoformat(s)


def open_csv_file(filename, delimiter=";", encoding="utf-8"):
    """
    open_csv_file opens a CSV file and returns a DictReader object.
    """
    try:
        file = open(filename, "r", encoding=encoding)
        return csv.DictReader(file, delimiter=delimiter)
    except FileNotFoundError:
        print(f"File {filename} not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error opening file {filename}: {e}")
        sys.exit(1)

