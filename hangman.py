#!/usr/bin/python

import sys
from argparse import ArgumentParser
from game import Strategy
from game import HangmanGame
from game import Timer


def run(game, strategy):
    while game.game_status() == HangmanGame.ONGOING:
        guess = strategy.next_guess(game)
        guess.make_guess(game)

    # return game.game_status()


def main(argv=None):

    if argv is None:
        argv = sys.argv
    try:
        parser = ArgumentParser()
        parser.add_argument("dictionary", help="dictionary file")
        parser.add_argument("words", nargs="+", help="list of words / file of words (ends with txt)")
        args = parser.parse_args()
        # print args

        if args.words[0].endswith('.txt'):
            with open(args.words[0], 'r') as gameWords:
                words = [word.strip().upper() for word in gameWords if word.strip() != ""]
        else:
            words = args.words

        total = 0
        print "Game starting..."
        with Timer() as totalTime:
            strategy = Strategy(args.dictionary)
            for word in words:
                word = word.lower()
                game = HangmanGame(word)

                # run the game, using strategy
                run(game, strategy)

                # total corrected guesses update
                total += game.game_status()

                for e1 in game.target:
                    print e1,
                print " -- missed:",
                for e2 in game.get_unmatched_letters():
                    print e2,
                print "\n#######################################"

        avg = total / float(len(words)) * 100

        print "Number of words tested:            " + str(len(words))
        print "Number of words guessed correctly: " + str(total)
        print "Corrected Guesses (%):             " + str(avg) + "%"
        print "Time to run:                       %09f sec" % totalTime.interval

        return 0

    except Exception as err:
        print >> sys.stderr, str(err)
        return 1


if __name__ == "__main__":
    sys.exit(main())
