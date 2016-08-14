
from __future__ import absolute_import
import json
import re
import common

def normalize_ratings(dest_ratings,dest_label,src_ratings,src_label):
    if src_label in src_ratings:
        dest_ratings[dest_label] = float(src_ratings[src_label])

class Review(object):

    CleanPattern = re.compile(r"showReview\((\d)+, 'full'\);",re.IGNORECASE)

    def __init__(self,d):
        self.id = d["ReviewID"]
        self.title =  d["Title"].encode("ascii","ignore") if "Title" in d else ""
        self.author = d["Author"]
        self.date = d["Date"]

        content = d["Content"].encode("ascii","ignore")
        self.content = Review.CleanPattern.sub('',content)

        self.ratings = {}
        raw_ratings = d["Ratings"]

        normalize_ratings(self.ratings,common.AspectBusiness,raw_ratings,"Business service (e.g., internet access)")
        normalize_ratings(self.ratings,common.AspectCheckin ,raw_ratings,"Check in / front desk")
        normalize_ratings(self.ratings,common.AspectClean ,raw_ratings,common.AspectClean)
        normalize_ratings(self.ratings,common.AspectLocation ,raw_ratings,common.AspectLocation)
        normalize_ratings(self.ratings,common.AspectOverall ,raw_ratings,common.AspectOverall)
        normalize_ratings(self.ratings,common.AspectRoom ,raw_ratings,common.AspectRoom)
        normalize_ratings(self.ratings,common.AspectService ,raw_ratings,common.AspectService)
        normalize_ratings(self.ratings,common.AspectValue ,raw_ratings,common.AspectValue)
        normalize_ratings(self.ratings,common.AspectSleep ,raw_ratings,common.AspectSleep)

class Hotel(object):
    def __init__(self,filename):
        with open(filename,"rt") as inputf:
            d = json.load(inputf)

        info = d["HotelInfo"]
        self.id = info["HotelID"]
        self.name = info.get("Name","Hotel#{}".format(self.id))
        self.price = info["Price"]

        self.reviews = [ Review(review_d) for review_d in d["Reviews"]]

if __name__ == "__main__":
    path = "data/262451.json"
    h = Hotel(path)
    print "Hotel-{}:{}".format(h.id,h.name)

    for index, review in  enumerate( h.reviews):
        print "************** REVIEW [{}] **************".format(index+1)
        for k,v in review.ratings.viewitems():
            print "{}: {}".format(k,v)

        print "Title: {}".format(review.title)
        print review.content
