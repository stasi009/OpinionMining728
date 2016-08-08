
from __future__ import absolute_import
import json
import common

class Review(object):
    def __init__(self,d):
        self.id = d["ReviewID"]
        self.title = d["Title"].encode("ascii","ignore")
        self.author = d["Author"]
        self.content = d["Content"].encode("ascii","ignore")
        self.date = d["Date"]

        self.ratings = {}
        ratings = d["Ratings"]

        self.ratings[common.AspectBusiness]= common.safe_get_rating(ratings,"Business service (e.g., internet access)")
        self.ratings[common.AspectCheckin] = common.safe_get_rating(ratings,"Check in / front desk")
        self.ratings[common.AspectClean] = common.safe_get_rating(ratings,"Cleanliness")
        self.ratings[common.AspectLocation] = common.safe_get_rating(ratings,"Location")
        self.ratings[common.AspectOverall] = common.safe_get_rating(ratings,"Overall")
        self.ratings[common.AspectRoom] = common.safe_get_rating(ratings,"Rooms")
        self.ratings[common.AspectService] = common.safe_get_rating(ratings,"Service")
        self.ratings[common.AspectValue] = common.safe_get_rating(ratings,"Value")

class Hotel(object):
    def __init__(self,filename):
        with open(filename,"rt") as inputf:
            d = json.load(inputf)

        info = d["HotelInfo"]
        self.name = info["Name"]
        self.id = info["HotelID"]
        self.price = info["Price"]

        self.reviews = [ Review(review_d) for review_d in d["Reviews"]]

if __name__ == "__main__":
    path = "data/2514303.json"
    h = Hotel(path)
    print "Hotel-{}:{}".format(h.id,h.name)

    for index, review in  enumerate( h.reviews):
        print "************** REVIEW [{}] **************".format(index+1)
        for k,v in review.ratings.viewitems():
            print "{}: {}".format(k,v)

        print "Title: {}".format(review.title)
        print review.content
