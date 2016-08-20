
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


if __name__ == "__main__":
    statistics_by_aspect()
