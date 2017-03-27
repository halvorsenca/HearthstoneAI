from fireplace.exceptions import GameOver
from .logging import log 
from fireplace.utils import setup_game, play_turn
from collections import defaultdict
import os.path
import random
import pickle

class Player():
	def __init__(self):
		if os.path.isfile('StateQualities.pkl'):
			with open('StateQualities.pkl', 'rb') as f:
				self.StateQualities = pickle.load(f)
		else:
# TODO: Add end state somehow!
			self.StateQualities = {}
		if os.path.isfile('Visited.pkl'):
			with open('Visited.pkl', 'rb') as f:
				self.Visited = pickle.load(f)
		else:
			self.Visited = defaultdict(self.zero)
# TODO: Replace with list of actions for Hearthstone
		#self.Moves = {0:'N', 1:'E', 2:'S', 3:'W'}
		self.turnSeq = []

# Need this functions o that Visited can be pickled...
	def zero(self):
		return 0

	def train(self):
		for _ in range(0, int(input("How many games: "))):
			try:
				game = setup_game()

###
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
					if self.Visited[currState] > 100000:
						print("This shouldn't run")
						#self.play_optimal(game, currState)
					else:
						play_turn(game)
						#self.play_random(game, currState)
					#self.calcQualities()
			except GameOver:
				#self.calcQualities()
				self.turnSeq.append((currState, -1))
				#self.calcQualities()
				log.info("Game Completed")

		with open('StateQualities.pkl', 'wb') as f:
			pickle.dump(self.StateQualities, f, pickle.HIGHEST_PROTOCOL)
		with open('Visited.pkl', 'wb') as f:
			pickle.dump(self.Visited, f, pickle.HIGHEST_PROTOCOL)

# TODO: Will need to update this to work with Hearthstone Actions
	def play_optimal(self, game, currState):
		directions = [
			self.StateQualities[(currState,'N')],
			self.StateQualities[(currState,'E')],
			self.StateQualities[(currState,'S')],
			self.StateQualities[(currState,'W')]
		]
		action = self.Moves[directions.index(max(directions))]
		self.turnSeq.append((game.currState, action))
		game.tryMove(action)

	def play_random(self, game, currState):
# There is a better way to randomly pick something from a list
		action = self.Moves[random.randint(0, 3)]
		self.turnSeq.append((currState, action))
		if self.Visited[self.turnSeq[-1][0]] == 1:
# TODO: Need to update with Hearthstone Actions
			self.StateQualities[(self.turnSeq[-1][0],'N')] = 0
			self.StateQualities[(self.turnSeq[-1][0],'E')] = 0
			self.StateQualities[(self.turnSeq[-1][0],'S')] = 0
			self.StateQualities[(self.turnSeq[-1][0],'W')] = 0
		game.tryMove(action)

# This had None for FieldHealths and myDmg
	def extract_gamestate(self, game):
		health = game.players[0].hero.health + game.players[0].hero.armor - game.players[1].hero.health + game.players[1].hero.armor
		handCards = len(game.players[0].hand) - len(game.players[1].hand)
		numMinions = len(game.players[0].field) - len(game.players[1].field)
		myDmg = self.get_total_damage(game.players[0])
		enemyDmg = self.get_field_damage(game.players[1])
		enemyFieldHealth = self.getMinionHealth(game.players[1])
		myFieldHealth = self.getMinionHealth(game.players[0])
	# Going to ignore secrets for the time being
		return (health, handCards, numMinions, myDmg, enemyDmg, myFieldHealth, enemyFieldHealth)

	def getMinionHealth(self, player):
		ans = 0
		for minion in player.field:
			# TODO: Need to test this to make sure hero isn't included
			ans += minion.health

	def get_total_damage(self, player):
		dmg = self.get_field_damage(player)
		# Go through hand and calculate total damage
		# Will probably go through and define specific spells
	
	def get_field_damage(self, player):
		dmg = 0
		for minion in player.field:
			dmg += minion.atk
		return dmg

	def calcQualities(self):
		if len(self.turnSeq) == 1:
			return
		else:
			if self.turnSeq[-1][0] == 3:
				bestaction = 0
				reward = 100
			elif self.turnSeq[-1][0] == 7:
				bestaction = 0
				reward = -100
			else:
				reward = 0
# TODO: Need to update with Hearthstone Actions
				directions = [
					self.StateQualities[(self.turnSeq[-1][0],'N')],
					self.StateQualities[(self.turnSeq[-1][0],'E')],
					self.StateQualities[(self.turnSeq[-1][0],'S')],
					self.StateQualities[(self.turnSeq[-1][0],'W')]
				]
				bestaction = self.StateQualities[(self.turnSeq[-1][0],self.Moves[directions.index(max(directions))])]
			self.StateQualities[self.turnSeq[-2]] += (reward + (0.9*bestaction)
				-self.StateQualities[self.turnSeq[-2]]) / self.Visited[self.turnSeq[-2][0]]

