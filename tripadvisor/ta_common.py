import cPickle
import numpy as np
import pandas as pd
import nltk
from sklearn.cross_validation import PredefinedSplit, KFold
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


def load_raw_data(filename):
    with open(filename, "rb") as inf:
        raw_data = cPickle.load(inf)

    X_raw = []
    y_raw = []
    for words, rating in raw_data:
        # ignore the edge case when rating == 3
        if rating <= 2:
            X_raw.append(words)
            y_raw.append(0)  # negative
        elif rating >= 4:
            X_raw.append(words)
            y_raw.append(1)  # positive

    return X_raw, y_raw


def print_label_frequency(title, y):
    freqdist = nltk.FreqDist()
    for l in y:
        freqdist[l] += 1

    print "[{}] totally {} labels".format(title, freqdist.N())
    for k in freqdist.iterkeys():
        print "\tLabel[{}]: {:.2f}%".format(k, freqdist.freq(k) * 100)


def do_nothing(x):
    """ since lamba cannot pickled and distributed among multiple process
        I have to create this stupid wrap function to let the task can be parallelized """
    return x


def make_train_validate_split(total, validate_ratio=0.333):
    # when using a validation set,
    # set the test_fold to 0 for all samples that are part of the validation set,
    # and to -1 for all other samples.
    folds_flag = np.full((total,), -1, dtype=np.int)

    n_validates = int(total * validate_ratio)
    folds_flag[-n_validates:] = 0

    return PredefinedSplit(test_fold=folds_flag)


def print_classification_report(title, ytrue, ypredict):
    print "\n******************* {} *******************".format(title)
    print "Accuracy: {}\n".format(accuracy_score(y_true=ytrue, y_pred=ypredict))
    print "Classification Report: "
    print classification_report(y_true=ytrue, y_pred=ypredict)
    print "Confusion Matrix: "
    print confusion_matrix(y_true=ytrue, y_pred=ypredict)


def crossval_predict(prefix, predictor, X, y, result, n_cv=5):
    if not np.array_equal( predictor.classes_, [0, 1]):
        raise Exception("classes labels NOT match")

    X = np.asarray(X)
    y = np.asarray(y)
    n_samples = len(X)
    print "totally {} samples, divided into {} folds".format(n_samples, n_cv)

    if result == "label":
        datas = np.full((n_samples, 1), np.NaN)
        header = "{}_label".format(prefix)
        yvalidates = pd.DataFrame(datas, columns=[header])
    elif result == "probability":
        datas = np.full((n_samples, 3), np.NaN)
        headers = ["{}_{}".format(prefix, t) for t in ["proba", "log_proba", "label"]]
        yvalidates = pd.DataFrame(datas, columns=headers)

    # no need to shuffle, since I can guarantee X is already shuffled before passing into this function
    folds = KFold(n_samples, n_cv)
    for index, (train_index, test_index) in enumerate(folds):
        Xtrain, Xtest = X[train_index], X[test_index]
        ytrain, ytest = y[train_index], y[test_index]

        predictor.fit(Xtrain, ytrain)
        if result == "label":
            yvalidates.iloc[test_index, 0] = predictor.predict(Xtest)
        elif result == "probability":
            ytest_probas = predictor.predict_proba(Xtest)
            pos_proba = ytest_probas[:, 1]  # probability for label=1 (Positive)

            yvalidates.iloc[test_index, 0] = pos_proba
            yvalidates.iloc[test_index, 1] = np.log(pos_proba)
            yvalidates.iloc[test_index, 2] = np.where(pos_proba > 0.5, 1, 0)
        else:
            raise Exception("unknown result type")

        print "====== cross-validated on {}-fold ======".format(index + 1)

    return yvalidates
