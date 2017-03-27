from fireplace.exceptions import GameOver
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
# TODO: Add end state somehow!
			self.StateQualities = {}
		if os.path.isfile('../Visited.pkl'):
			with open('Visited.pkl', 'rb') as f:
				self.Visited = pickle.load(f)
		else:
			self.Visited = defaultdict(self.zero)
		self.Moves = ['Play_Biggest', 'Play_Multiple', 'Trade_Minions', 'Attack_Hero']
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
					print("Can mulligan %r" % (player.choice.cards))
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
				print("Game Completed")

		with open('StateQualities.pkl', 'wb') as f:
			pickle.dump(self.StateQualities, f, pickle.HIGHEST_PROTOCOL)
		with open('Visited.pkl', 'wb') as f:
			pickle.dump(self.Visited, f, pickle.HIGHEST_PROTOCOL)

# TODO: Will need to update this to work with Hearthstone Actions
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
		action = random.choice(self.Moves)
		self.turnSeq.append((currState, action))
		if self.Visited[self.turnSeq[-1][0]] == 1:
# TODO: Need to update with Hearthstone Actions
			self.StateQualities[(self.turnSeq[-1][0],self.Moves[0])] = 0
			self.StateQualities[(self.turnSeq[-1][0],self.Moves[1])] = 0
			self.StateQualities[(self.turnSeq[-1][0],self.Moves[2])] = 0
			self.StateQualities[(self.turnSeq[-1][0],self.Moves[3])] = 0
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
				directions = [
					self.StateQualities[(self.turnSeq[-1][0],self.Moves[0])],
					self.StateQualities[(self.turnSeq[-1][0],self.Moves[1])],
					self.StateQualities[(self.turnSeq[-1][0],self.Moves[2])],
					self.StateQualities[(self.turnSeq[-1][0],self.Moves[3])]
				]
				bestaction = self.StateQualities[(self.turnSeq[-1][0],self.Moves[directions.index(max(directions))])]
			self.StateQualities[self.turnSeq[-2]] += (reward + (0.9*bestaction)
				-self.StateQualities[self.turnSeq[-2]]) / self.Visited[self.turnSeq[-2][0]]

