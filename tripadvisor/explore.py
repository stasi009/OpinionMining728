
import random
random.seed(689)

import os,sys
sys.path.append(os.path.abspath(".."))

import nltk
from nltk.corpus import stopwords
import logging
import glob

from entities import Hotel
import sentence

def review_stream(n_hotels):
    json_files = glob.glob( "data/*.json" )
    selected_hotels = random.sample(json_files,n_hotels)

    for hfile in selected_hotels:
        hotel = Hotel(hfile)
        for review in hotel.reviews:
            review_text = review.title + ". " + review.content if len(review.title) >0 else review.content
            yield review_text

def word_stream(review_stream):
    stop_words = set(stopwords.words("english"))
    for index,review in enumerate(review_stream):
        # treat the whole review as one long sentence
        sent = sentence.Sentence(review,stop_words)

        for word in sent.words:
            yield word

        print "{}-th review processed".format(index+1)

if __name__ == "__main__":
    N_HOTELS = 300
    stream_of_word = word_stream(review_stream(N_HOTELS))
    fdist = nltk.FreqDist(stream_of_word)

    with open("most_common_words.csv","wt") as outf:
        for (word,count) in fdist.most_common(100):
            outf.write("{},{}\n".format(word,count))
