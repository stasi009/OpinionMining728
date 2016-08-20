
from collections import defaultdict
from bson.objectid import ObjectId
from review import Review,ReviewsDal
import random

class ReviewsMongoProxy(object):

    def __init__(self,dbname):
        self.dbname = dbname
        self.dal = ReviewsDal(dbname)
        # we only store the string format, which is more convenient in web app
        self.all_ids = [str(id) for id in self.dal.list_ids()]

    def next_random_review_id(self):
        return random.choice(self.all_ids)

    def find_review_by_id(self,idstring):
        id = ObjectId(idstring)
        return self.dal.find_by_review_id(id,True)

    def update_review(self,review_id,contents):
        """
        new_conents is a dictionary which contains key-value pair like:
            sentiment_5:Negative
            aspect_4:Service
        """
        review_id = ObjectId(review_id)

        updated_aspect_sentiment = defaultdict(lambda: [None,None])
        for k,v in contents.iteritems():
            segments = k.split("_")
            if len(segments) != 2:
                continue# to make code easier, we just the whole request.form, it may contain some invalid arguments

            position = None
            if segments[0] == "aspect":
                position = 0
            elif segments[0] == "sentiment":
                position = 1
            else:
                # to make code easier, we just the whole request.form, it may contain some invalid arguments
                continue

            index = int(segments[1])
            updated_aspect_sentiment[index][position] = v

        return self.dal.update_aspects_sentiments(review_id,updated_aspect_sentiment)
