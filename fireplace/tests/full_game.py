#!/usr/bin/env python3
import sys; sys.path.append("..")
import os.path
import logging
import threading
import time
import json
from fireplace.logging import get_logger 
from fireplace import cards
from fireplace.exceptions import GameOver
from fireplace.utils import play_full_game
from fireplace.ai import Player
from hearthstone.enums import CardClass
from pymongo import MongoClient
from ast import literal_eval
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
	numThreads = int(input("How many threads: "))
	numGames = int(input("How many games per thread: "))

	verbosity = input("Silent(s) or Verbose(v): ")
	if verbosity == 's':
		log = get_logger("fireplace", logging.WARNING) 

	client = MongoClient()
	db = client.test

	cards1 = db.decks.find({"DeckName" : "Hand Lock"}, {"Cards" : 1, "_id" : 0})
	for neat in cards1:
		carderino2 = neat["Cards"]
	
	deck1 = []
	for hello in carderino2:
		deck1.append(cards.filter(name=hello)[0])

	cards2 = db.decks.find({"DeckName":"Midrange Beast Gadgetzan"},{"Cards":1,"_id":0})
	for something in cards2:
		deckList = something["Cards"]

	deck2 = []
	for card in deckList:
		deck2.append(cards.filter(name=card)[0])

	StateQualities = {}
	if os.path.isfile('StateQualities.json'):
		with open('StateQualities.json', 'r') as infile:
			tmp = json.load(infile)
		for key, value in tmp.items():
			StateQualities[literal_eval(key)] = value

	Visited = {}
	if os.path.isfile('Visited.json'):
		with open('Visited.json', 'r') as infile:
			tmp = json.load(infile)
		for key, value in tmp.items():
			Visited[literal_eval(key)] = value

	print("Starting all threads...")
	start_time = time.time()
	threads = []
	if numThreads == 1:
		Player(StateQualities.copy(),Visited.copy(),numGames,0,deck1,deck2)
	else:
		for i in range(0, numThreads):
			thread = threading.Thread(target=Player, args = (StateQualities.copy(),Visited.copy(),numGames,i,deck1,deck2))
			time.sleep(0.1)
			thread.start()
			threads.append(thread)

	print("Started all threads successfully!")

# Wait for threads to finish
	if numThreads != 1:
		for thread in threads:
			thread.join()

	finish_time = time.time()

	print("Finish time: ", finish_time - start_time)
# Start to merge files
	print("Merging Files... This may take a while!")
	ThreadQualities = []
	ThreadVisited = []
	for i in range(0,numThreads):
		with open('Output/StateQualities'+str(i)+'.json', 'r') as infile:
			tmp = json.load(infile)
			ThreadQualities.append({})
			for key, value in tmp.items():
				ThreadQualities[-1][literal_eval(key)] = value

		with open('Output/Visited'+str(i)+'.json', 'r') as infile:
			tmp = json.load(infile)
			ThreadVisited.append({})
			for key, value in tmp.items():
				ThreadVisited[-1][literal_eval(key)] = value

## Average together all the values output from threads
	StateQualities = {}
	Visited = {}

	for _ in range(0, numThreads):
		q = []
		v = []
		loopQualities = ThreadQualities.pop(0)
		loopVisited = ThreadVisited.pop(0)
		for key, value in loopQualities.items():
			if value == 0:
				continue
			for i in range(0, len(ThreadQualities)):
				if key in ThreadQualities[i].keys():
					x = ThreadQualities[i].pop(key)
					if x != 0:
						q.append(x)
						v.append(ThreadVisited[i][key[0]])
			totalV= sum(v) + loopVisited[key[0]]
			avgQ = value * (loopVisited[key[0]] / totalV)
			for i in range(0, len(q)):
				avgQ += q[i] * (v[i] / totalV)
			StateQualities[key] = avgQ
			if key[0] in Visited.keys():
				Visited[key[0]] += totalV
			else:
				Visited[key[0]] = totalV
			
	with open('StateQualities.json', 'w') as outfile:
		tmp = {}
		for key, value in StateQualities.items():
			tmp[str(key)] = value
		json.dump(tmp, outfile)
	with open('Visited.json', 'w') as outfile:
		tmp = {}
		for key, value in Visited.items():
			tmp[str(key)] = value
		json.dump(tmp, outfile)

	print("Done!")
			

# Don't need to worry about this
def main():
	cards.db.initialize()
	"""if len(sys.argv) > 1:
		numgames = sys.argv[1]
		if not numgames.isdigit():
			sys.stderr.write("Usage: %s [NUMGAMES]\n" % (sys.argv[0]))
			exit(1)
		for i in range(int(numgames)):
			test_full_game()
	else:"""
	test_full_game()


if __name__ == "__main__":
	main()
