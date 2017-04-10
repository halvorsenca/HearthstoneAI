from fireplace.exceptions import GameOver
from .logging import log 
from fireplace.utils import setup_game, play_turn
from collections import defaultdict
import os.path
import random
import pickle

class Player():
	def __init__(self):
		if os.path.isfile('../StateQualities.pkl'):
			with open('StateQualities.pkl', 'rb') as f:
				self.StateQualities = pickle.load(f)
		else:
			self.StateQualities = {}
		if os.path.isfile('../Visited.pkl'):
			with open('Visited.pkl', 'rb') as f:
				self.Visited = pickle.load(f)
		else:
			# This initializes every new entry with a zero
			self.Visited = defaultdict(self.zero)
		self.Moves = [play_offensive, play_defensive, play_utility, trade_spell,
						trade_minions, wipe_field, attack_hero, use_hero_power]
		self.turnSeq = []

# Need this functions so that Visited can be pickled...
	def zero(self):
		return 0

	def train(self):
		for _ in range(0, int(input("How many games: "))):
			try:
				game = setup_game()

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
					currState = self.extract_gamestate(game)
					self.Visited[currState] += 1
					#if self.Visited[currState] > 100000:
						#print("This shouldn't run")
						#self.play_optimal(game, currState)
					#else:
					play_turn(game)
					#self.play_random(game, currState)
					#self.calcQualities()
			except GameOver:
				#self.calcQualities()
				self.turnSeq.append((currState, -1))
				#self.calcQualities()
				log.info("Game Completed")

# TODO: Need to switch to using JSON because pkl could loss information
		with open('StateQualities.pkl', 'wb') as f:
			pickle.dump(self.StateQualities, f, pickle.HIGHEST_PROTOCOL)
		with open('Visited.pkl', 'wb') as f:
			pickle.dump(self.Visited, f, pickle.HIGHEST_PROTOCOL)

	def play_optimal(self, game, currState):
		directions = [
			self.StateQualities[(currState,self.Moves[0])],
			self.StateQualities[(currState,self.Moves[1])],
			self.StateQualities[(currState,self.Moves[2])],
			self.StateQualities[(currState,self.Moves[3])]
		]
		action = self.Moves[directions.index(max(directions))]
		self.turnSeq.append((game.currState, action))
		game.tryMove(action)

	def play_random(self, game, currState):
		did_action = False
		action = ''

		while not did_action:
			action = random.choice(self.Moves)
			did_action = action(game)

		self.turnSeq.append((currState, action))

		if self.Visited[self.turnSeq[-1][0]] == 1:
			for move in self.Moves:
				self.StateQualities[(self.turnSeq[-1][0],move)] = 0

	def extract_gamestate(self, game):
		myHealth = game.players[0].hero.health + game.players[0].hero.armor
		enemyHealth = game.players[1].hero.health + game.players[1].hero.armor

		cardAdvantage = (len(game.players[0].hand) + len(game.players[0].field))
											- (len(game.players[1].hand) + len(game.players[1].field))

# TODO: Need to figure out None issue
		totalDamage = self.get_field_damage(game.players[0])

		strongestEnemy = self.get_strongest_enemy(game.players[1])

# TODO: This probably isn't going to work
		jaraxxus = game.players[0].hero.id == 'EX1_323h'

		return (myHealth, enemyHealth, cardAdvantage, totalDamage, strongestEnemy, jaraxxus)
	
	def get_strongest_enemy(game):
		strongest = None
		for minion in game.players[1].field:
			if minion.health > strongest.health:
				strongest = minion
			elif minion.health == strongest.health and minion.atk > strongest.atk:
				strongest = minion
		return strongest.health
	
# TODO: None error
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
# If I have more health then I won
				if self.turnSeq[-1][0][0] > 0:
					reward = 100
				else:
					reward = -100
			else:
				reward = 0
				directions = []
				for move in self.Moves:
					directions.append(self.StateQualities[(self.turnSeq[-1][0],move)])
				bestaction = self.StateQualities[(self.turnSeq[-1][0],self.Moves[directions.index(max(directions))])]
			self.StateQualities[self.turnSeq[-2]] += (reward + (0.9*bestaction)
				-self.StateQualities[self.turnSeq[-2]]) / self.Visited[self.turnSeq[-2][0]]

