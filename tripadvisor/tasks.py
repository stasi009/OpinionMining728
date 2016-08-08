

import os.path
import glob
from tqdm import tqdm
from entities import Hotel

def generate_summary(datafolder):
    json_files = glob.glob( os.path.join(  datafolder,"*.json") )
    dest_filename = os.path.join(datafolder,"summary.csv")

    with open(dest_filename,"wt") as outf:
        for jsfile in tqdm(json_files):
            try:
                hotel = Hotel(jsfile)
            except Exception:
                print "!!! Failed to process file <{}>".format(jsfile)
                raise

            outf.write("{},{},{},{}\n".format(hotel.id,hotel.name,hotel.price, len(hotel.reviews)))

if __name__ == "__main__":
    generate_summary("data")
