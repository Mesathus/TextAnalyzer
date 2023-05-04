import builtins
import math
import string
import sys
from operator import itemgetter

import matplotlib.pyplot as plt
import re
import requests
from bs4 import BeautifulSoup


class TextAnalyzer(builtins.object):
    def __init__(self, src, src_type=None):  # constructor method
        self._src = src
        self._src_type = src_type
        if self._src_type is None:  # get src type if none is provided
            self.discover()
        if self._src_type == "text":  # convert src content to str depending on src_type
            self._content = src
            self._orig_content = src
        elif self._src_type == 'path':
            with(open(self._src, 'r')) as content:
                self._content = content.read()
                self._orig_content = content.read()
        elif self._src_type == 'url':
            r = requests.get(src, timeout=1)
            soup = BeautifulSoup(r.content, 'html.parser')
            self._content = str(soup.contents[2])  # this is a hack for that specific page, [2] might not work for all pages
            self._orig_content = self._content

    def discover(self):
        if self._src.startswith('http'):
            self._src_type = 'url'
        elif self._src.endswith('.txt'):
            self._src_type = 'path'
        else:
            self._src_type = 'text'

    def set_content_to_tag(self, tag, tag_id=None):  # getting contents of specific tags
        if self._src_type == 'url':
            r = requests.get(self._src, timeout=1)
            soup = BeautifulSoup(r.content, 'html.parser')
            self._content = soup.find(tag, id=tag_id).text

    def reset_content(self):
        print(self._content[0])
        self._content = self._orig_content
        print(self._content[0])

    def _words(self, casesensitive=False) -> []:  # list returning method
        words = self._content.splitlines()  # remove newline characters
        words = str(words).split()  # convert to a string and split on spaces
        words = [word.strip(string.punctuation).strip() for word in words]  # remove punctuation and empty spaces
        words = [word for word in words if len(word) > 0]  # remove '' entries from the list
        if not casesensitive:
            words = [word.upper() for word in words]  # convert to upper case if casesensitive=False
        return words

    def common_words(self, minlen=1, maxlen=100, count=10, casesensitive=False) -> []:  # list returning
        words = self._words(casesensitive)
        words = list(filter(lambda key: maxlen >= len(key) >= minlen, words))  # lambda to filter the list by word length
        if not casesensitive:
            words = [word.strip().upper() for word in words]
        wordSet = set(words)  # convert to a set to remove duplicate entries
        commonWordList = []
        for x in wordSet:
            commonWordList.append((x, words.count(x)))  # create tuples and append to list
        commonWordList.sort(key=itemgetter(1), reverse=True)  # sort by the tuple counts
        if count > len(commonWordList):  # adjust count if it's bigger than array length
            count = len(commonWordList)
        return commonWordList[:count]  # return a list length count

    def char_distribution(self, casesensitive=False, letters_only=False) -> []:
        words = self._words(casesensitive)
        if not casesensitive:
            words = [word.upper() for word in words]
            letterSet = set(string.ascii_letters.upper()) if letters_only else set(string.printable.upper())
        else:
            letterSet = set(string.ascii_letters) if letters_only else set(string.printable)  # determine types of characters to check distribution on
        words = str(words)
        words = words.replace("['", '').replace("', '", ' ').replace('"', '').replace("']", '')  # removing list artifacts from the string
        charList = [(re.escape(letter), len(re.findall(re.escape(letter), str(words)))) for letter in letterSet]  # ensure escape characters don't throw exceptions
        charList.sort(key=itemgetter(1), reverse=True)  # sort by the tuple counts
        return charList

    def plot_common_words(self, minlen=1, maxlen=100, count=10, casesensitive=False):
        words = self.common_words(minlen=minlen, maxlen=maxlen, count=count, casesensitive=casesensitive)
        word = [tup[0] for tup in words]  # break tuples into two lists, one for words and one for counts
        vals = [tup[1] for tup in words]
        plt.rcdefaults()
        fig, ax = plt.subplots()
        y_pos = vals  # x,y interim variables for readability
        x_pos = word
        ax.bar(x_pos, y_pos)  # this could be (word, vals) but would be less readable
        ax.set_ylabel("Word count")  # default labels to get number ticks based on min/max values
        ax.set_xticks(x_pos, labels=word)  # assign words to x-axis ticks
        plt.show()

    def plot_char_distribution(self, casesensitive=False, letters_only=False):
        words = self.char_distribution(casesensitive=casesensitive, letters_only=letters_only)
        char = [tup[0] for tup in words]  # same idea as plot_common_words method
        vals = [tup[1] for tup in words]
        plt.rcdefaults()
        fig, ax = plt.subplots()
        y_pos = vals
        x_pos = char
        ax.bar(x_pos, y_pos)
        ax.set_ylabel("Character count")
        ax.set_xticks(x_pos, labels=char)
        plt.show()

    @property
    def avg_word_length(self) -> float:  # float returning
        words = math.fsum([len(i.strip()) for i in self._words()]) / len(self._words())  # total length of all words / count of words
        return round(words, 2)

    @property
    def word_count(self) -> int:  # int returning
        count = len([x for x in self._words() if len(x) > 0])  # count words while removing any '' entries
        return count

    @property
    def distinct_word_count(self) -> int:  # int returning
        count = len(set([x for x in self._words() if len(x) > 0]))  # as above but convert to a set to remove duplicate values
        return count

    @property
    def positivity(self) -> int: # in returning
        tally = 0
        words = self.words
        with(open("positive.txt", "rt", encoding="utf-8")) as file:  # with is like C# using, handles closing the file for us
            data = file.readlines()
            data = [x.strip() for x in data]  # remove empty spaces and newline characters
            tally += math.fsum([1 for i in data if i in words])  # create a sum, adding 1 for every i that is in both words and data
        with(open("negative.txt", "rt", encoding="utf-8")) as file:
            data = file.readlines()
            data = [x.strip() for x in data]
            tally -= math.fsum([1 for i in data if i in words])
        tally = round(tally / self.word_count * 1000)
        return tally

    @property
    def words(self) -> []:  # list returning
        words = [w.upper() for w in self._words()]  # create an all uppercase list to return
        return words

#################################################################################
#   The code below is intended for testing in an IDE                            #
#   Only the code above is necessary for Jupyter Notebooks                      #
#                                                                               #
#################################################################################

    def print(self):
        print(self._content)
        print(self._orig_content)
        print(self.common_words(minlen=3, maxlen=8, count=50, casesensitive=True))
        print(self.char_distribution(letters_only=False))
        self.plot_common_words()
        self.plot_char_distribution(casesensitive=True, letters_only=True)


def main():  # main defined as a method so any variables created here aren't available globally
    # ta = TextAnalyzer('https://static.webucator.com/media/public/documents/harrison.html')
    url = 'https://static.webucator.com/media/public/documents/clinton.html'
    path = 'pride-and-prejudice.txt'
    text = '''The outlook wasn't brilliant for the Mudville Nine that day;
    the score stood four to two, with but one inning more to play.
    And then when Cooney died at first, and Barrows did the same,
    a sickly silence fell upon the patrons of the game.'''

    ta = TextAnalyzer(path)
    common_words = ta.common_words(count=sys.maxsize)
    print(common_words[len(common_words) - 1])
    # print(ta.avg_word_length)
    # print(ta.word_count)
    # print(ta.distinct_word_count)
    # print(ta.char_distribution())
    # print(ta.positivity)


if __name__ == "__main__":  # entrypoint of the program
    main()
