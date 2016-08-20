
import nltk
from pymongo import MongoClient
from sentence import Sentence

class Review(object):

    SentTokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    def __init__(self):
        # HotelId for TripAdvisor, or RoomId for Airbnb
        self.id = None
        self.business_id = None
        self.ratings = None

    def assign_comment(self,text,stop_words):
        self.sentences = []
        for raw_sentence in Review.SentTokenizer.tokenize(text):
            sent = Sentence.from_raw(raw_sentence,stop_words)
            if len(sent.words) >0:
                self.sentences.append(sent)

    def to_dict(self):
        d = {"business_id":self.business_id,\
        "ratings":self.ratings,\
        "sentences":[sent.to_dict() for sent in self.sentences]}

        if self.id is not None:
            d["_id"] = self.id

        return d

    @staticmethod
    def from_dict(d):
        r = Review()
        r.id = d.get("_id",None)
        r.business_id = d.get("business_id",None)# sometimes, we just don't care business_id
        r.ratings = d.get("ratings",None)
        r.sentences = [Sentence.from_dict(sent_dict) for sent_dict in d["sentences"]]
        return r

class ReviewsDal(object):

    def __init__(self,dbname,colname="reviews"):
        self._client = MongoClient()
        db = self._client[dbname]
        self._reviews = db[colname]

    def close(self):
        self._client.close()

    def insert_many(self,reviews):
        # cannot be iterator, but an non-empty list
        if len(reviews)>0:
            self._reviews.insert_many([r.to_dict() for r in reviews])

    def list_ids(self):
        cursor = self._reviews.find({},{"_id":1})
        return [d["_id"] for d in cursor]

    def find_by_review_id(self,reviewid,include_words = False):
        cursor = None
        if not include_words:
            # exclude from sending back 'words', save time and bandwidth
            cursor = self._reviews.find({"_id":reviewid},{"sentences.words":0})
        else:
            cursor = self._reviews.find({"_id":reviewid})

        reviews = list(cursor)
        if len(reviews) == 0:
            return None # no match
        elif len(reviews) == 1:
            return Review.from_dict(reviews[0])
        else:
            raise Exception("reviewid is unique, can only return 0 or 1")

    def update_aspects_sentiments(self,reviewid,new_aspects_sentiments):
        update_content = {}
        for sent_index,(new_aspect,new_sentiment) in new_aspects_sentiments.iteritems():
            update_content["sentences.{}.aspect".format(sent_index)] = new_aspect
            update_content["sentences.{}.sentiment".format(sent_index)] = new_sentiment

        result = self._reviews.update_one({"_id":reviewid},{"$set":update_content})
        return result.modified_count == 1

    def sentences_stream_by_aspect(self,aspect):
        cursor = self._reviews.find({"sentences.aspect":aspect},{"ratings":1,"sentences":1})
        for d in cursor:
            review = Review.from_dict(d)
            actual_rating = review.ratings.get(aspect,None)

            for sentence in review.sentences:
                if sentence.aspect == aspect:
                    if actual_rating is not None and float(actual_rating)>0:
                        sentence.sentiment = actual_rating# use 'actual_rating', a number, replace 'Positive/Negative'
                    yield sentence
