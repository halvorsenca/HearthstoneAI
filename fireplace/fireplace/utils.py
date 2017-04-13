import random
import os.path
from bisect import bisect
from importlib import import_module
from pkgutil import iter_modules
from typing import List
from xml.etree import ElementTree
from hearthstone.enums import CardClass, CardType
from .logging import log 
from . import playerbot
from . import cards

# Autogenerate the list of cardset modules
_cards_module = os.path.join(os.path.dirname(__file__), "cards")
CARD_SETS = [cs for _, cs, ispkg in iter_modules([_cards_module]) if ispkg]


# Some of the methods in this class may be useful
class CardList(list):
	def __contains__(self, x):
		for item in self:
			if x is item:
				return True
		return False

	def __getitem__(self, key):
		ret = super().__getitem__(key)
		if isinstance(key, slice):
			return self.__class__(ret)
		return ret

	def __int__(self):
		# Used in Kettle to easily serialize CardList to json
		return len(self)

	def contains(self, x):
		"True if list contains any instance of x"
		for item in self:
			if x == item:
				return True
		return False

	def index(self, x):
		for i, item in enumerate(self):
			if x is item:
				return i
		raise ValueError

	def remove(self, x):
		for i, item in enumerate(self):
			if x is item:
				del self[i]
				return
		raise ValueError

	def exclude(self, *args, **kwargs):
		if args:
			return self.__class__(e for e in self for arg in args if e is not arg)
		else:
			return self.__class__(e for k, v in kwargs.items() for e in self if getattr(e, k) != v)

	def filter(self, **kwargs):
		return self.__class__(e for k, v in kwargs.items() for e in self if getattr(e, k, 0) == v)


def random_draft(card_class: CardClass, exclude=[]):
	"""
	Return a deck of 30 random cards for the \a card_class
	"""
	from . import cards
	from .deck import Deck

	deck = []
	collection = []
	hero = card_class.default_hero

	for card in cards.db.keys():
		if card in exclude:
			continue
		cls = cards.db[card]
		if not cls.collectible:
			continue
		if cls.type == CardType.HERO:
			# Heroes are collectible...
			continue
		if cls.card_class and cls.card_class != card_class:
			continue
		collection.append(cls)

	while len(deck) < Deck.MAX_CARDS:
		card = random.choice(collection)
		if deck.count(card.id) < card.max_count_in_deck:
			deck.append(card.id)

	return deck


def random_class():
	return CardClass(random.randint(2, 10))


def get_script_definition(id):
	"""
	Find and return the script definition for card \a id
	"""
	for cardset in CARD_SETS:
		module = import_module("fireplace.cards.%s" % (cardset))
		if hasattr(module, id):
			return getattr(module, id)


def entity_to_xml(entity):
	e = ElementTree.Element("Entity")
	for tag, value in entity.tags.items():
		if value and not isinstance(value, str):
			te = ElementTree.Element("Tag")
			te.attrib["enumID"] = str(int(tag))
			te.attrib["value"] = str(int(value))
			e.append(te)
	return e


# This method sucks for what we are trying to do
def game_state_to_xml(game):
	tree = ElementTree.Element("HSGameState")
	tree.append(entity_to_xml(game))
	for player in game.players:
		tree.append(entity_to_xml(player))
	for entity in game:
		if entity.type in (CardType.GAME, CardType.PLAYER):
			# Serialized those above
			continue
		e = entity_to_xml(entity)
		e.attrib["CardID"] = entity.id
		tree.append(e)

	return ElementTree.tostring(tree)


def weighted_card_choice(source, weights: List[int], card_sets: List[str], count: int):
	"""
	Take a list of weights and a list of card pools and produce
	a random weighted sample without replacement.
	len(weights) == len(card_sets) (one weight per card set)
	"""

	chosen_cards = []

	# sum all the weights
	cum_weights = []
	totalweight = 0
	for i, w in enumerate(weights):
		totalweight += w * len(card_sets[i])
		cum_weights.append(totalweight)

	# for each card
	for i in range(count):
		# choose a set according to weighting
		chosen_set = bisect(cum_weights, random.random() * totalweight)

		# choose a random card from that set
		chosen_card_index = random.randint(0, len(card_sets[chosen_set]) - 1)

		chosen_cards.append(card_sets[chosen_set].pop(chosen_card_index))
		totalweight -= weights[chosen_set]
		cum_weights[chosen_set:] = [x - weights[chosen_set] for x in cum_weights[chosen_set:]]

	return [source.controller.card(card, source=source) for card in chosen_cards]


