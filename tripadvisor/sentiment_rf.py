
import os,sys
parentpath = os.path.abspath("..")
if parentpath not in sys.path:
    sys.path.append(parentpath)

import numpy as np
import cPickle
import nltk
from sklearn.feature_extraction.text import CountVectorizer,TfidfTransformer
from sklearn.grid_search import GridSearchCV,RandomizedSearchCV
from sklearn.cross_validation import PredefinedSplit
from sklearn.ensemble import RandomForestClassifier
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

def make_train_validate_split(total,validate_ratio=0.3):
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


def search_best_rf():
    Xtrain_raw, ytrain_raw = load_raw_data("sentidata_train_raw.pkl")
    print "training data loaded"
    print_label_frequency(ytrain_raw)

    ############# create the pipeline
    pipeline = Pipeline([
        ('vect', CountVectorizer(analyzer=do_nothing)),
        ('tfidf', TfidfTransformer()),
        ('rf', RandomForestClassifier(oob_score=True, verbose=1)),
    ])

    ############# initialize the search
    parameters = {
        'vect__max_features': (2000,3000,4000),
        'rf__n_estimators': range(300,1200,100),
        'rf__criterion':['gini','entropy'],
        'rf__max_depth': range(10,100,10),
        'rf__min_samples_split': range(10,100,10),
    }
    validate_split = PredefinedSplit(test_fold=make_train_validate_split(len(ytrain_raw)))

    scoring_method = "roc_auc"
    searchcv = RandomizedSearchCV(estimator=pipeline,
                                param_distributions=parameters,
                                n_iter=200,
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
    common.dump_predictor("pipeline_rf.pkl",bestpipeline)

    rf = bestpipeline.steps[-1][1]
    print "RF's OOB score: {}".format(rf.oob_score_)

    # words = bestpipeline.steps[0][1].get_feature_names()
    # feat_importances = zip(words, rf.feature_importances_)
    # feat_importances.sort(key=lambda t: -t[1])
    # print feat_importances

    ############# training error analysis
    ytrain_predict = bestpipeline.predict(Xtrain_raw)
    print_classification_report('Training Data', ytrain_raw, ytrain_predict)

    ############# test error analysis
    Xtest_raw, ytest_raw = load_raw_data("sentidata_test_raw.pkl")
    ytest_predict = bestpipeline.predict(Xtest_raw)
    print_classification_report('Testing Data', ytest_raw, ytest_predict)

def test_one_rf():
    Xtrain_raw, ytrain_raw = load_raw_data("sentidata_train_raw.pkl")
    print "training data loaded"
    print_label_frequency(ytrain_raw)

    ############# create the pipeline
    pipeline = Pipeline([
        ('vect', CountVectorizer(analyzer=lambda x:x,max_features=3000)),
        ('tfidf', TfidfTransformer()),
        ('rf', RandomForestClassifier(n_estimators=500,
                                      max_depth=200,
                                      min_samples_split=10,
                                      oob_score=True,
                                      n_jobs=-1,verbose=1,class_weight='balanced')),
    ])

    ############# train
    pipeline.fit(Xtrain_raw,ytrain_raw)

    ############# check result
    rf = pipeline.steps[-1][1]
    rf.oob_score_

    ############# training error
    ytrain_predict = pipeline.predict(Xtrain_raw)
    print classification_report(y_true=ytrain_raw,y_pred=ytrain_predict)
    print confusion_matrix(y_true=ytrain_raw,y_pred=ytrain_predict)

    ############# testing error
    Xtest_raw, ytest_raw = load_raw_data("sentidata_test_raw.pkl")
    ytest_predict = pipeline.predict(Xtest_raw)
    accuracy_score(y_true=ytest_raw,y_pred=ytest_predict)
    print classification_report(y_true=ytest_raw,y_pred=ytest_predict)


if __name__ == "__main__":
    search_best_rf()