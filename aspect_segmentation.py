
import heapq
from collections import Counter
import nltk
from nltk.corpus import stopwords
from sentence import Sentence
# from tqdm import tqdm
# import ipdb

class AspectSentence(Sentence):
    def __init__(self,raw_sentence,stopwords):
        super(AspectSentence,self).__init__(raw_sentence,stopwords)

        # overwrite the type, from list to dictionary
        self.words = Counter(self.words)

        # it is possible that one sentence can have two sub-sentences, and each sub-sentence has its own aspect
        # although it possible, but I think's it is rather rare
        # also, even we want to consider such rare case, store multiple possible aspects won't help much in later calculation
        self.aspect = None

    def match(self,aspects_keywords):
        """
        aspects_keywords must be a dictionary
        key: a string representing the aspect
        value: a set which contains the key words for that aspect
        """
        aspects_matched = Counter()

        for w,c in self.words.iteritems():
            for aspect,keywords in aspects_keywords.iteritems():
                if w in keywords:
                    aspects_matched[aspect] += c

        if len(aspects_matched) == 0: # no match
            self.aspect = None
        else:
            top_aspect,top_match = aspects_matched.most_common(1)[0]
            assert top_match > 0
            self.aspect = top_aspect

class AspectSegmentation(object):

    # only load once, faster than call 'sent_tokenize' each time
    SentTokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    def __init__(self,reviews,seed_aspect_keywords,extra_stop_words = None):
        """
        seed_aspect_keywords: dictionary
        key: aspect, string
        value: a set which holds the initial seed keywords
        """
        stop_words = set(stopwords.words("english"))
        if extra_stop_words is not None:
            stop_words |= set(extra_stop_words)

        self._sentences = []
        self._vocabulary = set()
        self._aspect_keywords = seed_aspect_keywords

        # the total number of specific word in all reviews
        self.word_total_occurs = Counter()

        # number of sentences which NOT contain word 'w'
        self.word_exclude_sents = Counter()

        iter_sentences = (sent for review in reviews for sent in AspectSegmentation.SentTokenizer.tokenize(review))
        for index, sent in enumerate(iter_sentences):
            aspect_sent = AspectSentence(sent,stop_words)
            self._sentences.append(aspect_sent)
            self.word_total_occurs += aspect_sent.words

            self._vocabulary.update(aspect_sent.words.elements())
            for w in aspect_sent.words.iterkeys():
                ##### this is a temporary step, now actually we are using 'word_exclude_sents' as 'word_include_sents'
                ##### count the number of sentence which include word 'w'
                self.word_exclude_sents[w] +=1

            print "{}-th sentence finish preprocessing".format(index+1)

        n_sentences = len(self._sentences)
        for w in self._vocabulary:
            self.word_exclude_sents[w] = n_sentences  - self.word_exclude_sents[w]

        # ipdb.set_trace()

    def __count(self):
        # C1 has key <word,aspect>
        # represents number of times of 'word' appear in 'aspect'
        C1 = Counter()

        # C3 has key <word,aspect>
        # represents number of sentences of 'aspect' which NOT contain 'word'
        C3 = Counter()

        # how many sentences in each aspect
        n_sents_each_aspects = Counter()

        for sent in self._sentences:
            if sent.aspect is not None:
                n_sents_each_aspects[sent.aspect] += 1

                for w,c in sent.words.iteritems():
                    C1[(w,sent.aspect)] += c

                    ##### this is just temporary step, where I use C3 as its opposite meaning
                    ##### number of sentence of 'aspect' which CONTAIN word 'w'
                    C3[(w,sent.aspect)] += 1

        for (w,aspect),n_include_sents in C3.iteritems():
            # n_sents_each_aspects[aspect]: how many sentenes in 'aspect'
            # n_include_sents: how many sentences in 'aspect' include word 'w'
            n_exclude_sents = n_sents_each_aspects[aspect] - n_include_sents
            assert n_exclude_sents >=0
            C3[(w,aspect)] =  n_exclude_sents

        return C1,C3

    def __chi_square(self,w,aspect,C1,C3,debugprint=False):
        # c: word's total number of occurance
        c = self.word_total_occurs[w]

        # c1: number of times of 'word' appear in 'aspect'
        c1 = C1[(w,aspect)]

        # c2: number of times of 'word' NOT in 'aspect'
        c2 = c - c1
        assert c2 >=0

        # c3: number of sentences of 'aspect' NOT contain word 'w'
        c3 = C3[(w,aspect)]

        # c4: number of sentences NOT of 'aspect' NOT contain word 'w'
        c4 = self.word_exclude_sents[w] - c3
        assert c4 >=0

        #
        temp = c1 * c4 - c2*c3
        nominator = c * temp * temp
        denominator =  (c1+c3)*(c2+c4)*(c1+c2)*(c3+c4)

        # since all c* are >=0, so if denominator==0
        # normally (without prove), nominator is also 0
        # so we can return 0 directly without doing the division
        chisquare = 0 if nominator == 0 else float(nominator)/denominator

        if debugprint:
            print "----------------- word<{}>, aspect<{}>".format(w,aspect)
            print "\t<%s> occur c=%d times"%(w,c)
            print "\tword<%s> appear in aspect<%s>: c1=%d times"%(w,aspect,c1)
            print "\tword<%s> appear out of aspect<%s>: c2=%d times"%(w,aspect,c2)
            print "\t#sentence in aspect<%s> NOT contain word<%s>: c3=%d"%(aspect,w,c3)
            print "\t#sentence NOT in aspect<%s> NOT contain word<%s>: c4=%d"%(aspect,w,c4)
            print "\t<{},{}> has chi-square: {}".format(w,aspect,chisquare)

        return chisquare

    def run_once(self,top_k=5,watchlist=None):
        # *********************************** MATCH
        for sent in self._sentences:
            sent.match(self._aspect_keywords)
        print "all sentences re-matched, begin counting"

        ################# for debug
        # for index,sent in enumerate(self._sentences):
        #     print "{}th <{}> {}".format(index+1,sent.aspect,sent.raw_sentence)
        ################# end debug

        # *********************************** COUNT
        C1,C3 = self.__count()
        print "finish counting"

        # *********************************** CHI-SQUARE
        keywords_updated = False
        for aspect in self._aspect_keywords.iterkeys():
            current_keywords = self._aspect_keywords[aspect]
            top_new_keywords = []

            for w in self._vocabulary:
                debugprint = False if watchlist is None else (w,aspect) in watchlist
                chisquare = self.__chi_square(w,aspect,C1,C3,debugprint)

                heapq.heappush(top_new_keywords,(chisquare,w))
                if len(top_new_keywords) > top_k:
                    heapq.heappop(top_new_keywords)# pop out the smallest

            for score,new_keyword in top_new_keywords:
                if new_keyword not in current_keywords:
                    current_keywords.add(new_keyword)
                    print "new keyword '%s' added into aspect '%s'"%(new_keyword,aspect )
                    keywords_updated = True

        return keywords_updated

    def run(self,top_k=5,n_iters=10):
        for index in xrange(n_iters):
            print "start {}-th iteration, ......".format(index+1)

            keywords_updated = self.run_once(top_k)
            if not keywords_updated:
                print "keywords remain the same, pre-exist"
                break
