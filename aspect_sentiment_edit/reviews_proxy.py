
from bson.objectid import ObjectId
from review import Review,ReviewsDal
import random

class ReviewsMongoProxy(object):

    def __init__(self,dbname):
        self.dal = ReviewsDal(dbname)
        # we only store the string format, which is more convenient in web app
        self.all_ids = [str(id) for id in self.dal.list_ids()]

    def next_random_review(self):
        next_review_id = ObjectId( random.choice(self.all_ids) )
        # no reason "find_by_review_id" return None
        return self.dal.find_by_review_id(next_review_id)
