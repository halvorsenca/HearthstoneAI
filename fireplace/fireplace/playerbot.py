import random
from .logging import log
from hearthstone.enums import CardType


def play_aggressive_turn(game: ".game.Game"):
	play_biggest_minion(game.players[0])
	attack_hero(game.players[0])

# Play Mountain Giant or Twilight Drake... Or any other
def play_offensive(player):
# Mountain Giant, Twilight Drake, Lord Jaraxxus, Abysal Enforcer
	card_ids = []
	playable_cards = get_playable_cards(player.hand)
	if len(playable_cards) > 0:
		playable_cards.sort(key=lambda card: card.cost)
		for card in playable_cards:
			if card.id is card_ids:
# Should update this some to not just play the first occurance
				card.play()
				return True
	return False

# Play a creature like Ancient Watcher that is meant for defense
def play_defensive():
# Sunfury Protector, Defender of Argus, Faceless Shambler
# Need to figure how to determine targets and positioning
	card_ids = []
	playable_cards = get_playable_cards(player.hand)
	if len(playable_cards) > 0:
		for card in playable_cards:
			if card.id in card_ids:
# TODO: If shamber need to find target
				card.play()
				return True
	return False

# Play a creature like Earthern ring farseer to heal minions/hero
def play_utility():
# Ancient Watcher, Earthen Ring Farseer, Mistress of Mixtures, Lord Jaraxxus
# Always heal damaged minions, else heal hero if none to heal
	card_ids = []
  playable_cards = get_playable_cards(player.hand)
  if len(playable_cards) > 0:
    for card in playable_cards:
			if card in card_ids:
#TODO: Earthern ring Farseer needs Target
				card.play()
				return True
  return False

def trade_spell(game):
#Mortal Coil, Shadow Bolt, Siphon Soul
# Check if spells exist, then search for minions with 1 or 4 health
# Update card_ids to determine which to cast and on who
	card_ids = []
  playable_cards = get_playable_cards(player.hand)
  if len(playable_cards) > 0:
    for card in playable_cards:
			if card in card_ids:
# TODO: All cards need targets
				card.play()
				return True
  return False

# make efficient trades then attack hero
def trade_minions(game):
# Without ML:
# 	Find largest stated minion
# 	Find smallest minion that can defeat it
  tradeMinions = []
  smallMinion = find_largest_minion(game.players[1].field)
  if smallMinion == 0:
    return False

  for minion in game.players[0].field:
    if minion.atk >= smallMinion.health:
      tradeMinions.append(minion)

  if len(tradeMinions) != 0:
    find_smallest_minion(tradeMinions).attack(smallMinion)
    return True
  return False

def find_smallest_minion(field):
  smallMinion = 0
  for minion in field:
    if smallMinion == 0 or smallMinion.health > minion.health:
      smallMinion = minion
  return smallMinion

def find_largest_minion(field):
  smallMinion = 0
  for minion in field:
    if smallMinion == 0 or smallMinion.health < minion.health:
      smallMinion = minion
  return smallMinion

def wipe_field(player):
# Doomsayer, Hellfire, Shadowflame, Twisting Nether, Abysal Enforcer
	card_ids = []
  playable_cards = get_playable_cards(player.hand)
  if len(playable_cards) > 0:
    for card in playable_cards:
			if card in card_ids:
# TODO: Shadowflame needs target
				card.play()
				return True
  return False

# Attack hero with everything that can attack
def attack_hero(player):
  result = False
	for character in player.characters:
		if character.can_attack():
			character.attack(character.targets[0])
      result = True
  return result

# Use the Hero Power
def use_hero_power(player):
  if player.hero.power.is_usable():
    player.hero.power.use()
    return True
  return False

def get_playable_cards(cards):
	playable_cards = []
	for card in cards:
		if card.is_playable():
			playable_cards.append(card)
	return playable_cards

