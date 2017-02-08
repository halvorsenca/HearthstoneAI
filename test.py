from bs4 import BeautifulSoup
from urllib.request import urlopen
import sys
#from pymongo import MongoClient

#client = MongoClient()
#db = client.test

#sys.stdout = open("cards.txt","w")


page = urlopen('http://www.icy-veins.com/hearthstone/warrior-standard-decks')
soup = BeautifulSoup(page,'html.parser')

deck = soup.find(class_="deck_presentation_name")

decks = soup.find_all(class_="deck_presentation_name")

decknum = 1;

for link in decks:
    line = link.a
    if any(word in line['href'] for word in ("cheap", "budget", "basic")):
        continue
    newPage = urlopen("http:" + line['href'])
    newSoup = BeautifulSoup(newPage,'html.parser')

    cardTable = newSoup.find('table', class_="deck_card_list")
    entry = cardTable.find_all('li')
    for card in entry:
        amount = int(card.contents[0][0])        
        name = card.contents[1].contents[0]
        
        for x in range(0, amount):
            result = db.decks.insert_one(
                {
                    "deckID": str(decknum),
                }
            




#resultHero = db.heroes.insert_one(
#    {
#        #heroname: [deckID1, deckID2, ...]
#    }

