
import json

def pprint_json(infilename,outfilename):
    with open(infilename,"rt") as inf:
        d = json.load(inf)

    with open(outfilename,"wt") as outf:
        json.dump(d,outf,indent=4)
