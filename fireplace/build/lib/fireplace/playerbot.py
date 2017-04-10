import random
from .logging import log
from hearthstone.enums import CardType


def play_aggressive_turn(game: ".game.Game"):
	play_biggest_minion(game.players[0])
# Make all minions go face
	attack_hero(game.players[0])

	#if game.players[0].hand[0].data.type is CardType.MINION:
		#print(game.players[0].hand[0].health)
		#print(game.players[0].hand[0].atk)
	#print(game.players[1].field)
	#print(game.players[1].hero.health)
	#print(game.players[1].hero.armor)


# Play the biggest minion in hand
def play_biggest_minion(player):
	playable_cards = get_playable_cards(player.hand)
	if len(playable_cards) > 0:
		playable_cards.sort(key=lambda card: card.cost, reverse=True)
		for card in playable_cards:
			if card.data.type is CardType.MINION:
				target = None
				if card.must_choose_one:
					card = random.choice(card.choose_cards)
				if card.requires_target():
					target = random.choice(card.targets)
				log.info("Playing %r on %r" % (card, target))
				card.play(target=target)
				if player.choice:
					choice = random.choice(player.choice.cards)
					log.info("Choosing card %r" % (choice))
					player.choice.choose(choice)
				break
	print("Playing Biggest Minion")

# Play several smaller minions in hand
def play_multiple_minions():
	print("Playing multiple_minions")

# make efficient trades then attack hero
def trade_minions():
	print("Trade minions")

# Attack hero with everything
def attack_hero(player):
	for character in player.characters:
		if character.can_attack():
			character.attack(character.targets[0])
	print("Attack Hero")

def get_playable_cards(cards):
	playable_cards = []
	for card in cards:
		if card.is_playable():
			playable_cards.append(card)
	return playable_cards
