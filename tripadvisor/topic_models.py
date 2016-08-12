
import random
random.seed(689)

import os,sys
sys.path.append(os.path.abspath(".."))

from nltk.corpus import stopwords
import logging
import glob
from gensim import corpora,models
from entities import Hotel
import sentence

N_HOTELS = 300
DictionaryFile = "ta.dict"
BowFile = "ta_bow.mm"
TfidfFile = "ta_tfidf.mm"
LsiModelFile = "ta_model.lsi"
LsiTopicsFile = "ta_lsi_topics.txt"
LdaModelFile = "ta_model.lda"
LdaTopicsFile = "ta_lda_topics.txt"

def review_stream(n_hotels):
    json_files = glob.glob( "data/*.json" )
    selected_hotels = random.sample(json_files,n_hotels)

    for hfile in selected_hotels:
        hotel = Hotel(hfile)
        for review in hotel.reviews:
            review_text = review.title + ". " + review.content if len(review.title) >0 else review.content
            yield review_text

def words_stream(review_stream):
    stop_words = set(stopwords.words("english"))
    for index,review in enumerate(review_stream):
        # treat the whole review as one long sentence
        sent = sentence.Sentence(review,stop_words)
        yield sent.words
        print "{}-th review processed".format(index+1)

def build_dictionary(review_stream):
    """
    what's the scale of each text? a review or a sentence? we should experiement on this problem.
    """
    w_stream = words_stream(review_stream)
    dictionary = corpora.Dictionary(w_stream)
    dictionary.save(DictionaryFile)  # store the dictionary, for future reference
    print(dictionary)

class Corpus(object):
    def __init__(self):
        self._dictionary = corpora.Dictionary.load(DictionaryFile)

    def __iter__(self):
        stream_review = review_stream(N_HOTELS)
        stream_words = words_stream(stream_review)
        for words in stream_words:
            yield self._dictionary.doc2bow(words)

def save_bow():
    corpus = Corpus()
    corpora.MmCorpus.serialize(BowFile,corpus)

def save_tfidf():
    corpus_bow = corpora.MmCorpus(BowFile)
    tfidf_model = models.TfidfModel(corpus_bow)

    corpus_tfidf = tfidf_model[corpus_bow]
    corpora.MmCorpus.serialize(TfidfFile,corpus_tfidf)

def lsi_model_topics():
    dictionary = corpora.Dictionary.load(DictionaryFile)
    corpus_tfidf = corpora.MmCorpus(TfidfFile)

    N_TOPICS = 300
    lsi_model = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=N_TOPICS)
    print "================= LSI MODEL IS BUILT ================="
    lsi_model.save(LsiModelFile)

    topics = lsi_model.show_topics(num_topics=-1, num_words=20, log=True, formatted=True)
    with open(LsiTopicsFile,"wt") as outf:
        for topic in topics:
            # topic[0]: topic number
            # topic[1]: topic description
            outf.write("\n####################### TOPIC {} #######################\n".format(topic[0]))
            outf.write(topic[1]+"\n")

def lda_model_topics():
    dictionary = corpora.Dictionary.load(DictionaryFile)
    corpus_bow = corpora.MmCorpus(BowFile)

    N_TOPICS = 100
    model = models.LdaModel(corpus_bow, id2word=dictionary, num_topics=N_TOPICS)
    print "================= LDA MODEL IS BUILT ================="
    model.save(LdaModelFile)

    topics = model.show_topics(num_topics=N_TOPICS, log=True, formatted=True)
    with open(LdaTopicsFile,"wt") as outf:
        for topic in topics:
            # topic[0]: topic number
            # topic[1]: topic description
            outf.write("\n####################### TOPIC {} #######################\n".format(topic[0]))
            outf.write(topic[1]+"\n")

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

    # save_bow()
    # save_tfidf()
    # lsi_model_topics()
    lda_model_topics()
