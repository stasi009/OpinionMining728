
import nltk
from nltk.corpus import stopwords
from tripadvisor.entities import TaHotel
from review import Review,ReviewsDal

StopWords = frozenset(stopwords.words("english"))
DbName = "tripadvisor"

def get_reviews(hotel_file):
    hotel = TaHotel(hotel_file)

    reviews = []
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

if __name__ == "__main__":
    # test_review_to_dict()
    # test_insert_db()
    test_list_all_ids()
