
import re

ReplacePatterns = [
                    (r'won\'t', 'will not'),
                    (r'can\'t', 'cannot'),
                    (r'i\'m', 'i am'),
                    (r'ain\'t', 'is not'),
                    (r'(\w+)\'ll', '\g<1> will'),
                    (r'(\w+)n\'t', '\g<1> not'),
                    (r'(\w+)\'ve', '\g<1> have'),
                    (r'(\w+)\'s', '\g<1> is'),
                    (r'(\w+)\'re', '\g<1> are'),
                    (r'(\w+)\'d', '\g<1> would'),
                    (r'1st','first'),
                    (r'2nd','second'),
                    (r'3rd','third')
                    ]
class TextCleaner(object):
    """
    1. expand contraction and abbrevations
    2. remove all non-letters, only keep letters
    3. normalize to all lower case
    """

    def __init__(self,replace_patterns = ReplacePatterns):
        self.replace_patterns = [(re.compile(regex,re.IGNORECASE),replacewith)  for regex,replacewith in replace_patterns]

    def clean(self, text):
        s = text

        ############### expand contraction and abbrevations
        for (pattern, replacewith) in self.replace_patterns:
            s = re.sub(pattern, replacewith, s)

        ############### only keep letters
        s = re.sub("[^a-zA-Z]", " ", s)

        return s.lower()# normalize to lower case
