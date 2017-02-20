from bs4 import BeautifulSoup
from urllib.request import urlopen
import sys
from pymongo import MongoClient

client = MongoClient()
db = client.test

sys.stdout = open("cards.txt","w")

heroes = ["warrior", "druid", "hunter", "mage", "paladin", "priest", "rogue", "shaman", "warlock"]
url = "http://www.icy-veins.com/hearthstone/"

#for all the heroes in the heroes list run through an iteration of a list
for i in range(0,len(heroes)):
	
	#create the insertion entry for the hero database
	insertion_hero = {"HeroName" : heroes[i], "Decks" : []}

	#create the new url for the open by appending the hero name on the url set above
	tempUrl = url + heroes[i] + "-standard-decks"
	page = urlopen(tempUrl)
	soup = BeautifulSoup(page,'html.parser')

	#will redirect the html files into a someDir and then create a zip file for it
	with open("someDir/" + heroes[i]+".html","w") as outputfile:
		outputfile.write(str(soup))

	deck = soup.find(class_="deck_presentation_name")

	decks = soup.find_all(class_="deck_presentation_name")

	decknum = 1;
	
	#for each link in the decks classification 
	for link in decks:
		
		#create the base entry for the deck database
		insertion_deck = {"DeckID": decknum, "DeckName" : link.contents[1].contents[0], "Cards" : []}

		line = link.a
		if any(word in line['href'] for word in ("cheap", "budget", "basic")):
			continue

		#opens the decks page to retrieve cards
		newPage = urlopen("http:" + line['href'])
		newSoup = BeautifulSoup(newPage,'html.parser')
		with open("someDir/" + link.contents[1].contents[0].replace("/",'') + ".html", "w") as outputfile:
			outputfile.write(str(newSoup))

		cardTable = newSoup.find('table', class_="deck_card_list")
		entry = cardTable.find_all('li')

		#once again will run through each card in the table and gather information about that card
		for card in entry:
			amount = int(card.contents[0][0])        
			name = card.contents[1].contents[0]
			
			#if there are multiple of one card it will print it to the deck the number of times needed
			for x in range(0, amount):
				insertion_deck['Cards'].append(name)

		#finishes the insertion process for the deck 
		posts = db.decks
		insertion_id = posts.insert_one(insertion_deck).inserted_id

		decknum += 1

		print(decknum)

		insertion_hero['Decks'].append(link.contents[1].contents[0])

	
	heroDb = db.heroes
	hero_id = heroDb.insert_one(insertion_hero).inserted_id

