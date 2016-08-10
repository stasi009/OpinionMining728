
import nltk
from nltk.corpus import stopwords
from text_cleaner import TextCleaner
import utility

class AspectSentence(object):
    """
    data structure which represents a sentence during the process of 'aspect segmentation'
    """
    StopWords = frozenset(stopwords.words("english"))# frozenset has better performance
    Cleaner = TextCleaner()
    Lemmatizer = nltk.WordNetLemmatizer()

    def __init__(self,raw_sentence):
        self.raw_sentence = raw_sentence
        # clean
        # 1. expand abbrevations and contractions
        # 2. remove non-letters
        # 3. change to all lower case
        clean_sentence = AspectSentence.Cleaner.clean(self.raw_sentence)

        # tokenize into words
        words = nltk.word_tokenize( clean_sentence )

        # remove stopwords
        words = [w for w in words if w not in AspectSentence.StopWords]

        # lemmatize
        self.words = utility.lemmatize_with_pos(AspectSentence.Lemmatizer,words)

if __name__ == "__main__":
    """
    unit tests
    """
    text = "It was my second stay at the Mandarin Oriental Paris and I can only reconfirm my first impression... MOP is a wonderful, modern property-centrally located with spacious rooms and a truly excellent service. Everything I expected and much more was delivered flawlessy with enthusiasm and lots of care."
    sentence = AspectSentence(text)
    print sentence.raw_sentence
    print "===============>"
    print sentence.words
