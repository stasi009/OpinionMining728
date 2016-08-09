

import os.path
import glob
import json
from tqdm import tqdm
from entities import Hotel

def generate_summary(datafolder):
    """
    webapp need some summary information, which has no need to iterate all hotels each time I need them
    so a better solution is iterate just once, retrieve those summaries, and save them into file for future usage

    since the content has a lot of commas, so I cannot use CSV format
    but since it has a lot of files to process, I cannot save them into one big container and dump once
    so I have to write my dump-to-json codes, generate json and dump to file side by side
    """
    json_files = glob.glob( os.path.join(  datafolder,"*.json") )
    total_files = len(json_files)
    dest_filename = "summary.json"

    with open(dest_filename,"wt") as outf:
        outf.write("[\n")

        for index,jsfile in enumerate( tqdm(json_files) ):
            try:
                hotel = Hotel(jsfile)
            except Exception:
                print "!!! Failed to process file <{}>".format(jsfile)
                raise

            txt = json.dumps({"Id":hotel.id,"Name":hotel.name,"Price":hotel.price,"NumReviews":len(hotel.reviews)})
            separator = "\n" if index+1 == total_files else ",\n"
            outf.write(txt+ separator )

        outf.write("]\n")

if __name__ == "__main__":
    generate_summary("data")
