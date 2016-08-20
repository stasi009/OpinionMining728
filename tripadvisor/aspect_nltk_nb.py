
import random
import csv
import cPickle

import nltk
from nltk.classify import NaiveBayesClassifier
from nltk.classify.util import accuracy

import common

def get_samples_stream(filename):
    with open(filename,"rt") as inf:
        reader = csv.reader(inf)
        for row in reader:
            yield (row[0],row[1].split() )

def binary_bow_feature(samples):
    # samples is a list, where each cell is a tuple
    # tuple[0] is the aspect
    # tuple[1] is the words
    # return result is also a list where each cell is a tuple
    # tuple[0] is the features represented by a dictionary
    # tuple[1] is the aspect
    return ( ( {}.fromkeys(words,True),  aspect) for aspect, words in samples  )

def split_samples(all_samples,test_sample_ratio):
    random.shuffle(all_samples)
    test_size = int(len(all_samples) * test_sample_ratio)
    test_samples,train_samples = all_samples[:test_size],all_samples[test_size:]
    return train_samples,test_samples

def classify_multi_labels(classifer,features,confidence=0.8):
    """
    one sentence may talk about multiple aspect
    we just return multiple aspects whose total probability exceeds the confidence
    """
    prob_dist = classifier.prob_classify(features)
    label_probs = [(label,prob_dist[label]) for label in classifer.labels()]
    label_probs.sort(lambda t: t[1],reversed=True)

    raise NotImplemented()

def multilabel_check_accuracy(classifier,samples,confidence = 0.8):
    pass

def naivebayes_classify(filename):
    raw_sample_stream = get_samples_stream(filename)
    all_samples = list( binary_bow_feature(raw_sample_stream) )

    # filter out two classes of outliers
    # these two categories contain too few examples, so the word frequency in these two categories
    # cannot reflect the true probability
    all_samples = [(features,aspect) for features,aspect in all_samples if aspect != common.AspectNothing and aspect != common.AspectBusiness]

    test_sample_ratio = 0.25
    train_samples,test_samples = split_samples(all_samples,test_sample_ratio)
    print "training set has {} samples, test set has {} samples".format(len(train_samples),len(test_samples))

    classifier = NaiveBayesClassifier.train(train_samples)
    print "training completes"

    print "training accuracy: {}".format(accuracy(classifier,train_samples))
    print "test accuracy: {}".format(accuracy(classifier,test_samples))
    classifier.show_most_informative_features(n=10)

    return classifier

if __name__ == "__main__":
    classifier = naivebayes_classify("aspects_train.csv")
    with open("aspect_nltk_naivebayes.pkl","wb") as outf:
        cPickle.dump(classifier,outf)
    print "classifier trained and saved"
