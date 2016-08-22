from __future__ import print_function

import os,sys
parentpath = os.path.abspath("..")
if parentpath not in sys.path:
    sys.path.append(parentpath)

import cPickle
from pymongo import MongoClient
from bson.objectid import ObjectId

from review import Review,ReviewsDal

dbname = "tripadvisor_train"
reviewid = "57b3c3e460c0ff08b162bd9d"

dal = ReviewsDal(dbname)
reviewid = "57b3bf2360c0ff08b161ff1e"
review = dal.find_by_review_id(ObjectId(reviewid),True)


def print_review(review):
    print("************ REVIEW <{}> ************".format(review.id))
    print("business_id: {}".format(review.business_id))
    print("ratings: {}".format(review.ratings))

    for index,sentence in enumerate( review.sentences):
        print ("\t[{}]: {}".format(index + 1, sentence.raw))
        if sentence.words is not None:
            print ("\t{}".format(sentence.words))
        print ("\t ##### aspect: {}".format(sentence.aspect))
        print ("\t ##### sentiment: {}".format(sentence.sentiment))


def load_classifier(pklname):
    with open(pklname,"rb") as inf:
        return cPickle.load(inf)

classifier = load_classifier("aspect_nltk_nb.pkl")

def temp_print_review(reviewid):
    review = dal.find_by_review_id(ObjectId(reviewid), True)
    for index,sentence in enumerate(review.sentences):
        print ("********* {}-th sentence: ".format(index + 1))
        print (sentence.raw)

        features = {}.fromkeys(sentence.words_no_negsuffix(), True)
        probabilites = classifier.prob_classify(features)

        probabilites = [(label,probabilites.prob(label)) for label in classifier.labels()]
        probabilites.sort(key = lambda  t: -t[1])# sort in descending order
        for label, prob in probabilites:
            print ("\t[{}]:{:.2f}".format(label, prob))





