import os
import sys

parentpath = os.path.abspath("..")
if parentpath not in sys.path:
    sys.path.append(parentpath)

import itertools

from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer,TfidfTransformer
from sklearn.pipeline import Pipeline

import common
import ta_common as tac

def nltk_features(words_list,labels):
    return [ ( {}.fromkeys(words,True), label) for words,label in itertools.izip(words_list,labels)]


def run_naive_bayes(use_tfidf):
    Xtrain_all, ytrain_all = tac.load_raw_data("sentidata_train_raw.pkl")
    tac.print_label_frequency("Train",ytrain_all)

    ############# create the pipeline
    if use_tfidf:
        pipeline = Pipeline([
            ('vect', CountVectorizer(analyzer=tac.do_nothing)),
            ('tfidf', TfidfTransformer()),
            ('nb', MultinomialNB())
        ])
    else:
        pipeline = Pipeline([
            ('vect', CountVectorizer(analyzer=tac.do_nothing)),
            ('nb', MultinomialNB())
        ])

    ############# fit
    pipeline.fit(Xtrain_all, ytrain_all)
    common.simple_dump("sentimodel_nb.pkl",pipeline)

    ############# training error analysis
    ytrain_predict = pipeline.predict(Xtrain_all)
    tac.print_classification_report('Training Data',ytrain_all,ytrain_predict)

    ############# test error analysis
    Xtest, ytest = tac.load_raw_data("sentidata_test_raw.pkl")
    tac.print_label_frequency("Test",ytest)

    ytest_predict = pipeline.predict(Xtest)
    tac.print_classification_report('Testing Data',ytest,ytest_predict)

# def nltk_nb():
#     Xtrain_raw, ytrain_raw = load_raw_data("sentidata_train_raw.pkl")
#     print "\ntraining data distribution"
#     print_label_frequency(ytrain_raw)
#
#     train_features = nltk_features(Xtrain_raw,ytrain_raw)
#     classifier = nltk.NaiveBayesClassifier.train(train_features)
#
#     # training errors
#     ytrain_predict = classifier.classify_many([t[0] for t in train_features])
#     print_classification_report('Training Data', ytrain_raw, ytrain_predict)
#
#     # test error
#     Xtest_raw, ytest_raw = load_raw_data("sentidata_test_raw.pkl")
#     print "\ntest data distribution"
#     print_label_frequency(ytest_raw)
#
#     test_features = nltk_features(Xtest_raw,ytest_raw)
#
#     ytest_predict = classifier.classify_many([t[0] for t in test_features])
#     print_classification_report('Testing Data', ytest_raw, ytest_predict)

def crossval_generate_meta_features():
    Xtrain_all, ytrain_all = tac.load_raw_data("sentidata_train_raw.pkl")

    pipeline = common.simple_load("sentimodel_nb.pkl",1)[0]
    yvalidates = tac.crossval_predict("nb",pipeline,Xtrain_all,ytrain_all,"probability")

    tac.print_classification_report("validation",ytrue=ytrain_all,ypredict=yvalidates["nb_label"])
    yvalidates.to_csv("nb_meta_features.csv")


if __name__ == "__main__":
    # run_naive_bayes(False)
    # nltk_nb()
    crossval_generate_meta_features()