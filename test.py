from bs4 import BeautifulSoup
from urllib.request import urlopen

page = urlopen('http://www.icy-veins.com/hearthstone/warrior-standard-decks')
soup = BeautifulSoup(page,'html.parser')

decks = soup.find_all(class_="deck_presentation_name")

for link in decks:
    line = link.a
    print(line['href'])

#for link in decks:
#    links = decks.find_all("href")

#print(links)