def setup_game() -> ".game.Game":
	from .game import Game
	from .player import Player

	from pymongo import MongoClient

	client = MongoClient()
	db = client.test

	heromap = {
		"WARRIOR": CardClass.WARRIOR.default_hero,
		"DRUID": CardClass.DRUID.default_hero,
		"HUNTER": CardClass.HUNTER.default_hero,
		"MAGE": CardClass.MAGE.default_hero,
		"PALADIN": CardClass.PALADIN.default_hero,
		"PRIEST": CardClass.PRIEST.default_hero,
		"ROGUE": CardClass.ROGUE.default_hero,
		"WARLOCK": CardClass.WARLOCK.default_hero,
		"SHAMAN": CardClass.SHAMAN.default_hero,
	}

	#get a random hero
	#hero1 = random.choice(list(heromap.keys()))
	#hero1lower = hero1.lower()

	#get the decks from the hero
	#deckmap1 = db.heroes.find({"HeroName" : hero1lower}, {"Decks" : 1, "_id" : 0})
	#for hey in deckmap1:
		#deckerino1 = hey["Decks"]
	#return a random deck
	#deckchoice1 = random.choice(deckerino1)
	
	#get the cards from the random deck
	#cards1 = db.decks.find({"DeckName" : deckchoice1}, {"Cards" : 1, "_id" : 0})
	#for hi in cards1:
	#	carderino1 = hi["Cards"]

	#create the deck from the ground up 
	#deck1 = []
	#for every in carderino1:
	#	deck1.append(cards.filter(name=every)[0])
	
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
	#deck2 = random_draft(CardClass.PALADIN)
	player1 = Player("Player1", deck1, CardClass.WARLOCK.default_hero)
	player2 = Player("Player2", deck2, CardClass.HUNTER.default_hero)

	game = Game(players=(player1, player2))
	game.start()

	return game


##
# Start a turn off by looking at a list of playable card.
# Separate into spells and minions.
# Check for win condition, if true then go for win.
# Else, check enemy minions for valuable trades through spells or weaker minions.
# Then calculate maximum damage that is playable that turn.
#
# Things to research:
#   Maybe make two methods for player1_turn and player2_turn
#   How to mulligan?
##
def play_turn(game: ".game.Game") -> ".game.Game":
	if game.players[0].current_player:
		play_random_turn(game.players[0])
	elif game.players[1].current_player:
		play_random_turn(game.players[1])
	game.end_turn()
	return game

def play_random_turn(player):
	heropower = player.hero.power
	if heropower.is_usable() and random.random() < 0.1:
		if heropower.requires_target():
			heropower.use(target=random.choice(heropower.targets))
		else:
			heropower.use()

	# iterate over our hand and play whatever is playable
	for card in player.hand:
		if card.is_playable() and random.random() < 0.5:
			target = None
			if card.must_choose_one:
				card = random.choice(card.choose_cards)
			if card.requires_target():
				target = random.choice(card.targets)
			log.info("Playing %r on %r" % (card, target))
			card.play(target=target)

			if player.choice:
				choice = random.choice(player.choice.cards)
				#print("Choosing card %r" % (choice))
				player.choice.choose(choice)

			continue

	# Randomly attack with whatever can attack
	for character in player.characters:
		if character.can_attack():
			character.attack(random.choice(character.targets))

def play_full_game() -> ".game.Game":
	game = setup_game()

	for player in game.players:
# Need to change how my bot mulligans
		print("Can mulligan %r" % (player.choice.cards))
		mull_count = random.randint(0, len(player.choice.cards))
		cards_to_mulligan = random.sample(player.choice.cards, mull_count)
		player.choice.choose(*cards_to_mulligan)

	playerInput = ''
	while True:
    # Could also add input to skip a number turns or go straight to the end
    # Also need to figure out how to make instance of the game state
		if playerInput != 'end':
			playerInput = input('Press enter to see next turn or type end to finish game: ')
		play_turn(game)
		print()

	return game
