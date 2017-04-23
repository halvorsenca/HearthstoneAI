from fireplace.exceptions import GameOver
from .logging import log 
from fireplace.utils import setup_game, play_turn
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
		for _ in range(0, numGames):
			try:
				game = setup_game(deck1, deck2)

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
					#if self.Visited[currState] > 100000:
						#self.play_optimal(game, currState)
					#else:
					if game.players[0].current_player:
						currState = self.extract_gamestate(game)
						if not currState in self.Visited.keys():
							self.Visited[currState] = 0
						self.Visited[currState] += 1
						self.play_random(game, currState)
						self.calcQualities()
					elif game.players[1].current_player:
						play_turn(game)
			except GameOver:
				self.calcQualities()
				currState = self.extract_gamestate(game)
				self.turnSeq.append((currState, -1))
				self.calcQualities()
				log.info("Game Completed")

	def play_random(self, game, currState):
		did_action = False
		action = None

		while not did_action:
			action = random.choice(self.Moves)
			did_action = action(game)

		self.turnSeq.append((currState, action.__name__))

		#if self.Visited[self.turnSeq[-1][0]] == 1:
			#for move in self.Moves:
				#self.StateQualities[(self.turnSeq[-1][0],move.__name__)] = 0

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
					reward = 100
				else:
					reward = -100
			else:
				reward = self.turnSeq[-1][0][3]
				directions = []
				for move in self.Moves:
					if not (self.turnSeq[-1][0], move.__name__) in self.StateQualities.keys():
						self.StateQualities[(self.turnSeq[-1][0], move.__name__)] = 0
					directions.append(self.StateQualities[(self.turnSeq[-1][0],move.__name__)])
				bestaction = self.StateQualities[(self.turnSeq[-1][0],self.Moves[directions.index(max(directions))].__name__)] # Need to figure out better way to query Moves
			if not self.turnSeq[-2] in self.StateQualities.keys():
				self.StateQualities[self.turnSeq[-2]] = 0
			self.StateQualities[self.turnSeq[-2]] += (reward + (0.9*bestaction) - self.StateQualities[self.turnSeq[-2]]) / self.Visited[self.turnSeq[-2][0]]

	"""
	Will have to update this to reflect updates before making optimal plays
	but don't really need it until after the game has been trained
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
	"""
