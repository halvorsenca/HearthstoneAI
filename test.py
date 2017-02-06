from bs4 import BeautifulSoup
from urllib.request import urlopen

page = urlopen('http://www.icy-veins.com/hearthstone/warrior-standard-decks')
soup = BeautifulSoup(page,'html.parser')

deck = soup.find(class_="deck_presentation_name")

decks = soup.find_all(class_="deck_presentation_name")

for link in decks:
    line = link.a
    if any(word in line['href'] for word in ("cheap", "budget", "basic")):
        continue
    newPage = urlopen("http:" + line['href'])
    newSoup = BeautifulSoup(newPage,'html.parser')

    cardTable = newSoup.find('table', class_="deck_card_list")
    entry = cardTable.find_all('li')
    for card in entry:
        print(card.contents[0])
        print(card.contents[1].contents[0])


