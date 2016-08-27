import os
import sys

parentpath = os.path.abspath("..")
if parentpath not in sys.path:
    sys.path.append(parentpath)

import numpy as np
from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import CountVectorizer,TfidfTransformer
from sklearn.grid_search import GridSearchCV
from sklearn.pipeline import Pipeline

import common
import ta_common as tac

def search_best_svc():
    Xtrain_all, ytrain_all = tac.load_raw_data("sentidata_train_raw.pkl")
    tac.print_label_frequency("Training Data",ytrain_all)

    ############# create the pipeline
    pipeline = Pipeline([
        ('vect', CountVectorizer(analyzer=tac.do_nothing)),
        ('tfidf', TfidfTransformer()),
        ('svc', LinearSVC(dual=False, verbose=1)),# dual=False when #samples>#features
    ])

    ############# initialize the search
    parameters = {
        'vect__max_features': (2000,3000,4000, 5000),
        'svc__C': np.logspace(-3,3,7),
        'svc__penalty': ['l1','l2']
    }
    scoring_method = "roc_auc"
    validate_split = tac.make_train_validate_split(len(ytrain_all))
    searchcv = GridSearchCV(estimator=pipeline,
                            param_grid=parameters,
                            scoring=scoring_method,
                            n_jobs=-1,
                            verbose=1,
                            cv = validate_split)

    ############# search
    print "#################### search cv begins"
    searchcv.fit(Xtrain_all, ytrain_all)
    print "#################### search cv ends"
    print "best {}: {}".format(scoring_method, searchcv.best_score_)
    print "best parameters: ", searchcv.best_params_

    ############# save the best model
    bestpipeline = searchcv.best_estimator_
    common.simple_dump("sentimodel_svc.pkl",bestpipeline)

    ############# training error analysis
    print "************************* Training Data *************************"
    ytrain_predict = bestpipeline.predict(Xtrain_all)
    tac.print_classification_report('Training Data',ytrain_all,ytrain_predict)

    ############# test error analysis
    print "************************* Test Data *************************"
    Xtest, ytest = tac.load_raw_data("sentidata_test_raw.pkl")
    tac.print_label_frequency("Testing Data",ytest)

    ytest_predict = bestpipeline.predict(Xtest)
    tac.print_classification_report('Testing Data',ytest,ytest_predict)

def crossval_generate_meta_features():
    Xtrain_all, ytrain_all = tac.load_raw_data("sentidata_train_raw.pkl")

    pipeline = common.simple_load("sentimodel_svc.pkl",1)[0]
    yvalidates = tac.crossval_predict("svc",pipeline,Xtrain_all,ytrain_all,"label")

    tac.print_classification_report("validation",ytrue=ytrain_all,ypredict=yvalidates["svc_label"])
    yvalidates.to_csv("svc_meta_features.csv")

if __name__ == "__main__":
    # search_best_svc()
    crossval_generate_meta_features()