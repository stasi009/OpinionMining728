
import random
random.seed(689)

import os,sys
sys.path.append(os.path.abspath(".."))

import nltk
from nltk.corpus import stopwords
import logging
import glob
from gensim import corpora,models
from entities import Hotel
import sentence

DictionaryFile = "ta.dict"
BowFile = "ta_bow.mm"
TfidfFile = "ta_tfidf.mm"
LsiModelFile = "ta_model.lsi"
LsiTopicsFile = "ta_lsi_topics.txt"
LdaModelFile = "ta_model.lda"
LdaTopicsFile = "ta_lda_topics.txt"

def select_hotels(n_hotels):
    json_files = glob.glob( "data/*.json" )
    return random.sample(json_files,n_hotels)

def words_stream(hotel_files,extra_stopwords = None):
    """
    what's the scale of each text? a review or a sentence? we should experiement on this problem.
    """
    stop_words = set(stopwords.words("english"))
    if extra_stopwords is not None:
        stop_words |= set(extra_stopwords)

    for hindex,hfile in enumerate(hotel_files):
        hotel = Hotel(hfile)

        for rindex,review in enumerate(hotel.reviews):
            review_text = review.title + ". " + review.content if len(review.title) >0 else review.content

            # treat the whole review as one long sentence
            sent = sentence.Sentence(review_text,stop_words)
            yield sent.words

            print "{}-th hotel's {}-th review processed".format(hindex+1,rindex+1)

def build_dictionary(hotel_files,extra_stopwords=None):
    stream_of_words = words_stream(hotel_files,extra_stopwords)
    dictionary = corpora.Dictionary(stream_of_words)
    dictionary.save(DictionaryFile)  # store the dictionary, for future reference
    print "==================== Dictionary Generated and Saved ===================="

class Corpus(object):
    def __init__(self,hotel_files,extra_stopwords = None):
        self._dictionary = corpora.Dictionary.load(DictionaryFile)
        self._hotel_files = hotel_files

    def __iter__(self):
        stream_of_words = words_stream(hotel_files,extra_stopwords)
        for words in stream_of_words:
            yield self._dictionary.doc2bow(words)

def save_bow(hotel_files,extra_stopwords=None):
    corpus = Corpus(hotel_files,extra_stopwords)
    corpora.MmCorpus.serialize(BowFile,corpus)
    print "==================== BOW data Generated and Saved ===================="

def save_tfidf():
    corpus_bow = corpora.MmCorpus(BowFile)
    tfidf_model = models.TfidfModel(corpus_bow)

    corpus_tfidf = tfidf_model[corpus_bow]
    corpora.MmCorpus.serialize(TfidfFile,corpus_tfidf)

    print "==================== TF-IDF data Generated and Saved ===================="

def save_topics(model,filename):
    with open(filename,"wt") as outf:
        # ---------- write each topic and words' contribution
        topics = model.show_topics(num_topics=-1, log=False, formatted=True)
        for topic in topics:
            # topic[0]: topic number
            # topic[1]: topic description
            outf.write("\n############# TOPIC {} #############\n".format(topic[0]))
            outf.write(topic[1]+"\n")

        # ---------- words statistics in all topics
        outf.write("\n\n\n****************** KEY WORDS ******************\n")
        topics = model.show_topics(num_topics=-1, log=False, formatted=False)
        keywords = (word for (_,words) in topics for (word,score) in words)

        fdist = nltk.FreqDist(keywords)
        for index,(w,c) in enumerate( fdist.most_common(100) ):
            outf.write("{}-th keyword: <{},{}>\n".format(index+1,w,c))

def lsi_model_topics():
    dictionary = corpora.Dictionary.load(DictionaryFile)
    corpus_tfidf = corpora.MmCorpus(TfidfFile)

    N_TOPICS = 300
    lsi_model = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=N_TOPICS)
    print "================= LSI MODEL IS BUILT ================="

    lsi_model.save(LsiModelFile)
    save_topics(lsi_model,LsiTopicsFile)

def lda_model_topics():
    dictionary = corpora.Dictionary.load(DictionaryFile)
    corpus_bow = corpora.MmCorpus(BowFile)

    N_TOPICS = 100
    model = models.LdaModel(corpus_bow, id2word=dictionary, num_topics=N_TOPICS)
    print "================= LDA MODEL IS BUILT ================="

    model.save(LdaModelFile)
    save_topics(model,LdaTopicsFile)

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

    hotel_files = select_hotels(500)
    extra_stopwords = ["hotel","room","great","also","place"]

    build_dictionary(hotel_files,extra_stopwords)
    save_bow(hotel_files,extra_stopwords)
    save_tfidf()
    lsi_model_topics()
    lda_model_topics()
