from bs4 import BeautifulSoup
from urllib.request import urlopen

page = urlopen('http://www.icy-veins.com/hearthstone/warrior-standard-decks')
soup = BeautifulSoup(page,'html.parser')

all_tables=soup.find('table')
decks = soup.find('table', class_='deck_presentation')

links = decks.findAll('a')
for link in links:
    print(link.get("href"))

#warrior_links = decks.find_all("a")
#for link in warrior_links:
#    print(link.get("href"))
