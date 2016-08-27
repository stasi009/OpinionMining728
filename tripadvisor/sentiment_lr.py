import os
import sys

parentpath = os.path.abspath("..")
if parentpath not in sys.path:
    sys.path.append(parentpath)

from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.grid_search import GridSearchCV
from sklearn.pipeline import Pipeline

import common
import ta_common as tac

def search_best_lr():
    Xtrain_all, ytrain_all = tac.load_raw_data("sentidata_train_raw.pkl")
    tac.print_label_frequency("Training",ytrain_all)

    ############# create the pipeline
    pipeline = Pipeline([
        ('vect', CountVectorizer(analyzer=tac.do_nothing)),
        ('tfidf', TfidfTransformer()),
        ('lr', LogisticRegression(dual=False, verbose=1)),  # dual=False when #samples>#features
    ])

    ############# initialize the search
    parameters = {
        'vect__max_features': (1000, 2000, 3000, 4000,50000),
        'lr__C': [0.001, 0.01, 0.1, 1, 10, 100, 1000],
        'lr__penalty': ['l2','l1'],
    }
    scoring_method = "roc_auc"
    validate_split = tac.make_train_validate_split(len(ytrain_all))
    searchcv = GridSearchCV(estimator=pipeline,
                            param_grid=parameters,
                            scoring=scoring_method,
                            n_jobs=-1,
                            verbose=1,
                            cv=validate_split)

    ############# search
    print "#################### search cv begins"
    searchcv.fit(Xtrain_all, ytrain_all)
    print "#################### search cv ends"
    print "best {}: {}".format(scoring_method, searchcv.best_score_)
    print "best parameters: ", searchcv.best_params_

    ############# save the best model
    bestpipeline = searchcv.best_estimator_
    common.simple_dump("pipeline_lr.pkl", bestpipeline)

    ############# training error analysis
    ytrain_predict = bestpipeline.predict(Xtrain_all)
    tac.print_classification_report('Training Data', ytrain_all, ytrain_predict)

    ############# test error analysis
    Xtest, ytest = tac.load_raw_data("sentidata_test_raw.pkl")
    tac.print_label_frequency("Testing",ytest)

    ytest_predict = bestpipeline.predict(Xtest)
    tac.print_classification_report('Testing Data', ytest, ytest_predict)


if __name__ == "__main__":
    search_best_lr()
