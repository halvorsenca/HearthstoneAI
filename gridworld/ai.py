from game import Game
import os.path
import random
import pickle

class Player():
	def __init__(self):
		if os.path.isfile('StateQualities.pkl'):
			with open('StateQualities.pkl', 'rb') as f:
				self.StateQualities = pickle.load(f)
		else:
			self.StateQualities = {(3,-1): 100, (7,-1):-100}
		if os.path.isfile('Visited.pkl'):
			with open('Visited.pkl', 'rb') as f:
				self.Visited = pickle.load(f)
		else:
			self.Visited = [0] * 12
		self.Moves = {0:'N', 1:'E', 2:'S', 3:'W'}
		self.turnSeq = []

	def print_qualities(self):
		for x in range(0, 12):
			if x in [3,5,7]:
				continue
			print('State', x, '- Visits:', self.Visited[x])
			print('N', self.StateQualities[(x,'N')])
			print('E', self.StateQualities[(x,'E')])
			print('S', self.StateQualities[(x,'S')])
			print('W', self.StateQualities[(x,'W')])

	def train(self):
		for _ in range(0, int(input("How many games: "))):
			game = Game()
			self.turnSeq = []
			while not game.Game_Over():
				self.Visited[game.currState] += 1
				#if self.Visited[game.currState] > 100000:
					#self.play_optimal(game)
				#else:
				self.play_random(game)
				if game.Game_Over():
					self.calcQualities()
					self.turnSeq.append((game.currState, -1))
				self.calcQualities()

		with open('StateQualities.pkl', 'wb') as f:
			pickle.dump(self.StateQualities, f, pickle.HIGHEST_PROTOCOL)
		with open('Visited.pkl', 'wb') as f:
			pickle.dump(self.Visited, f, pickle.HIGHEST_PROTOCOL)

	def play_optimal(self, game):
		directions = [
			self.StateQualities[(game.currState,'N')],
			self.StateQualities[(game.currState,'E')],
			self.StateQualities[(game.currState,'S')],
			self.StateQualities[(game.currState,'W')]
		]
		action = self.Moves[directions.index(max(directions))]
		self.turnSeq.append((game.currState, action))
		game.tryMove(action)

	def play_random(self, game):
		action = self.Moves[random.randint(0, 3)]
		self.turnSeq.append((game.currState, action))
		if self.Visited[self.turnSeq[-1][0]] == 1:
			self.StateQualities[(self.turnSeq[-1][0],'N')] = 0
			self.StateQualities[(self.turnSeq[-1][0],'E')] = 0
			self.StateQualities[(self.turnSeq[-1][0],'S')] = 0
			self.StateQualities[(self.turnSeq[-1][0],'W')] = 0
		game.tryMove(action)

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
					self.StateQualities[(self.turnSeq[-1][0],'N')],
					self.StateQualities[(self.turnSeq[-1][0],'E')],
					self.StateQualities[(self.turnSeq[-1][0],'S')],
					self.StateQualities[(self.turnSeq[-1][0],'W')]
				]
				bestaction = self.StateQualities[(self.turnSeq[-1][0],self.Moves[directions.index(max(directions))])]
			self.StateQualities[self.turnSeq[-2]] += (reward + (0.9*bestaction)
				-self.StateQualities[self.turnSeq[-2]]) / self.Visited[self.turnSeq[-2][0]]

