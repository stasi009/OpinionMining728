import numpy as np


class SentimentLexicon(object):
    def __init__(self, n_ratings):
        # finally, self.words is a dictionary
        # key: word
        # value: a tuple, tuple[0] is ER (expected rating), tuple[1] is word's distribution
        self.words = {}

        self.rating_totals = np.zeros(n_ratings)
        self.n_ratings = n_ratings

        # calculate once, no need to calculate more than once
        avg_rating = (1.0 + n_ratings) / 2.0
        self.centered_ratings = np.arange(1, 1 + n_ratings, dtype=np.float) - avg_rating

    def count(self, word, rating):
        if word in self.words:
            rating_dist = self.words[word]
        else:
            rating_dist = np.zeros(self.n_ratings)
            # default sentiment score is 0, means neutral
            self.words[word] = rating_dist

        # rating starts from 1, while pos starts from 0
        pos = int(rating) - 1
        rating_dist[pos] += 1
        self.rating_totals[pos] += 1

    def normalize(self):
        for w, rating_dist in self.words.iteritems():
            rating_dist /= self.rating_totals

            temp = rating_dist.sum()
            rating_dist /= temp

            expected_rating = np.sum(self.centered_ratings * rating_dist)
            self.words[w] = (expected_rating, rating_dist)

    def get_expected_rating(self, w):
        return self.words[w][0] if w in self.words else 0
