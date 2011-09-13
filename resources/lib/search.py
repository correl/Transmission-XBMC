import re
import socket
from urllib2 import urlopen
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup

socket.setdefaulttimeout(15)

class Search:
    def __init__(self):
        return NotImplemented
    def search(terms):
        return NotImplemented

class BTJunkie(Search):
    def __init__(self):
        self.search_uri = 'http://btjunkie.org/rss.xml?query=%s&o=52'
    def search(self, terms):
        torrents = []
        url = self.search_uri % '+'.join(terms.split(' '))
        f = urlopen(url)
        soup = BeautifulStoneSoup(f.read())
        for item in soup.findAll('item'):
            (name, seeds, leechers) = re.findall('(.*?)\s+\[(\d+)\/(\d+)\]$', item.title.text)[0]
            torrents.append({
                'url': item.enclosure['url'],
                'name': name,
                'seeds': int(seeds),
                'leechers': int(leechers),
            })
        return torrents
class TPB(Search):
    def __init__(self):
        self.search_uri = 'http://thepiratebay.org/search/%s/'
    def search(self, terms):
        torrents = []
        url = self.search_uri % '+'.join(terms.split(' '))
        f = urlopen(url)
        soup = BeautifulSoup(f.read())
        for details in soup.findAll('a', {'class': 'detLink'}):
            name = details.text
            url = details.findNext('a', {'href': re.compile('^http:\/\/torrents\.thepiratebay\.org\/')})['href']
            td = details.findNext('td')
            seeds = int(td.text)
            td = td.findNext('td')
            leechers = int(td.text)
            torrents.append({
                'url': url,
                'name': name,
                'seeds': seeds,
                'leechers': leechers,
            })
        return torrents

if __name__ == '__main__':
    s = TPB()
    results = s.search('zettai')
