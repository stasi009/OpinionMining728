
import heapq
import logging
from collections import Counter
import nltk
from tqdm import tqdm
from aspect_sentence import AspectSentence

class AspectSegmentation(object):

    # only load once, faster than call 'sent_tokenize' each time
    SentTokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    def __init__(self,reviews,seed_aspect_keywords):
        """
        seed_aspect_keywords: dictionary
        key: aspect, string
        value: a set which holds the initial seed keywords
        """

        self._sentences = []
        self._vocabulary = set()
        self._aspect_keywords = seed_aspect_keywords

        # the total number of specific word in all reviews
        self.word_total_occurs = Counter()

        # number of sentences which NOT contain word 'w'
        self.word_exclude_sents = Counter()

        for review in tqdm(reviews):
            sentences = AspectSegmentation.SentTokenizer.tokenize(review)

            for sent in tqdm(sentences):
                aspect_sent = AspectSentence(sent)

                self._sentences.append(aspect_sent)
                self.word_total_occurs += aspect_sent.words

                self._vocabulary.update(aspect_sent.words.elements())
                for w in aspect_sent.words.iterkeys():
                    ##### this is a temporary step, now actually we are using 'word_exclude_sents' as 'word_include_sents'
                    ##### count the number of sentence which include word 'w'
                    self.word_exclude_sents[w] +=1

        n_sentences = len(self._sentences)
        for w in self._vocabulary:
            self.word_exclude_sents[w] = n_sentences  - self.word_exclude_sents[w]

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

    def __chi_square(self,w,aspect,C1,C3):
        # c: word's total number of occurance
        c = self.word_total_occurs[w]
        logging.debug("<%s> occur c=%d times",w,c)

        # c1: number of times of 'word' appear in 'aspect'
        c1 = C1[(w,aspect)]
        logging.debug("word<%s> appear in aspect<%s>: c1=%d times",w,aspect,c1)

        # c2: number of times of 'word' NOT in 'aspect'
        c2 = c - c1
        assert c2 >=0
        logging.debug("word<%s> appear out of aspect<%s>: c2=%d times",w,aspect,c2)

        # c3: number of sentences of 'aspect' NOT contain word 'w'
        c3 = C3[(w,aspect)]
        logging.debug("#sentence in aspect<%s> NOT contain word<%s>: c3=%d",aspect,w,c3)

        # c4: number of sentences NOT of 'aspect' NOT contain word 'w'
        c4 = self.word_exclude_sents[w] - c3
        assert c4 >=0
        logging.debug("#sentence NOT in aspect<%s> NOT contain word<%s>: c4=%d",aspect,w,c4)

        #
        temp = c1 * c4 - c2*c3
        nominator = c * temp * temp
        denominator =  (c1+c3)*(c2+c4)*(c1+c2)*(c3+c4)

        # we think denominator==0 as abnormal, which often occurs on some strange words
        # so just return -1, which will be filtered out in future stepes
        return -1 if denominator == 0 else float(nominator)/denominator

    def run_once(self,top_k=5):
        # *********************************** MATCH
        for sent in tqdm(self._sentences):
            sent.match(self._aspect_keywords)
        logging.info("all sentences re-matched, begin counting")

        # *********************************** COUNT
        C1,C3 = self.__count()
        logging.info("finish counting")

        # *********************************** CHI-SQUARE
        keywords_updated = False
        for aspect in self._aspect_keywords.iterkeys():
            current_keywords = self._aspect_keywords[aspect]
            top_new_keywords = []

            for w in self._vocabulary:
                chisquare = self.__chi_square(w,aspect,C1,C3)

                heapq.heappush(top_new_keywords,(chisquare,w))
                if len(top_new_keywords) > top_k:
                    heapq.heappop(top_new_keywords)# pop out the smallest

            for score,new_keyword in top_new_keywords:
                if new_keyword not in current_keywords:
                    current_keywords.add(new_keyword)
                    logging.info("new keyword '%s' added into aspect '%s'",new_keyword,aspect )
                    keywords_updated = True

        return keywords_updated

    def run(self,top_k=5,n_iters=10):
        for index in xrange(n_iters):
            keywords_updated = self.run_once(top_k)
            if not keywords_updated:
                break
