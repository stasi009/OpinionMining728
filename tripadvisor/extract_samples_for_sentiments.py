
import os,sys
parentpath = os.path.abspath("..")
if parentpath not in sys.path:
    sys.path.append(parentpath)

import random
import cPickle
from pymongo import MongoClient
from sklearn.feature_extraction.text import CountVectorizer
import nltk

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

    # cursor = sentisent_collection.find({'sentiment':{'$lte':2}}).skip(99).limit(120)
    cursor = sentisent_collection.aggregate([ {'$match':{'sentiment':3}},
                                              { '$sample': { 'size': 120 } } ])
    for index,sentd in enumerate(cursor):
        sent = Sentence.from_dict(sentd)
        print "\n\n[{}] Aspect: {}, Sentiment: {}".format(index+1,sent.aspect,sent.sentiment)
        print sent.raw
        print "--------------"
        print sent.words

    client.close()

def sample_split(dbname,num_train,num_validate,num_test):
    client = MongoClient()
    db = client[dbname]
    sentisent_collection = db.sentiment_sentences

    ################## load and count
    aspect_dist = nltk.FreqDist()
    sentiment_dist = nltk.FreqDist()

    all_samples = []
    cursor = sentisent_collection.aggregate([ { '$sample': { 'size': num_train + num_validate + num_test } } ])
    for index,d in enumerate(cursor):
        sent = Sentence.from_dict(d)
        all_samples.append( (sent.words,sent.sentiment) )

        aspect_dist[sent.aspect] +=1
        sentiment_dist[int(sent.sentiment)] +=1
    client.close()

    ################## show statistics
    for k in aspect_dist:
        print '[{}]: {}'.format(k,aspect_dist.freq(k))

    for k in sentiment_dist:
        print '[{}]: {}'.format(k,sentiment_dist.freq(k))

    ################## shuffle
    random.shuffle(all_samples)

    ################## split
    def __dump(filename,data):
        with open(filename,"wb") as outf:
            cPickle.dump(data,outf)

    __dump("sentidata_train_raw.pkl",all_samples[:num_train])
    __dump("sentidata_validate_raw.pkl",all_samples[num_train:num_train+num_validate])
    __dump("sentidata_test_raw.pkl",all_samples[num_train+num_validate:])

def test_count_vectorizer():
    inputs = ['hello hello world', "i don't care", 'what should I do next what','I regret']
    inputs = [s.split() for s in inputs]

    vectorizer = CountVectorizer(analyzer=lambda x: x)
    matrix = vectorizer.fit_transform(inputs)
    vectorizer.vocabulary_


if __name__ == "__main__":
    # classifier = load_classifier("aspect_nltk_nb.pkl")
    # load_reviews_save_sentiment_sentences("tripadvisor_train",classifier)
    # load_sentences()
    sample_split("tripadvisor_train",15000,6000,6000)





