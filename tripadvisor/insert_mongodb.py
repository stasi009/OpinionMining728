
import os,sys
sys.path.append(os.path.abspath(".."))

import os.path
import random
import glob
import shutil
import threading
from Queue import Queue

import nltk
from nltk.corpus import stopwords
from entities import TaHotel
from review import Review,ReviewsDal

def sample_move(numfiles,destfolder):
    allfiles = glob.glob("*.json")
    files = random.sample(allfiles,numfiles)
    for fname in files:
        shutil.move(fname,destfolder)

class ParseJsonAgent(object):
    def __init__(self,datafolder,queue):
        self.allfiles = glob.glob(os.path.join(datafolder,"*.json"))
        self.queue = queue

        stop_words = stopwords.words("english")
        stop_words.append("hotel")
        self.stopwords = frozenset(stop_words)

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

if __name__ == "__main__":
    datafolder = "data/train1"
    dbname = "tripadvisor_train"
    queue = Queue()

    parse_agent = ParseJsonAgent(datafolder,queue)
    save_agent = SaveMongoAgent(dbname,queue)

    save_agent.start()
    parse_agent.run()

    queue.join()
    print "!!! ALL DONE !!!"
