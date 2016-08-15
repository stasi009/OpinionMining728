
import re
import json
from collections import Counter
import nltk
from nltk.corpus import stopwords
import common

ReplacePatterns = [
                    (r'won\'t', 'will not'),
                    (r'can\'t', 'cannot'),
                    (r'i\'m', 'i am'),
                    (r'ain\'t', 'is not'),
                    (r'(\w+)\'ll', '\g<1> will'),
                    (r'(\w+)n\'t', '\g<1> not'),
                    (r'(\w+)\'ve', '\g<1> have'),
                    (r'(\w+)\'s', '\g<1> is'),
                    (r'(\w+)\'re', '\g<1> are'),
                    (r'(\w+)\'d', '\g<1> would'),
                    (r'1st','first'),
                    (r'2nd','second'),
                    (r'3rd','third'),
                    ]

class Sentence(object):
    """
    data structure which represents a sentence during the process of 'aspect segmentation'
    """
    ReplacePatterns = [(re.compile(regex,re.IGNORECASE),replacewith)  for regex,replacewith in ReplacePatterns]
    Lemmatizer = nltk.WordNetLemmatizer()

    def __init__(self,raw = None,words = None, aspect=common.AspectUnknown, sentiment=common.SentimentUnknown):
        self.raw = raw
        self.words = words
        self.aspect = common.AspectUnknown if aspect is None else aspect
        self.sentiment = common.SentimentUnknown if sentiment is None else sentiment

    def to_dict(self):
        return {"raw":self.raw,"words":self.words,"aspect":self.aspect,"sentiment":self.sentiment}

    @staticmethod
    def from_raw(sentence,stop_words = None):
        sent = Sentence(sentence)

        ############### expand contraction and abbrevations
        for (pattern, replacewith) in Sentence.ReplacePatterns:
            sentence = re.sub(pattern, replacewith, sentence)

        ############### only keep letters
        sentence = re.sub("[^a-zA-Z]", " ", sentence)

        ############### normalize to lower case
        sentence = sentence.lower()

        ############### tokenize into words
        words = nltk.word_tokenize( sentence )

        ############### lemmatize
        # !!! Notice the order is important
        # !!! given ["the","parking","is","crazy"], nltk.pos_tag can recognize "parking" as Noun,
        # !!! lemmatize will return "parking"
        # !!! however, if we remove stopwords first, given ["parking","crazy"],
        # !!! nltk.pos_tag will think "parking" as Verb
        # !!! and lemmatize return "park"
        words = common.lemmatize_with_pos(Sentence.Lemmatizer,words)

        ############### remove stopwords
        if stop_words is None:
            stop_words = set(stopwords.words("english"))
        words = [w for w in words if len(w)>1 and w not in stop_words]

        #
        sent.words = words
        return sent

    @staticmethod
    def from_dict(d):
        return Sentence(d.get("raw",None),d.get("words",None),\
        d.get("aspect",common.AspectUnknown),d.get("sentiment",common.SentimentUnknown))
