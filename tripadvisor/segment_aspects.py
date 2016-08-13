
import random
random.seed(689)

import os,sys
sys.path.append(os.path.abspath(".."))

import glob
import json
import nltk
from nltk.corpus import stopwords
from tqdm import tqdm

from entities import Hotel
from sentence import Sentence
from aspect_segmentation import AspectSegmentation

def select_hotels(n_hotels):
    json_files = glob.glob( "data/*.json" )
    return random.sample(json_files,n_hotels)

def get_raw_sentence_stream(hotel_files):
    sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    for hfile in hotel_files:
        hotel = Hotel(hfile)

        for review in hotel.reviews:
            if len(review.title) >0:
                yield review.title

            for sentence in sent_tokenizer.tokenize(review.content):
                yield sentence

def preproc_save_sentences(filename,raw_sent_stream,extra_stopwords = None):
    stop_words = set(stopwords.words("english"))
    if extra_stopwords is not None:
        stop_words |= set(extra_stopwords)

    with open(filename,"wt") as outf:
        outf.write("[")

        for index,raw_sent in enumerate( raw_sent_stream):
            prev_terminator = '\n' if index ==0 else ',\n'
            sentence = Sentence.from_raw(raw_sent,stop_words)
            if len(sentence.words)>0:
                outf.write(prev_terminator + sentence.dump_json())
                print "{}-th sentence processed and saved".format(index+1)

        outf.write("\n]")

def task_preproc_save_sentences(sent_file,n_hotels):
    extra_stopwords = ["hotel","room","great","also","place","would"]
    hotel_files = select_hotels(n_hotels)
    raw_sent_stream = get_raw_sentence_stream(hotel_files)
    preproc_save_sentences(sent_file,raw_sent_stream,extra_stopwords)

def save_segmentation_results(segmenter,outfname):
    # json doesn't support set, so transform into list
    keywords = {k:list(v) for k,v in segmenter._aspect_keywords.iteritems() }
    sentences = [ {"aspect":sent.aspect,"raw":sent.raw} for sent in segmenter._sentences]
    dd = {"keywords": keywords,"sentences":sentences}

    with open(outfname,"wt") as outf:
        json.dump(dd,outf,indent=4)

def segment_aspects(input_fname,out_fname):
    print "begin loading sentences, ......"
    with open(input_fname,"rt") as inf:
        dd = json.load(inf)
        sentences = [ Sentence.from_json(d) for d in dd]
    print "{} sentences loaded".format(len(sentences))

    ######### for test and debug
    # sentences = random.sample(sentences,2000)
    ######### end test and debug

    seed_aspect_keywords = {
        "Overall":set(["recommend","recommendation","love","return","best","regret","rating"]),
        "Value": set(["value", "price", "quality", "worth"]),
        "Room": set([ "suite", "view", "bed","spacious","noisy","small"]),
        "Location": set(["location", "traffic", "minute", "parking","restaurant","shop","locate","subway","bus","airport","downtown"]),
        "Cleanliness": set(["clean", "dirty", "maintain", "smell"]),
        "Service": set(["staff","check", "help","service","helpful","friendly"]),
        "Business service": set(["business", "center", "computer", "internet","wifi","free"])
    }
    segmenter = AspectSegmentation(sentences,seed_aspect_keywords)
    segmenter.run()

    # save resuls
    print "begin dumping the results, ......"
    save_segmentation_results(segmenter,out_fname)
    print "!!! DONE !!!"

if __name__ == "__main__":
    # task_preproc_save_sentences("sentences.json",500)
    segment_aspects("sentences.json","aspect_tagged_sentences.json")
