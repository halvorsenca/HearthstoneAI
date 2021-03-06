import sys
from fireplace.exceptions import GameOver
from .logging import log 
from fireplace.utils import setup_game, play_turn
from hearthstone.enums import PlayState
from collections import defaultdict
from fireplace.playerbot import play_offensive, play_defensive, play_utility, trade_spell, trade_minions, wipe_field, attack_hero, use_hero_power, end_turn
import os.path
import random
import json

class Player():
	def __init__(self, StateQualities, Visited, numGames, threadNum, deck1, deck2):
		self.StateQualities = StateQualities
		self.Visited = Visited

		self.Moves = [play_offensive, play_defensive, play_utility, trade_spell,
								trade_minions, wipe_field, attack_hero, use_hero_power, end_turn]
		self.turnSeq = []
		self.threadNum = threadNum

		self.train(numGames, deck1, deck2)

		print("Thread %d outputting file" % self.threadNum)
		with open('Output/StateQualities'+str(self.threadNum)+'.json', 'w') as outfile:
			tmp = {}
			for key, value in self.StateQualities.items():
				tmp[str(key)] = value
			json.dump(tmp, outfile)
		with open('Output/Visited'+str(self.threadNum)+'.json', 'w') as outfile:
			tmp = {}
			for key, value in self.Visited.items():
				tmp[str(key)] = value
			json.dump(tmp, outfile)

	def train(self, numGames, deck1, deck2):
		percent = 10
		gamesWon = 0
		for i in range(0, numGames):
			if (i/numGames)*100 >= percent:
				print("Thread %d: %d%%" % (self.threadNum, percent))
				percent += 10
			game = setup_game(deck1, deck2)
			try:
### This came from utils.py
				for player in game.players:
					log.info("Can mulligan %r" % (player.choice.cards))
					mull_count = random.randint(0, len(player.choice.cards))
					cards_to_mulligan = random.sample(player.choice.cards, mull_count)
					player.choice.choose(*cards_to_mulligan)
###

				self.turnSeq = []
# Play each turn
				while True:
					if game.players[0].current_player:
						currState = self.extract_gamestate(game)
						if not currState in self.Visited.keys():
							self.Visited[currState] = 0
						self.Visited[currState] += 1
						if self.Visited[currState] > 100:#sys.maxsize:
							self.play_optimal(game, currState)
						else:
							self.play_random(game, currState)
						self.calcQualities()
					elif game.players[1].current_player:
						play_turn(game)
			except GameOver:
				self.calcQualities()
				currState = self.extract_gamestate(game)
				self.turnSeq.append((currState, -1))
				self.calcQualities()
				if game.players[0].playstate == PlayState.WON:
					gamesWon += 1
				log.info("Game Completed")
		print("Thread", self.threadNum, "Win Rate:", (gamesWon / numGames)*100, "%")

	def play_random(self, game, currState):
		did_action = False
		action = None

		while not did_action:
			action = random.choice(self.Moves)
			did_action = action(game)

		log.info("Performed action %s in state %s" % (action.__name__, currState))

		self.turnSeq.append((currState, action.__name__))

	def play_optimal(self, game, currState):
		directions = []
		for move in self.Moves:
			if not (currState, move.__name__) in self.StateQualities.keys():
				self.StateQualities[(currState, move.__name__)] = 0
			directions.append((move, self.StateQualities[(currState, move.__name__)]))

		directions.sort(key=lambda x:x[1], reverse=True)

		for direction in directions:
			action = direction[0]
			did_action = action(game)
			if did_action:
				log.info("Performed action %s in state %s" % (action.__name__, currState))
				break

		self.turnSeq.append((currState, action.__name__))

	def extract_gamestate(self, game):
		myHealth = game.players[0].hero.health + game.players[0].hero.armor
		enemyHealth = game.players[1].hero.health + game.players[1].hero.armor

		cardAdvantage = (len(game.players[0].hand) + len(game.players[0].field)) - (len(game.players[1].hand) + len(game.players[1].field))

		totalDamage = self.get_field_damage(game.players[0])

		strongestEnemy = self.get_strongest_enemy(game)

		jaraxxus = game.players[0].hero.id == 'EX1_323h'

		mana = (game.players[0].max_mana - game.players[0].used_mana) + game.players[0].temp_mana

		return (myHealth, enemyHealth, mana, cardAdvantage, totalDamage, strongestEnemy, jaraxxus)
	
	def get_strongest_enemy(self, game):
		strongest = None
		for minion in game.players[1].field:
			if strongest == None or minion.health > strongest.health:
				strongest = minion
			elif minion.health == strongest.health and minion.atk > strongest.atk:
				strongest = minion
		return 0 if strongest == None else strongest.health
	
	def get_field_damage(self, player):
		dmg = 0
		for minion in player.field:
			dmg += minion.atk
		return dmg

	def calcQualities(self):
		if len(self.turnSeq) == 1:
			return
		else:
			if self.turnSeq[-1][1] == -1:
				bestaction = 0
				if self.turnSeq[-1][0][0] > 0:
					reward = 1000
				else:
					reward = -1000
			else:
				reward = 0
				directions = []
				for move in self.Moves:
					if not (self.turnSeq[-1][0], move.__name__) in self.StateQualities.keys():
						self.StateQualities[(self.turnSeq[-1][0], move.__name__)] = 0
					directions.append(self.StateQualities[(self.turnSeq[-1][0],move.__name__)])
				bestaction = self.StateQualities[(self.turnSeq[-1][0],self.Moves[directions.index(max(directions))].__name__)] # Need to figure out better way to query Moves
			if not self.turnSeq[-2] in self.StateQualities.keys():
				self.StateQualities[self.turnSeq[-2]] = 0
			self.StateQualities[self.turnSeq[-2]] += (reward + (0.9*bestaction) - self.StateQualities[self.turnSeq[-2]])# / self.Visited[self.turnSeq[-2][0]]

