
import random
# random.seed(1234)

import os.path
import glob
import json
from tqdm import tqdm
from entities import TaHotel
import common

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

def compare_reviews_on_aspect(aspect,num_reviews):
    reviews_with_aspect = []
    reviews_without_aspect = []

    allfiles = glob.glob( "data/*.json" )
    while len(reviews_with_aspect) < num_reviews or len(reviews_without_aspect) < num_reviews:
        datafile = random.choice(allfiles)
        hotel = TaHotel(datafile)
        print "processing hotel file <{}>".format(datafile)

        for review in hotel.reviews:
            print "\n"
            print review.ratings
            print review.entire_content()

            if len(reviews_with_aspect) < num_reviews and aspect in review.ratings:
                reviews_with_aspect.append(review.entire_content())
                print "+++ {}-th review with <{}> added".format(len(reviews_with_aspect),aspect)

            if len(reviews_without_aspect) < num_reviews and aspect not in review.ratings:
                reviews_without_aspect.append(review.entire_content())
                print "--- {}-th review without <{}> added".format(len(reviews_without_aspect),aspect)

    ### save into file
    with open("reviews_with_{}.txt".format(aspect),"wt") as outf:
        for review in reviews_with_aspect:
            outf.write(review+"\n\n")

    with open("reviews_without_{}.txt".format(aspect),"wt") as outf:
        for review in reviews_without_aspect:
            outf.write(review+"\n\n")

if __name__ == "__main__":
    # generate_summary("data")
    compare_reviews_on_aspect(common.AspectLocation,10)
