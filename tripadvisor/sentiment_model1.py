
import numpy as np
import cPickle
import nltk
from sklearn.feature_extraction.text import CountVectorizer,TfidfTransformer
from sklearn.grid_search import GridSearchCV,RandomizedSearchCV
from sklearn.cross_validation import PredefinedSplit
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

def load_raw_data(filename):
    with open(filename,"rb") as inf:
        raw_data = cPickle.load(inf)

    X_raw = []
    y_raw = []
    for words,rating in raw_data:
        # ignore the edge case when rating == 3
        if rating <=2:
            X_raw.append(words)
            y_raw.append(0)# negative
        elif rating >= 4:
            X_raw.append(words)
            y_raw.append(1)# positive

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
    return x

def dump_predictor(filename,learner):
    with open(filename, 'wb') as outfile:
        cPickle.dump(learner,outfile)

def load_predictor(filename):
    with open(filename,"rb") as infile:
        return cPickle.load(infile)

#################
ps = PredefinedSplit(test_fold=make_train_validate_split(10))
for train_index, test_index in ps:
    print("TRAIN:", train_index, "TEST:", test_index)

if __name__ == "__main__":
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
        'vect__max_features': (3000,4000,5000),
        'rf__n_estimators': range(300,1500,100),
        'rf__criterion':['gini','entropy'],
        'rf__max_depth': range(10,100,10),
        'rf__min_samples_split': range(10,100,10),
    }
    validate_split = PredefinedSplit(test_fold=make_train_validate_split(len(ytrain_raw)))

    searchcv = RandomizedSearchCV(estimator=pipeline,
                                param_distributions=parameters,
                                n_iter=200,
                                n_jobs=-1,
                                verbose=1,
                                cv = validate_split)

    ############# search
    print "#################### search cv begins"
    searchcv.fit(Xtrain_raw, ytrain_raw)
    print "#################### search cv ends"
    print "best score: ", searchcv.best_score_
    print "best parameters: ", searchcv.best_params_

    ############# check the best model
    bestpipeline = searchcv.best_estimator_
    dump_predictor("pipeline_rf.pkl",bestpipeline)

    rf = bestpipeline.steps[-1][1]
    print "RF's OOB score: {}".format(rf.oob_score_)

    words = bestpipeline.steps[0][1].get_feature_names()
    feat_importances = zip(words, rf.feature_importances_)
    feat_importances.sort(key=lambda t: -t[1])
    print feat_importances