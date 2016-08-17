
import nltk
from nltk.corpus import stopwords
from bson.objectid import ObjectId
from tripadvisor.entities import TaHotel
from review import Review,ReviewsDal

StopWords = frozenset(stopwords.words("english"))
DbName = "tripadvisor"

def get_reviews(hotel_file):
    hotel = TaHotel(hotel_file)

    for index,tareview in enumerate( hotel.reviews):
        review = Review()
        review.business_id = hotel.id
        review.ratings = tareview.ratings
        review.assign_content(tareview.entire_content(),StopWords)
        yield review

def test_review_to_dict():
    datafile = "tripadvisor/data/2514286.json"
    for index,review in enumerate(get_reviews(datafile)):
        print "********** {}-th review: ".format(index+1)
        print review.to_dict()

def test_insert_db():
    datafile = "tripadvisor/data/536101.json"
    dal = ReviewsDal(DbName)
    dal.insert_many(get_reviews(datafile))
    print "INSERTED INTO DATABASE"

def test_list_all_ids():
    dal = ReviewsDal(DbName)
    print dal.list_ids()

def print_review_by_review_id(reviewid):
    dal = ReviewsDal(DbName)
    review = dal.find_by_review_id(reviewid)
    print "************ REVIEW <{}> ************".format(review.id)
    print "business_id: {}".format(review.business_id)
    print "ratings: {}".format(review.ratings)

    for index,sentence in enumerate( review.sentences):
        print "\t[{}]: {}".format(index+1,sentence.raw)
        print "\t ##### aspect: {}".format(sentence.aspect)
        print "\t ##### sentiment: {}".format(sentence.sentiment)

def test_update_aspect_sentiment():
    reviewid = ObjectId("57b0030160c0ff0f9b37a8fc")
    print "=========================== before update"
    print_review_by_review_id(reviewid)

    # update
    dal = ReviewsDal(DbName)
    new_aspects_sentiments = {
        3:("Value","Positive"),
        8:("Service","Negative")
    }
    success = dal.update_aspects_sentiments(reviewid,new_aspects_sentiments)
    print "update successful? {}".format(success)

    print "=========================== after update"
    print_review_by_review_id(reviewid)

def test_list_sentences_by_aspect():
    aspect = "Service"
    dal = ReviewsDal(DbName)
    for index,sentence in enumerate(dal.sentences_stream_by_aspect(aspect)):
        print "\n********** [{}] {}: {}".format(index+1,sentence.aspect,sentence.sentiment)
        print sentence.raw

if __name__ == "__main__":
    # test_review_to_dict()
    # test_insert_db()
    # test_list_all_ids()
    # print_review_by_review_id(ObjectId("57b0030160c0ff0f9b37a8fc"))
    # test_update_aspect_sentiment()
    test_list_sentences_by_aspect()
