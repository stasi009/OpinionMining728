
import os,sys
parentpath = os.path.abspath("..")
if parentpath not in sys.path:
    sys.path.append(parentpath)

import random
import csv
import nltk
from nltk.classify import NaiveBayesClassifier
from nltk.classify.util import accuracy

def get_samples_stream(filename):
    with open(filename,"rt") as inf:
        reader = csv.reader(inf)
        for row in reader:
            yield (row[0],row[1].split() )

def statistics_by_aspect():
    filename = "aspects_train.csv"
    words_dist = nltk.ConditionalFreqDist()
    sample_sizes = nltk.FreqDist()

    samples_stream = get_samples_stream(filename)
    for aspect,words in samples_stream:
        sample_sizes[aspect] += 1
        for word in words:
            words_dist[aspect][word] += 1

    for category,dist in words_dist.iteritems():
        print "\n------- Category: {}".format(category)
        print dist.most_common(20)

    total_samples = sample_sizes.N()
    print "\ntotally {} samples".format(total_samples)
    for aspect, count in sample_sizes.iteritems():
        print "aspect[{}] has {} samples, {:.2f}%".format(aspect,count, count*100.0/total_samples)

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

def print_errors(classifier,samples):
    for features,real_label in samples:
        result_label = classifier.classify(features)
        if result_label != real_label:
            print "\n ############# {}".format(features)
            print "real_label: {}, my result: {}".format(real_label,result_label)

def naivebayes_classify(filename):
    raw_sample_stream = get_samples_stream(filename)
    all_samples = list( binary_bow_feature(raw_sample_stream) )

    test_sample_ratio = 0.25
    train_samples,test_samples = split_samples(all_samples,test_sample_ratio)
    print "training set has {} samples, test set has {} samples".format(len(train_samples),len(test_samples))

    classifier = NaiveBayesClassifier.train(train_samples)
    print "training completes"

    print "training accuracy: {}".format(accuracy(classifier,train_samples))
    print "test accuracy: {}".format(accuracy(classifier,test_samples))
    classifier.show_most_informative_features(n=10)

    print_errors(classifier,all_samples)

    return classifier

if __name__ == "__main__":
    # statistics_by_aspect()
    classifier = naivebayes_classify("aspects_train.csv")
