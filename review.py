
import nltk
from pymongo import MongoClient
from sentence import Sentence

class Review(object):

    SentTokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    def __init__(self):
        # HotelId for TripAdvisor, or RoomId for Airbnb
        self.business_id = None
        self.ratings = None

    def assign_content(self,text,stop_words):
        self.sentences = [ Sentence.from_raw(raw_sentence,stop_words) for raw_sentence in Review.SentTokenizer.tokenize(text) ]

    def to_dict(self):
        return {"business_id":self.business_id,\
        "ratings":self.ratings,\
        "sentences":[sent.to_dict() for sent in self.sentences]}

    @staticmethod
    def from_dict(self,d):
        self.business_id = d["business_id"]
        self.ratings = d.get("ratings",None)
        sent_dicts = d["sentences"]
        self.sentences = [Sentence.from_dict(sent_dict) for sent_dict in sent_dicts]

class ReviewsDal(object):

    def __init__(self,dbname,colname="reviews"):
        self._client = MongoClient()
        db = self._client[dbname]
        self._reviews = db[colname]

    def insert(self,reviews):
        # cannot be iterator, but a concrete list
        self._reviews.insert_many([r.to_dict() for r in reviews])
