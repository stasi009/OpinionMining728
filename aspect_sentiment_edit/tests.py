
import os,sys
sys.path.append(os.path.abspath(".."))

from reviews_proxy import ReviewsMongoProxy

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

if __name__ == "__main__":
    test_get_next_random_review()
