
import os,sys
parentpath = os.path.abspath("..")
if parentpath not in sys.path:
    sys.path.append(parentpath)

import os.path
import random
import glob
import shutil
import threading
from Queue import Queue

import nltk
from nltk.corpus import stopwords
from pymongo import MongoClient
from bson.objectid import ObjectId

from entities import TaHotel
from negation_suffix import NegationSuffixAdder
from sentence import Sentence
from review import Review,ReviewsDal
import common

def sample_move(numfiles,destfolder):
    allfiles = glob.glob("*.json")
    files = random.sample(allfiles,numfiles)
    for fname in files:
        shutil.move(fname,destfolder)

class ParseJsonAgent(object):
    def __init__(self,datafolder,queue):
        self.allfiles = glob.glob(os.path.join(datafolder,"*.json"))
        self.queue = queue
        self.stopwords = common.make_stop_words()

    def run(self):
        for index,fname in enumerate(self.allfiles):
            hotel = TaHotel(fname)

            reviews = []
            for tareview in hotel.reviews:
                review = Review()
                review.business_id = hotel.id
                review.ratings = tareview.ratings
                review.assign_comment(tareview.entire_content(),self.stopwords)
                reviews.append(review)

            if len(reviews)>0:
                self.queue.put(reviews)
                print "[PARSER]: {}-th file<{}> parsed, {} reviews enqueued".format(index+1,fname,len(reviews))

class SaveMongoAgent(threading.Thread):
    def __init__(self,dbname,queue):
        threading.Thread.__init__(self)
        self.daemon = True # daemon thread, won't prevent main thread from exiting
        self.dal = ReviewsDal(dbname)
        self.queue = queue
        self.counter = 0

    def run(self):
        while True:
            reviews = self.queue.get()
            self.dal.insert_many(reviews)

            self.counter += 1
            print "[SAVER]: {}-th batch, {} reviews inserted".format(self.counter,len(reviews))
            self.queue.task_done()

def insert_into_db(datafolder,dbname):
    queue = Queue()

    parse_agent = ParseJsonAgent(datafolder,queue)
    save_agent = SaveMongoAgent(dbname,queue)

    save_agent.start()
    parse_agent.run()

    queue.join()
    print "!!! ALL DONE !!!"

def update_add_neg_suffix(dbname,query_condition):
    stop_words = common.make_stop_words()
    client = MongoClient()
    review_collection = client[dbname]['reviews']

    cursor = review_collection.find(query_condition,{"sentences.raw":1,"sentences.words":1})
    for rindex,rd in enumerate(cursor):
        review = Review.from_dict(rd)

        update_content = {}
        for sindex,sent in enumerate(review.sentences):
            new_sent = Sentence.from_raw(sent.raw,stop_words)
            if set(new_sent.words) != set(sent.words):
                update_content["sentences.{}.words".format(sindex)] = new_sent.words

        if len(update_content)>0:
            result = review_collection.update_one({"_id":review.id},{"$set":update_content})
            if result.modified_count != 1:
                raise Exception("failed to update review<{}>".format(review.id))

        print "{}-th review updated {} sentences".format(rindex+1,len(update_content))

    client.close()

def get_all_known_aspect_sentences(dbname):
    client = MongoClient()
    review_collection = client[dbname]["reviews"]

    query_condition = {"sentences": {'$elemMatch': {'aspect': {'$ne':'Unknown'}}   }   }
    cursor = review_collection.find(query_condition,{"sentences":1})
    for d in cursor:
        review = Review.from_dict(d)
        for sentence in review.sentences:
            if sentence.aspect != "Unknown":
                yield sentence

    client.close()

def export_from_db(dbname,filename):
    sentence_stream = get_all_known_aspect_sentences(dbname)
    with open(filename,"wt") as outf:
        for sent in sentence_stream:
            outf.write("{},{}\n".format(sent.aspect, " ".join(sent.words_no_negsuffix()  )  )  )

if __name__ == "__main__":
    # insert_into_db("data/test1","tripadvisor_test")
    # export_from_db("tripadvisor_train","aspects_train.csv")
    # update_add_neg_suffix("tripadvisor_train",{'_id':ObjectId("57b3c96560c0ff08b163a0b3")})
    update_add_neg_suffix("tripadvisor_test",{})
