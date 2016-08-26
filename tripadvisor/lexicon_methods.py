import os, sys

parentpath = os.path.abspath("..")
if parentpath not in sys.path:
    sys.path.append(parentpath)

from tqdm import tqdm
from sentiment_lexicon import SentimentLexicon
import common

def task_calculate_expected_ratings():
    raw_data = common.simple_load("sentidata_train_raw.pkl")

    lexicon = SentimentLexicon(5)
    for words, rating in tqdm(raw_data):
        for word in words:
            lexicon.count(word, rating)
    print "couting finished"

    lexicon.normalize()
    print "complete normalization"

    common.simple_dump("sentiment_lexicon.pkl",lexicon.words)
    print "sentiment lexicon generated and saved"

def inspect_sentiment_lexicon():
    sentiment_lexicon = common.simple_load("sentiment_lexicon.pkl")

    sorted_lexicon = sorted( ((k,v[0]) for k,v in sentiment_lexicon.iteritems() ),key=lambda t: t[1])

    n_toppings = 15
    print sorted_lexicon[: n_toppings]
    print sorted_lexicon[-n_toppings:]

if __name__ == "__main__":
    task_calculate_expected_ratings()


