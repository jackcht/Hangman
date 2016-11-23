#!/usr/bin/python

import time
import collections
import re


# Game class
class HangmanGame:
    # 0 means LOSE; 1 means WIN
    WON = 1
    LOST = 0
    ONGOING = -1
    MAXGUESS = 6
    UNKNOWN = '_'

    def __init__(self, real):
        self.real = real.lower()
        self.target = list(self.UNKNOWN * len(self.real))   # list of underscores, updated when having corrected guesses
        self.matchedLetters = set()
        self.unmatchedLetters = set()

    ################
    # Getter functions
    def wrong_guesses(self):
        return len(self.unmatchedLetters)

    def get_current_guess(self):
        return "".join(self.target)

    def get_matched_letters(self):
        return set(self.matchedLetters)

    def get_unmatched_letters(self):
        return set(self.unmatchedLetters)

    def get_all_guessed(self):
        return self.matchedLetters | self.unmatchedLetters

    ########################
    # functions
    def game_status(self):
        if self.real == self.get_current_guess():
            return self.WON
        elif self.wrong_guesses() > self.MAXGUESS:
            return self.LOST
        else:
            return self.ONGOING

    def guess_letter(self, ch):
        if self.game_status() == self.ONGOING:
            ch = ch.lower()
            guess_correct = False
            for i in range(len(self.real)):
                if self.real[i] == ch:
                    self.target[i] = ch
                    guess_correct = True
            if guess_correct:
                self.matchedLetters.add(ch)
            else:
                self.unmatchedLetters.add(ch)

        return self.get_current_guess()


# a Timer class so as to get the current system time
class Timer:
    def __enter__(self):
        self.start = self.get_time()
        return self

    def __exit__(self, *args):
        self.end = self.get_time()
        self.interval = self.end - self.start

    def get_time(self):
        return time.clock()


# a simple guess as a wrapper of Guessing
class GuessLetter:
    def __init__(self, guess):
        self.guess = guess

    def make_guess(self, game):
        game.guess_letter(self.guess)


# Word Dictionary class
class WordDict:
    def __init__(self, words=None):
        if words is None:
            self.words = set()
            self.letterFreq = collections.Counter()
        else:
            self.words = words.copy()
            self.updated()

    def copy(self):
        """shallow copy"""
        copy_set = WordDict()
        copy_set.words = self.words.copy()
        copy_set.letterFreq = self.letterFreq.copy()
        return copy_set

    def updated(self):
        self.letterFreq = collections.Counter([letter for subset in map(set, self.words) for letter in subset])

    def __len__(self):
        return len(self.words)


# strategy class for finding next letter
class Strategy:

    def __init__(self, filename):
        self.wordCandidate = WordDict()
        self.wordCache = collections.defaultdict(WordDict)
        self.load_dict(filename)
        self.first_guess()

    def cache(self, game):
        self.wordCache[self.key(game)] = self.wordCandidate.copy()

    def key(self, game):
        return "".join(list(game.get_current_guess()) + ['!'] +
                       sorted(game.get_unmatched_letters()))

    def next_guess(self, game):
        for each in game.target:
            print each,
        print " -- missed:",
        for e2 in game.get_unmatched_letters():
            print e2,
        print "\n"

        self.update_candidates(game)
        return GuessLetter(self.letter_strategy(self.wordCandidate, game.get_all_guessed(), False))

    def letter_strategy(self, word_set, letter_set, first=True):
        for letter, _ in sorted(word_set.letterFreq.most_common(),
                                key=lambda lc: (lc[1], lc[0]), reverse=True):
            if letter not in letter_set:
                if not first:
                    print "guess: " + letter
                return letter

    def update_candidates(self, game):
        if self.key(game) in self.wordCache:
            self.wordCandidate = self.wordCache[self.key(game)].copy()
            return
        wrong_letters = game.get_unmatched_letters()
        if wrong_letters:
            not_wrong_letters = "[^" + "".join(wrong_letters) + "]{"
        else:
            not_wrong_letters = "[a-z]{"

        current = re.compile("(" + HangmanGame.UNKNOWN +
                             "+|[a-z]+)").findall(game.get_current_guess())
        for i in range(len(current)):
            if current[i][0] == HangmanGame.UNKNOWN:
                current[i] = not_wrong_letters + str(len(current[i])) + "}"

        current.append("$")
        guess_regex = re.compile("".join(current))

        temp = self.wordCandidate.words.copy()

        for word in temp:
            if guess_regex.match(word) is None:
                self.wordCandidate.words.remove(word)

        self.wordCandidate.updated()

        self.cache(game)

    def load_dict(self, filename):
        with open(filename, 'r') as dictionary:
            for line in dictionary:
                word = line.strip()
                if word != "":
                    # cache the specific word candidates for the word length
                    key = HangmanGame.UNKNOWN * len(word) + "!"
                    self.wordCache[key].words.add(word.lower())
        for k in self.wordCache:
            self.wordCache[k].updated()

    def first_guess(self):
        emptyset = set()
        temp = self.wordCache.copy()
        for k in temp:
            if len(self.wordCache[k]) > 10:
                # determine first guess letter
                letter = self.letter_strategy(self.wordCache[k], emptyset, True)

                cache_no_letter = self.wordCache[k].copy()
                for word in self.wordCache[k].words:
                    if letter in word:
                        cache_no_letter.words.remove(word)
                cache_no_letter.updated()

                # save to cache with new key (first miss, since first guess needs very long)
                key = HangmanGame.UNKNOWN * len(word) + '!' + letter
                self.wordCache[key] = cache_no_letter
