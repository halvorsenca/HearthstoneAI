from bs4 import BeautifulSoup
from urllib.request import urlopen

page = urlopen('https://www.google.com/')
soup = BeautifulSoup(page, 'html.parser')
