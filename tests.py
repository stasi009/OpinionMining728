
import logging
import nltk
import utility
import text_cleaner
import aspect_segmentation

def test_clean():
    cleaner = text_cleaner.TextCleaner()
    texts = [   "can't is a contraction",
                "I'm a Chinese",
                "1630 NE Valley Rd, Pullman, WA, 99163, Apt X103",
                "I should've done that thing I didn't do",
                "2ND place",
                "bye, Pullman, bye, USA"]

    for index,text in enumerate(texts):
        print "******************** {}".format(index+1)
        print text
        print "===>"
        print cleaner.clean(text)

def test_lemmatize_with_pos():
    text = "The restaurants nearby are better than the shops further away"
    words = nltk.word_tokenize(text)
    lemmatizer = nltk.WordNetLemmatizer()
    print utility.lemmatize_with_pos(lemmatizer,words)

def test_aspect_segmentation():
    # seed_aspect_keywords = {
    #     "Value": set(["value", "price", "quality", "worth"]),
    #     "Room": set(["room", "suite", "view", "bed","spacious"]),
    #     "Location": set(["location", "traffic", "minute", "restaurant","sight"]),
    #     "Cleanliness": set(["clean", "dirty", "maintain", "smell"]),
    #     "Service": set(["staff", "greet","check", "help","service"]),
    #     "Business service": set(["business", "center", "computer", "internet"])
    # }
    seed_aspect_keywords = {
        "Room": set(["room", "suite", "view", "bed","spacious"]),
        "Location": set(["location", "traffic", "minute", "restaurant","sight"]),
        "Service": set(["staff", "greet","check", "help","service"]),
    }
    reviews = ["Wonderful facilities, comfortable beds and an excellent location. The staff at the Hotel are extremely friendly and helpful. The ensuite bathroom is modern, spcaious and comfortable. The spa, gym and pool are easily accessible with comfortable changing facilities. There a lots of shops locally and if you are sightseeing, there is easy access via the metro at Concorde to the sights to the north and south as well as being virtually on top of the Louvre and the Musee D'Orsay."]

    segmenter =  aspect_segmentation.AspectSegmentation(reviews,seed_aspect_keywords)
    segmenter.run_once()

    # print final aspect keywords
    for aspect,keywords in segmenter._aspect_keywords.iteritems():
        print "\nAspect<{}> has keywords: \n{}\n".format(aspect,keywords)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    # test_clean()
    # test_lemmatize_with_pos()
    test_aspect_segmentation()
