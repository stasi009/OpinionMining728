
import os,sys
parentpath = os.path.abspath("..")
if parentpath not in sys.path:
    sys.path.append(parentpath)

import cPickle
from reviews_proxy import ReviewsMongoProxy
from classifier import Classifier

def print_review(review):
    print "************ REVIEW <{}> ************".format(review.id)
    print "business_id: {}".format(review.business_id)
    print "ratings: {}".format(review.ratings)

    for index,sentence in enumerate( review.sentences):
        print "\t[{}]: {}".format(index+1,sentence.raw)
        print "\t ##### aspect: {}".format(sentence.aspect)
        print "\t ##### sentiment: {}".format(sentence.sentiment)

def test_get_next_random_review():
    proxy = ReviewsMongoProxy("tripadvisor")

    num_reviews = 3
    for index in xrange(num_reviews):
        print "\n\n"
        review = proxy.next_random_review()
        print_review(review)

def test_classify():

    proxy = ReviewsMongoProxy("tripadvisor_train")
    review = proxy.find_review_by_id(proxy.next_random_review_id())

    classifier = Classifier("../tripadvisor/aspect_nltk_nb.pkl")
    classifier.classify(review)

    print_review(review)

if __name__ == "__main__":
    # test_get_next_random_review()
    test_classify()
