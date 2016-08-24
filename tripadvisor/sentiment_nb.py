


import os,sys
parentpath = os.path.abspath("..")
if parentpath not in sys.path:
    sys.path.append(parentpath)

import numpy as np
import cPickle
import itertools

import nltk
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer,TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score,classification_report,confusion_matrix

import common

def load_raw_data(filename):
    with open(filename,"rb") as inf:
        raw_data = cPickle.load(inf)

    X_raw = []
    y_raw = []
    for words,rating in raw_data:
        # ignore the edge case when rating == 3
        if rating <=2:
            X_raw.append(words)
            y_raw.append(1)# negative
        elif rating >= 4:
            X_raw.append(words)
            y_raw.append(0)# positive

    return X_raw,y_raw

def nltk_features(words_list,labels):
    return [ ( {}.fromkeys(words,True), label) for words,label in itertools.izip(words_list,labels)]

def print_label_frequency(y):
    freqdist = nltk.FreqDist()
    for l in y:
        freqdist[l] +=1

    print "totally {} labels".format(freqdist.N())
    for k in freqdist.iterkeys():
        print "\tLabel[{}]: {:.2f}%".format(k,freqdist.freq(k) * 100)


def print_classification_report(title,ytrue,ypredict):
    print "\n******************* {} *******************".format(title)
    print "Accuracy: {}\n".format(accuracy_score(y_true=ytrue,y_pred=ypredict))
    print classification_report(y_true=ytrue,y_pred=ypredict)
    print ""
    print confusion_matrix(y_true=ytrue,y_pred=ypredict)

def run_naive_bayes(use_tfidf):
    Xtrain_raw, ytrain_raw = load_raw_data("sentidata_train_raw.pkl")
    print "training data loaded"
    print_label_frequency(ytrain_raw)

    ############# create the pipeline
    pipeline = None
    if use_tfidf:
        pipeline = Pipeline([
            ('vect', CountVectorizer(analyzer=lambda x:x)),
            ('tfidf', TfidfTransformer()),
            ('nb', MultinomialNB())
        ])
    else:
        pipeline = Pipeline([
            ('vect', CountVectorizer(analyzer=lambda x: x)),
            ('nb', MultinomialNB())
        ])

    ############# fit
    pipeline.fit(Xtrain_raw, ytrain_raw)

    ############# training error analysis
    ytrain_predict = pipeline.predict(Xtrain_raw)
    print_classification_report('Training Data',ytrain_raw,ytrain_predict)

    ############# test error analysis
    Xtest_raw, ytest_raw = load_raw_data("sentidata_test_raw.pkl")
    ytest_predict = pipeline.predict(Xtest_raw)
    print_classification_report('Testing Data',ytest_raw,ytest_predict)

def nltk_nb():
    Xtrain_raw, ytrain_raw = load_raw_data("sentidata_train_raw.pkl")
    print "\ntraining data distribution"
    print_label_frequency(ytrain_raw)

    train_features = nltk_features(Xtrain_raw,ytrain_raw)
    classifier = nltk.NaiveBayesClassifier.train(train_features)

    # training errors
    ytrain_predict = classifier.classify_many([t[0] for t in train_features])
    print_classification_report('Training Data', ytrain_raw, ytrain_predict)

    # test error
    Xtest_raw, ytest_raw = load_raw_data("sentidata_test_raw.pkl")
    print "\ntest data distribution"
    print_label_frequency(ytest_raw)

    test_features = nltk_features(Xtest_raw,ytest_raw)

    ytest_predict = classifier.classify_many([t[0] for t in test_features])
    print_classification_report('Testing Data', ytest_raw, ytest_predict)


if __name__ == "__main__":
    run_naive_bayes(False)
    # nltk_nb()