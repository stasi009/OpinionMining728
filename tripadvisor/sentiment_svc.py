

import os,sys
parentpath = os.path.abspath("..")
if parentpath not in sys.path:
    sys.path.append(parentpath)

import numpy as np
import cPickle
import nltk
from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import CountVectorizer,TfidfTransformer
from sklearn.grid_search import GridSearchCV,RandomizedSearchCV
from sklearn.cross_validation import PredefinedSplit
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

def print_label_frequency(y):
    freqdist = nltk.FreqDist()
    for l in y:
        freqdist[l] +=1

    print "totally {} labels".format(freqdist.N())
    for k in freqdist.iterkeys():
        print "\tLabel[{}]: {:.2f}%".format(k,freqdist.freq(k) * 100)

def make_train_validate_split(total,validate_ratio=0.333):
    # when using a validation set,
    # set the test_fold to 0 for all samples that are part of the validation set,
    # and to -1 for all other samples.
    folds_flag = np.full((total,),-1,dtype=np.int)

    n_validates = int(total * validate_ratio)
    folds_flag[-n_validates:] = 0

    return folds_flag

def do_nothing(x):
    """ since lamba cannot pickled and distributed among multiple process
        I have to create this stupid wrap function to let the task can be parallelized """
    return x

def print_classification_report(title,ytrue,ypredict):
    print "\n******************* {} *******************".format(title)
    print "Accuracy: {}\n".format(accuracy_score(y_true=ytrue,y_pred=ypredict))
    print classification_report(y_true=ytrue,y_pred=ypredict)
    print ""
    print confusion_matrix(y_true=ytrue,y_pred=ypredict)

def search_best_svc():
    Xtrain_raw, ytrain_raw = load_raw_data("sentidata_train_raw.pkl")
    print "training data loaded"
    print_label_frequency(ytrain_raw)

    ############# create the pipeline
    pipeline = Pipeline([
        ('vect', CountVectorizer(analyzer=do_nothing)),
        ('tfidf', TfidfTransformer()),
        ('svc', LinearSVC(dual=False, verbose=1)),# dual=False when #samples>#features
    ])

    ############# initialize the search
    parameters = {
        'vect__max_features': (2000,3000,4000),
        'svc__C': [0.001,0.01,0.1,1,10,100,1000],
        'svc__penalty': ['l1','l2'],
        #'svc__class_weight': [None,'balanced']
    }

    scoring_method = "roc_auc"
    validate_split = PredefinedSplit(test_fold=make_train_validate_split(len(ytrain_raw)))
    searchcv = GridSearchCV(estimator=pipeline,
                            param_grid=parameters,
                            scoring=scoring_method,
                            n_jobs=-1,
                            verbose=1,
                            cv = validate_split)

    ############# search
    print "#################### search cv begins"
    searchcv.fit(Xtrain_raw, ytrain_raw)
    print "#################### search cv ends"
    print "best {}: {}".format(scoring_method, searchcv.best_score_)
    print "best parameters: ", searchcv.best_params_

    ############# check the best model
    bestpipeline = searchcv.best_estimator_
    common.dump_predictor("pipeline_svc.pkl",bestpipeline)

    ############# training error analysis
    ytrain_predict = bestpipeline.predict(Xtrain_raw)
    print_classification_report('Training Data',ytrain_raw,ytrain_predict)

    ############# test error analysis
    Xtest_raw, ytest_raw = load_raw_data("sentidata_test_raw.pkl")
    ytest_predict = bestpipeline.predict(Xtest_raw)
    print_classification_report('Testing Data',ytest_raw,ytest_predict)

if __name__ == "__main__":
    search_best_svc()