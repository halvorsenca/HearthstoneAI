from bs4 import BeautifulSoup
from urllib.request import urlopen

page = urlopen('http://www.icy-veins.com/hearthstone/')
soup = BeautifulSoup(page)

print(soup.prettify())
