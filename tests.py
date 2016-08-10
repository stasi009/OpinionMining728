
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
    seed_aspect_keywords = {
        "Value": set(["value", "price", "quality", "worth"]),
        "Room": set(["room", "suite", "view", "bed"]),
        "Location": set(["location", "traffic", "minute", "restaurant"]),
        "Cleanliness": set(["clean", "dirty", "maintain", "smell"]),
        "Check In":set(["stuff", "check", "help", "reservation"]),
        "Service": set(["service", "food", "breakfast", "buffet"]),
        "Business service": set(["business", "center", "computer", "internet"])
    }
    reviews = ["The location is obviously great and see nice decor as expected for a recently built hotel. The service is slightly better than a big global franchise like a Park Hyatt. They don't have the personal touch of the Peninsula for those who know how good they are. I would guess those from the near east are just waiting for a Jumeriah to open... The rooms are not astounding, I stayed in an \"Atelier\" suite and it felt claustrophobic--surprising--considering what a couple thousand euros a night would get you nearby. You get an inconsistent level of service, an inconsistent level of attentiveness. In general, perhaps it is overpriced for what you get? H\u00f4tel de Crillon, or Ritz Paris, anyone?"]

    segmenter =  aspect_segmentation.AspectSegmentation(reviews,seed_aspect_keywords)
    segmenter.run_once()

if __name__ == "__main__":
    # logging.basicConfig(level=logging.DEBUG)

    # test_clean()
    # test_lemmatize_with_pos()
    test_aspect_segmentation()
