#!/usr/bin/env python3
import sys; sys.path.append("..")
from fireplace import cards
from fireplace.exceptions import GameOver
from fireplace.utils import play_full_game
from fireplace.ai import Player

##
# If you get an error about not being able to import cards
# then make sure you run './setup install' using python3.
#
# Any time you make a change to anything that isn't this file
# run './setup install' in python3 to compile those changes.
# If you don't the changes will not be reflected during you next
# run.
#
# This will also throw an charmap error in windows because
# windows is a terrible operating system.
##

def test_full_game():
	player = Player()
	player.train()
	#try:
    # This will start the game
		#play_full_game()
	#except GameOver:
    # This will always run whenever the game ends.
		#print("Game completed normally.")


# Don't need to worry about this
def main():
	cards.db.initialize()
	if len(sys.argv) > 1:
		numgames = sys.argv[1]
		if not numgames.isdigit():
			sys.stderr.write("Usage: %s [NUMGAMES]\n" % (sys.argv[0]))
			exit(1)
		for i in range(int(numgames)):
			test_full_game()
	else:
		test_full_game()


if __name__ == "__main__":
	main()
