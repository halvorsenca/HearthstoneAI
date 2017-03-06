import random

class Game():
	def __init__(self):
		self.START_STATE = 8
		self.WALL = 5
		self.REWARD_STATE = 3
		self.PENALTY_STATE = 7

		self.board = ['o','o','o','R','o','W','o','P','o','o','o','o']
		self.currState = 8
		self.moves = {'N': 0, 'E': 1, 'S': 2, 'W': 3}
		self.directions = ['N', 'E', 'S', 'W']
	
	def Game_Over(self):
		return self.currState in [3,7]

	def Start_Game(self):
		while not self.Game_Over():
			self.printBoard()
			print()
			self.tryMove(input("Which direction do you want to move in: "))

		if self.currState == 3:
			return 100
		elif self.currState == 7:
			return -100
		else:
			return 0
	
	def tryMove(self, direction):
		roll = random.random()
		move = ''
		if roll >= 0.8 and roll < 0.9:
			i = (self.moves[direction] + 1) % 4
			move = self.directions[i]
		elif roll >= 0.9:
			i = (self.moves[direction] - 1) % 4
			move = self.directions[i]
		else:
			move = direction
	
		if self.isLegal(move):
			return self.makeMove(move)
		else:
			return 0
	
	def makeMove(self, direction):
		if direction == 'N':
			self.currState -= 4
		elif direction == 'E':
			self.currState += 1
		elif direction == 'S':
			self.currState += 4
		elif direction == 'W':
			self.currState -= 1
		
		if self.currState == 3:
			return 100
		elif self.currState == 7:
			return -100
		else:
			return 0
	
	def isLegal(self, direction):
		if direction == 'N':
			nextState = self.currState - 4
			return nextState >= 0 and nextState != self.WALL
		elif direction == 'E':
			nextState = self.currState + 1
			return nextState >= 0 and nextState != self.WALL and not self.currState in [3,7,11]
		elif direction == 'S':
			nextState = self.currState + 4
			return nextState <= 11 and nextState != self.WALL
		elif direction == 'W':
			nextState = self.currState - 1
			return nextState >= 0 and nextState != self.WALL and not self.currState in [0,4,8]
		else:
			return False
	
	def printBoard(self):
		self.board[self.currState] = 'x'
		for i in range(0,9,4):
			print(self.board[i], self.board[i+1], self.board[i+2], self.board[i+3])
		self.board[self.currState] = 'o'
