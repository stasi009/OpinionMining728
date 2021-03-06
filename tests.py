
import logging
import nltk
import common
from sentence import Sentence
from aspect_segmentation import AspectSegmentation
from negation_suffix import NegationSuffixAdder

def test_sentence():
    texts = [   "can't is a contraction",
                "she isn't my wife",
                "I'm a Chinese",
                "1630 NE Valley Rd, Pullman, WA, 99163, Apt X103",
                "I should've done that thing I didn't do",
                "2ND place",
                "bye, Pullman, bye, USA"]

    for index,text in enumerate(texts):
        sent = Sentence(text)
        print "\n******************** {}".format(index+1)

        print sent.raw
        print "===>"
        print sent.words

def test_lemmatize_with_pos():
    text = "The restaurants nearby are better than the shops further away"
    words = nltk.word_tokenize(text)
    lemmatizer = nltk.WordNetLemmatizer()
    print utility.lemmatize_with_pos(lemmatizer,words)

def test_aspect_segmentation():
    seed_aspect_keywords = {
        "Room": set(["room", "suite", "view", "bed","spacious"]),
        "Location": set(["location", "traffic", "minute", "restaurant","sight"]),
        "Service": set(["staff", "greet","check", "help","service"]),
    }
    reviews = ["Wonderful facilities, comfortable beds and an excellent location. The staff at the Hotel are extremely friendly and helpful. The ensuite bathroom is modern, spcaious and comfortable. The spa, gym and pool are easily accessible with comfortable changing facilities. There a lots of shops locally and if you are sightseeing, there is easy access via the metro at Concorde to the sights to the north and south as well as being virtually on top of the Louvre and the Musee D'Orsay."]

    extra_stop_words = ["hotel","great"]
    segmenter = AspectSegmentation(reviews,seed_aspect_keywords,extra_stop_words)
    segmenter.run_once()

    # print final aspect keywords
    for aspect,keywords in segmenter._aspect_keywords.iteritems():
        print "\nAspect<{}> has keywords: \n{}\n".format(aspect,keywords)

def test_negation_suffix():
    stopwords = common.make_stop_words()
    sentences = [   "I don't like Beijing 123, because it's too expensive", "I cannot 4 run away 56, since I am a grown man",
                    "never ever come back again, I swear to god","without any problem","I don't think I will enjoy it: it might be too spicy" ]
    for index,raw_sent in enumerate(sentences):
        sentence = Sentence.from_raw(raw_sent,stopwords)
        print "\n=========================== [{}]".format(index+1)
        print sentence.raw
        print sentence.words

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    # test_sentence()
    # test_lemmatize_with_pos()
    # test_aspect_segmentation()
    test_negation_suffix()
