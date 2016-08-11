
import random
random.seed(689)

import glob

import os,sys
sys.path.append(os.path.abspath(".."))

from entities import Hotel
from aspect_segmentation import AspectSegmentation

def select_inputs(n_hotels):
    json_files = glob.glob( "data/*.json" )
    selected_hotels = random.sample(json_files,n_hotels)

    print "Randomly select {} files from total {} files".format(len(selected_hotels),len(json_files))
    for index,hfile in enumerate( selected_hotels):
        print "[{}] {}".format(index+1,hfile)

    for hfile in selected_hotels:
        hotel = Hotel(hfile)
        for review in hotel.reviews:
            yield review.title + ". " + review.content

def save_result(segmenter):
    pass

if __name__ == "__main__":
    n_hotels = 10
    iter_reviews = select_inputs(n_hotels)

    seed_aspect_keywords = {
        "Value": set(["value", "price", "quality", "worth"]),
        "Room": set(["room", "suite", "view", "bed","spacious","noisy"]),
        "Location": set(["location", "traffic", "minute", "restaurant","shop","locate"]),
        "Cleanliness": set(["clean", "dirty", "maintain", "smell"]),
        "Service": set(["staff","check", "help","service","helpful","friendly"]),
        "Business service": set(["business", "center", "computer", "internet","wifi"])
    }

    extra_stop_words = ["hotel","great"]
    segmenter = AspectSegmentation(iter_reviews,seed_aspect_keywords,extra_stop_words)
    segmenter.run()
