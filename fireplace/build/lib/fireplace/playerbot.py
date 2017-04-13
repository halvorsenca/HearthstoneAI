import random
from .logging import log
from hearthstone.enums import CardType


"""
def play_aggressive_turn(game: ".game.Game"):
	play_biggest_minion(game.players[0])
	attack_hero(game.players[0])
"""

# Play Mountain Giant or Twilight Drake... Or any other
def play_offensive(game):
# Mountain Giant, Twilight Drake, Abysal Enforcer
	card_ids = ['EX1_105', 'EX1_043','CFM_751']
	playable_cards = get_playable_cards(game.players[0].hand)
	offensive_cards = []
	if len(playable_cards) > 0:
		for card in playable_cards:
			if card.id in card_ids:
				offensive_cards.append(card)
		if len(offensive_cards) > 0:
			offensive_cards.sort(key=sort_offensive_cards)
			offensive_cards[0].play()
			return True
	return False

def sort_offensive_cards(card):
	card_order = {
		'EX1_043' : 1,
		'EX1_105' : 2,
		'CFM_751' : 3
	}
	return card_order[card.id]

# Play a creature like Ancient Watcher that is meant for defense
def play_defensive(game):
# Sunfury Protector, Defender of Argus, Faceless Shambler
	card_ids = ['EX1_058', 'EX1_093', 'OG_174']
	playable_cards = get_playable_cards(game.players[0].hand)
	if len(playable_cards) > 0:
		for card in playable_cards:
			if card.id in card_ids:
				if card.id == card_ids[2]:
					target = None
					for minion in card.targets:
						if target == None or target.health < minion.health:
							target = minion
						elif target.health == minion.health and target.atk < minion.atk:
							target = minion
					if target != None:
						card.play(target=target)
						return True
				else:
					# Need to find index
					play = 0
					prevStat = 0
					currStat = 0
					prev_minion = None
					for i, minion in enumerate(game.players[0].field):
						if i == 0:
							prev_minion = minion
							play = 1
						else:
							currStat = prev_minion.health + minion.health
							if currStat > prevStat:
								prevStat = currStat
								play = i
					card.play(index=play)
					return True
	return False

# Play a creature like Earthern ring farseer to heal minions/hero
def play_utility(game):
# Ancient Watcher, Earthen Ring Farseer, Mistress of Mixtures, Lord Jaraxxus
# Always heal damaged minions, else heal hero if none to heal
	card_ids = ['EX1_045', 'CS2_117', 'CFM_120', 'EX1_323']
	playable_cards = get_playable_cards(game.players[0].hand)
	if len(playable_cards) > 0:
		for card in playable_cards:
			if card in card_ids:
				if card.id == card_ids[1]:
					targets = []
					for minion in card.targets:
						if minion.max_health - 3 >= minion.health and not minion in game.players[1].characters:
							targets.append(minion)
					if len(targets) > 0:
						targets.sort(key=lambda minion: minion.atk + minion.max_health, reverse=True)
						card.play(target=targets[0])
						return True
					elif game.players[0].hero.health <= 27:
						card.play(target=game.players[0].hero)
						return True
				else:
					card.play()
					return True
	return False

def trade_spell(game):
#Mortal Coil, Shadow Bolt, Siphon Soul
# Check if spells exist, then search for minions with 1 or 4 health
	card_ids = ['EX1_302', 'CS2_057', 'EX1_309']
	playable_cards = get_playable_cards(game.players[0].hand)
	spells = []
	if len(playable_cards) > 0:
		for card in playable_cards:
			if card in card_ids:
				spells.append(card)
		if len(spells) > 0:
			spells.sort(key=lambda card: card.cost)
			for card in spells:
				if card.id == card_ids[0]:
					health = 1
				elif card.id == card_ids[1]:
					health = 4
				else:
					health = 999
				targets = []
				for enemy in card.targets:
					if enemy in game.players[1].field:
						if enemy.health <= health:
							targets.append(enemy)
				if len(targets) > 0:
					targets.sort(key=lambda minion: minion.atk, reverse=True)
					card.play(target=targets[0])
					return True
	return False

# make efficient trades then attack hero
def trade_minions(game):
	minions = []
	field = list(game.players[0].field)
	for minion in field:
		if minion.can_attack():
			minions.append(minion)
	if len(minions) > 0:
		minions.sort(key=lambda minion: minion.atk + minion.health, reverse=True)
		if len(minions[0].targets) > 0:
			targets = minions[0].targets
			targets.sort(key=lambda minion: minion.atk + minion.health)
			#print("Attacking with: ", minions[0], "\nTarget: ", targets[0])
			minions[0].attack(targets[0])
			return True
	return False

def wipe_field(game):
# Doomsayer, Hellfire, Shadowflame, Twisting Nether, Abysal Enforcer
	card_ids = ['NEW1_021', 'CS2_062', 'EX1_303', 'EX1_312', 'CFM_751']
	playable_cards = get_playable_cards(game.players[0].hand)
	if len(playable_cards) > 0:
		for card in playable_cards:
			if card in card_ids:
				if card.id == card_ids[2]:
					strongest = 0
					for enemy in game.players[0].field:
						if enemy.health > strongest:
							strongest = enemy.health
					targets = []
					for minion in card.targets:
						if minion.atk >= strongest:
							targets.append(minion)
					if len(targets) > 0:
						targets.sort(key=lambda minion: minion.health + minion.atk)
						card.play(target=targets[0])
						return True
				else:
					card.play()
					return True
	return False

# Attack hero with everything that can attack
def attack_hero(game):
	result = False
	characters = list(game.players[0].characters)
	for character in characters:
		if character.can_attack():
			#print("Attacking with: ", character, "\nTarget: ", character.targets[0])
			character.attack(character.targets[0])
			result = True
	return result

# Use the Hero Power
def use_hero_power(game):
	if game.players[0].hero.power.is_usable():
		game.players[0].hero.power.use()
		return True
	return False

def end_turn(game):
	game.end_turn()
	return True

def get_playable_cards(cards):
	playable_cards = []
	for card in cards:
		if card.is_playable():
			playable_cards.append(card)
	return playable_cards

