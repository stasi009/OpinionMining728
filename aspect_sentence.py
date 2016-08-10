
from collections import Counter
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
        self.aspects_matched = Counter()
        # it is possible that one sentence can have two sub-sentences, and each sub-sentence has its own aspect
        # although it possible, but I think's it is rather rare
        # also, even we want to consider such rare case, store multiple possible aspects won't help much in later calculation
        self.aspect = None

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
        words = utility.lemmatize_with_pos(AspectSentence.Lemmatizer,words)

        self.words = Counter(words)

    def match(self,aspects_keywords):
        """
        aspects_keywords must be a dictionary
        key: a string representing the aspect
        value: a set which contains the key words for that aspect
        """
        self.aspects_matched.clear()

        for w,c in self.words:
            for aspect,keywords in aspects_keywords:
                if w in keywords:
                    self.aspects_matched[aspect] += c

        top_aspect,top_match = self.aspects_matched.most_common(1)
        # if the sentence describes no aspect, then all its matched count is 0
        # then such sentence's aspect is None
        self.aspect = top_aspect if top_match >0 else None

if __name__ == "__main__":
    """
    unit tests
    """
    text = "It was my second stay at the Mandarin Oriental Paris and I can only reconfirm my first impression... MOP is a wonderful, modern property-centrally located with spacious rooms and a truly excellent service. Everything I expected and much more was delivered flawlessy with enthusiasm and lots of care."
    sentence = AspectSentence(text)
    print sentence.raw_sentence
    print "===============>"
    print sentence.words
