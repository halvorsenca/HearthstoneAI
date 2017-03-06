import random
from hearthstone.enums import CardType


def play_aggressive_turn(game: ".game.Game"):
	playable_cards = get_playable_cards(game.players[0].hand)
	if len(playable_cards) > 0:
		playable_cards.sort(key=lambda card: card.cost, reverse=True)
# Check for threats that can be killed by spells
		for card in playable_cards:
			if card.data.type is CardType.MINION:
				target = None
				if card.must_choose_one:
# Probably don't need to worry about this as much in aggressive play
# Machine Learning would be much better at making these decisions
					card = random.choice(card.choose_cards)
				if card.requires_target():
# This will also need to get elaborated
					target = random.choice(card.targets)
				print("Playing %r on %r" % (card, target))
				card.play(target=target)
				if game.players[0].choice:
					choice = random.choice(game.players[0].choice.cards)
					print("Choosing card %r" % (choice))
					game.players[0].choice.choose(choice)
			break

# Make all minions go face
	for character in game.players[0].characters:
		if character.can_attack():
			character.attack(character.targets[0])

	#if game.players[0].hand[0].data.type is CardType.MINION:
		#print(game.players[0].hand[0].health)
		#print(game.players[0].hand[0].atk)
	#print(game.players[1].field)
	#print(game.players[1].hero.health)
	#print(game.players[1].hero.armor)


def get_playable_cards(cards):
	playable_cards = []
	for card in cards:
		if card.is_playable():
			playable_cards.append(card)
	return playable_cards
