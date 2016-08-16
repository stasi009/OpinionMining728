
import nltk
import json

AspectBusiness = "BusinessService"
AspectClean = "Cleanliness"
AspectLocation = "Location"
AspectOverall = "Overall"
AspectRoom = "Rooms"
AspectService = "Service"
AspectValue = "Value"
AspectCheckin = "Check in"
AspectSleep = "Sleep Quality"
AsepctNothing = "Nothing"
AspectUnknown = "Unknown"

SentimentPositive = "Positive"
SentimentNegative = "Negative"
SentimentNeutral = "Neutral"
SentimentUnknown = "Unknown"

def pprint_json(infilename,outfilename):
    with open(infilename,"rt") as inf:
        d = json.load(inf)

    with open(outfilename,"wt") as outf:
        json.dump(d,outf,indent=4)

Coarse2FinePosTags = {
    'n': ("NN","NNS","NNP","NNPS"),
    'a': ("JJ","JJR","JJS"),
    'r': ("RB","RBR","RBS"),
    'v': ("VB","VBD","VBG","VBN","VBP","VBZ")
}
Fine2CoarsePosTags = { finetag: k for k,v in Coarse2FinePosTags.iteritems() for finetag in v }

def lemmatize_with_pos(lemmatizer,words):
    """
    to get better lemmatization result, we need to specify POS in lemmatize(w,pos) method
    however, the POS from nltk.pos_tag function is fine-grained POS,
    doesn't match what lemmatize want, which is coarse-grained POS
    so I define this function to transform fine-grained POS to coarse-grained POS
    and return 'n' for unspecified, which is the default of lemmatize() method
    """
    pos_tagged_words = nltk.pos_tag(words)
    return [lemmatizer.lemmatize(w,pos = Fine2CoarsePosTags.get(pos,'n')) for w,pos in pos_tagged_words]
