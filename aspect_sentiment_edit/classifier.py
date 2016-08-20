
import cPickle

class Classifier(object):

    def __init__(self,pkl_file):
        with open(pkl_file,"rb") as inf:
            self.classifier = cPickle.load(inf)
        print "classifier is loaded"

    def classify(self,review):
        for sentence in review.sentences:
            features = {}.fromkeys(sentence.words_no_negsuffix(),True)
            sentence.aspect = self.classifier.classify(features)
