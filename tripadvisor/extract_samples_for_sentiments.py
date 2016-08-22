
import os,sys
parentpath = os.path.abspath("..")
if parentpath not in sys.path:
    sys.path.append(parentpath)

import cPickle
from pymongo import MongoClient
from bson.objectid import ObjectId
import common
from sentence import  Sentence
from review import Review,ReviewsDal
from aspect_nltk_nb import ImprovedNbClassifier

def review_to_sentences(review,classifier):
    composed_sentences = {aspect: (rating,[],[]) for aspect,rating in review.ratings.iteritems() if rating>0}

    for sentence in review.sentences:
        aspect = None
        if sentence.aspect != common.AspectUnknown:
            aspect = sentence.aspect # has been manually tagged
        else:
            features = {}.fromkeys(sentence.words_no_negsuffix(), True)
            aspect = classifier.classify(features)

        if aspect != common.AspectUnknown and aspect in composed_sentences:
            comp_sentence = composed_sentences[aspect]
            comp_sentence[1].append(sentence.raw)
            comp_sentence[2].extend(sentence.words)

    for aspect, comp_sentence in composed_sentences.iteritems():
        if len(comp_sentence[2]) >0:
            composed_raw_sent = " ".join(comp_sentence[1])
            yield Sentence(raw = composed_raw_sent,words = comp_sentence[2],aspect=aspect,sentiment=comp_sentence[0])


def load_classifier(pklname):
    with open(pklname,"rb") as inf:
        return cPickle.load(inf)

def load_reviews_save_sentiment_sentences(dbname,classifier):
    client = MongoClient()
    db = client[dbname]
    reviews_collection = db["reviews"]
    sentisent_collection = db["sentiment_sentences"]

    review_cursor = reviews_collection.find({})
    for index,rd in enumerate(review_cursor):
        review = Review.from_dict(rd)

        sentence_dicts  = [ s.to_dict() for s in review_to_sentences(review,classifier) ]
        if len(sentence_dicts)>0:
            sentisent_collection.insert_many(sentence_dicts)

        print "{}-th review extract {} sentences and saved".format(index+1,len(sentence_dicts))

    client.close()

def load_sentences():
    dbname = "tripadvisor_train"
    client = MongoClient()
    db = client[dbname]
    sentisent_collection = db["sentiment_sentences"]

    cursor = sentisent_collection.find({'sentiment':{'$lte':2}}).skip(99).limit(120)
    for index,sentd in enumerate(cursor):
        sent = Sentence.from_dict(sentd)
        print "\n[{}] Aspect: {}, Sentiment: {}".format(index+1,sent.aspect,sent.sentiment)
        print sent.raw
        print sent.words

    client.close()

if __name__ == "__main__":
    # classifier = load_classifier("aspect_nltk_nb.pkl")
    # load_reviews_save_sentiment_sentences("tripadvisor_train",classifier)
    load_sentences()





