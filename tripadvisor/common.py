

import json

AspectBusiness = "Business Service"
AspectCheckin = "Check in"
AspectClean = "Cleanliness"
AspectLocation = "Location"
AspectOverall = "Overall"
AspectRoom = "Rooms"
AspectService = "Service"
AspectValue = "Value"

def pprint_json(infilename,outfilename):
    with open(infilename,"rt") as inf:
        d = json.load(inf)

    with open(outfilename,"wt") as outf:
        json.dump(d,outf,indent=4)

def safe_get_rating(ratings_d,key):
    return float(ratings_d[key]) if key in ratings_d else None
