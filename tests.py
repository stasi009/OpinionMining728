
import nltk
import utility
import text_cleaner

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

if __name__ == "__main__":
    # test_clean()
    test_lemmatize_with_pos()
