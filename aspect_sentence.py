
from collections import Counter
import nltk
from text_cleaner import TextCleaner
import utility

class AspectSentence(object):
    """
    data structure which represents a sentence during the process of 'aspect segmentation'
    """
    Cleaner = TextCleaner()
    Lemmatizer = nltk.WordNetLemmatizer()

    def __init__(self,raw_sentence,stop_words):
        self.raw_sentence = raw_sentence

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
        words = [w for w in words if w not in stop_words]

        # lemmatize
        words = utility.lemmatize_with_pos(AspectSentence.Lemmatizer,words)

        self.words = Counter(words)

    def match(self,aspects_keywords):
        """
        aspects_keywords must be a dictionary
        key: a string representing the aspect
        value: a set which contains the key words for that aspect
        """
        aspects_matched = Counter()

        for w,c in self.words.iteritems():
            for aspect,keywords in aspects_keywords.iteritems():
                if w in keywords:
                    aspects_matched[aspect] += c

        if len(aspects_matched) == 0: # no match
            self.aspect = None
        else:

            top_aspect,top_match = aspects_matched.most_common(1)[0]
            assert top_match > 0
            self.aspect = top_aspect

if __name__ == "__main__":
    """
    unit tests
    """
    text = "It was my second stay at the Mandarin Oriental Paris and I can only reconfirm my first impression... MOP is a wonderful, modern property-centrally located with spacious rooms and a truly excellent service. Everything I expected and much more was delivered flawlessy with enthusiasm and lots of care."
    sentence = AspectSentence(text)
    print sentence.raw_sentence
    print "===============>"
    print sentence.words
