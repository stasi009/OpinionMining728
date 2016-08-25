
import cPickle
import numpy as np
import nltk
import xgboost as xgb
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score,classification_report,confusion_matrix

def print_label_frequency(title,y):
    freqdist = nltk.FreqDist()
    for l in y:
        freqdist[l] +=1

    print "[{}] totally {} labels".format(title,freqdist.N())
    for k in freqdist.iterkeys():
        print "\tLabel[{}]: {:.2f}%".format(k,freqdist.freq(k) * 100)

def load_raw_data(filename):
    with open(filename,"rb") as inf:
        raw_data = cPickle.load(inf)

    X_raw = []
    y_raw = []
    for words,rating in raw_data:
        # ignore the edge case when rating == 3
        if rating <=2:
            X_raw.append(words)
            # negative, since 'negative' is less frequent, we make 'negative' our primal focus
            y_raw.append(1)
        elif rating >= 4:
            X_raw.append(words)
            y_raw.append(0)# positive

    return X_raw,y_raw

def make_dmatrix(max_words):
    # Xtrain_raw is list of list, each element is a list of words
    Xtrain_raw, ytrain_raw = load_raw_data("sentidata_train_raw.pkl")

    validate_ratio = 0.333
    validate_size = int(len(ytrain_raw) * validate_ratio)

    # split the original train dataset into 'train' and 'validation' sets
    Xvalidate_words, Xtrain_words = Xtrain_raw[:validate_size],Xtrain_raw[validate_size:]
    yvalidate, ytrain = ytrain_raw[:validate_size],ytrain_raw[validate_size:]
    print_label_frequency("Train",ytrain)
    print_label_frequency("Validate",yvalidate)

    # initialize TF-IDF model
    # since we already get a list of words, no need to preprocess and tokenize
    # just return passed-in list of words
    tfidf_vectorizer = TfidfVectorizer(analyzer=lambda x:x,max_features=max_words)
    Xtrain_tfidf = tfidf_vectorizer.fit_transform(Xtrain_words)

    # dmatrix for training: DMatrix can accept sparse matrix as its input
    dmatrix_train = xgb.DMatrix(Xtrain_tfidf,ytrain)
    dmatrix_train.save_binary("train.dmatrix")

    # dmatrix for validation
    Xvaliate_tfidf = tfidf_vectorizer.transform(Xvalidate_words)
    dmatrix_validate = xgb.DMatrix(Xvaliate_tfidf,yvalidate)
    dmatrix_validate.save_binary("validate.dmatrix")

    # dmatrix for test
    Xtest_words,ytest = load_raw_data("sentidata_test_raw.pkl")
    print_label_frequency("Test",ytest)

    Xtest_tfidf = tfidf_vectorizer.transform(Xtest_words)
    dmatrix_test = xgb.DMatrix(Xtest_tfidf,ytest)
    dmatrix_test.save_binary("test.dmatrix")

    #
    return dmatrix_train,dmatrix_validate,dmatrix_test

def predict(title,bst,dmatrix,prob_cutoff=0.5):
    true_label = dmatrix.get_label()

    probas = bst.predict(dmatrix, ntree_limit=bst.best_iteration)
    # probas is the probability for label=1
    predict_label = np.where(probas > prob_cutoff, 1, 0)

    print "================= {} =================".format(title)
    print "Accuracy: {}".format(accuracy_score(true_label,predict_label))
    print "Classification Report: "
    print classification_report(y_true=true_label,y_pred=predict_label)
    print "Confusion Matrix: "
    print confusion_matrix(y_true=true_label,y_pred=predict_label)

def train(param,dmatrix_train,dmatrix_validate):
    param['silent'] = 1
    param['objective'] = 'binary:logistic'  # output probabilities
    param['eval_metric'] = 'auc'

    num_rounds = param["num_rounds"]
    early_stopping_rounds = param["early_stop_rounds"]

    # early stop will check on the last dataset
    watchlist = [(dmatrix_train, 'train'), (dmatrix_validate, 'validate')]
    bst = xgb.train(param, dmatrix_train, num_rounds, watchlist, early_stopping_rounds=early_stopping_rounds)

    print "parameters: {}".format(param)
    print "best {}: {:.2f}".format (param["eval_metric"],bst.best_score)
    print "best_iteration: %d" % (bst.best_iteration)

    return bst

param = {}
param["num_rounds"] = 200
param["early_stop_rounds"] = 15

param['max_depth'] = 6
param['eta'] = 0.05
param["subsample"] = 0.75
param["colsample_bytree"] = 0.75

dmatrix_train,dmatrix_validate,dmatrix_test = make_dmatrix(4000)

bst = train(param,dmatrix_train,dmatrix_validate)

# check performance
prob_cutoff=0.5
predict("train",bst, dmatrix_train,prob_cutoff )
predict("validate",bst, dmatrix_validate,prob_cutoff)
predict("test",bst, dmatrix_test,prob_cutoff)




