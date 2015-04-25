import sys
import re
import socket
from urllib2 import urlopen, Request, URLError, HTTPError
from urllib import quote, quote_plus, urlencode
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup

socket.setdefaulttimeout(15)

class Search:
    def __init__(self):
        return NotImplemented
    def search(terms):
        return NotImplemented

class Mininova(Search):
    def __init__(self):
        self.search_uri = 'http://www.mininova.org/rss/%s'
    def search(self, terms):
        torrents = []
        url = self.search_uri % quote_plus(terms)
        f = urlopen(url)
        soup = BeautifulStoneSoup(f.read())
        for item in soup.findAll('item'):
            (seeds, leechers) = re.findall('Ratio: (\d+) seeds, (\d+) leechers', item.description.text)[0]
            torrents.append({
                'url': item.enclosure['url'],
                'name': item.title.text,
                'seeds': int(seeds),
                'leechers': int(leechers),
            })
        return torrents
class TPB(Search):
    def __init__(self):
        self.user_agent = 'Mozilla/5.0'
        self.search_uris = ['https://thepiratebay.se/search/%s/',
                            'http://pirateproxy.net/search/%s/']
    def search(self, terms):
        torrents = []
        f = None
        for url in [u % quote(terms) for u in self.search_uris]:
            req = Request(url)
            req.add_header('User-Agent', self.user_agent)
            try:
                f = urlopen(req)
                break
            except URLError:
                continue
        if not f:
            raise Exception('Out of pirate bay proxies')
        soup = BeautifulSoup(f.read())
        for details in soup.findAll('a', {'class': 'detLink'}):
            name = details.text
            url = details.findNext('a', {'href': re.compile('^magnet:')})['href']
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
class Kickass(Search):
    def __init__(self):
        self.search_uri = 'http://kickass.to/usearch/%s/?field=seeders&sorder=desc&rss=1'
    def search(self, terms):
        torrents = []
        url = self.search_uri % quote_plus(terms)
        try:
            f = urlopen(url)
            soup = BeautifulStoneSoup(f.read())
            for item in soup.findAll('item'):
                torrents.append({
                    'url': item.enclosure['url'],
                    'name': item.title.text,
                    'seeds': int(item.find('torrent:seeds').text),
                    'leechers': int(item.find('torrent:peers').text),
                })
        except HTTPError as e:
            if e.code == 404:
                pass
            else:
                raise
        return torrents
class L337x(Search):
    def __init__(self):
        self.uri_prefix = 'http://1337x.to'
        self.search_uri = self.uri_prefix + '/sort-search/%s/seeders/desc/1/'
    def search(self, terms):
        torrents = []
        url = self.search_uri % quote_plus(terms)
        f = urlopen(url)
        soup = BeautifulStoneSoup(f.read())
        for details in soup.findAll('a', {'href': re.compile('^/torrent/')}):
            div = details.findNext('div')
            seeds = int(div.text)
            div = div.findNext('div')
            f_link = urlopen(self.uri_prefix + details['href'])
            soup_link = BeautifulStoneSoup(f_link.read())
            link = soup_link.find('a', {'href': re.compile('^magnet:')})
            if not link:
                continue
            torrents.append({
                'url': link['href'],
                'name': details.text,
                'seeds': seeds,
                'leechers': int(div.text),
            })
        return torrents
class YTS(Search):
    def __init__(self):
        self.search_uri = 'http://yts.to/rss/%s/all/all/0'
    def search(self, terms):
        torrents = []
        url = self.search_uri % quote(terms, '')
        f = urlopen(url)
        soup = BeautifulStoneSoup(f.read())
        for item in soup.findAll('item'):
            item_quality = item.link.text.rpartition('_')[2]
            item_f = urlopen(item.link.text)
            item_soup = BeautifulStoneSoup(item_f.read())
            qualities = [s.text.strip() for s in
                         item_soup.findAll('span', {'class': re.compile('^tech-quality')})]
            q_index = qualities.index(item_quality)
            span = item_soup.findAll('span', {'title': 'Peers and Seeds'})[q_index]
            ps_pos = len(span.parent.contents) - 1
            ps = span.parent.contents[ps_pos].split('/')
            torrents.append({
                'url': item.enclosure['url'],
                'name': item.title.text,
                'seeds': int(ps[1]),
                'leechers': int(ps[0])
            })
        return torrents
class Lime(Search):
    def __init__(self):
        self.search_uri = 'https://www.limetorrents.cc/searchrss/%s/'
    def search(self, terms):
        torrents = []
        url = self.search_uri % quote(terms)
        f = urlopen(url)
        soup = BeautifulStoneSoup(f.read())
        for item in soup.findAll('item'):
            (seeds, leechers) = re.findall('Seeds: (\d+) , Leechers (\d+)', item.description.text)[0]
            torrents.append({
                'url': item.enclosure['url'],
                'name': item.title.text,
                'seeds': int(seeds),
                'leechers': int(leechers)
            })
        return torrents
class EZTV(Search):
    def __init__(self):
        self.user_agent = 'Mozilla/5.0'
        self.uri_prefix = 'https://eztv.ch'
        self.search_uri = self.uri_prefix + '/search/'
    def search(self, terms):
        torrents = []
        data = {'SearchString': '', 'SearchString1': terms, 'search': 'Search'}
        req = Request(self.search_uri, urlencode(data))
        req.add_header('User-Agent', self.user_agent)
        f = urlopen(req)
        soup = BeautifulStoneSoup(f.read())
        for (c, item) in enumerate(soup.findAll('a', {'class': 'magnet'})):
            if c == 30: break
            info = item.findPrevious('a')
            link = self.uri_prefix + info['href']
            item_req = Request(link)
            item_req.add_header('User-Agent', self.user_agent)
            item_f = urlopen(item_req)
            item_soup = BeautifulStoneSoup(item_f.read())
            sp = item_soup.findAll('span', {'class': re.compile('^stat_')})
            if sp:
                sp = [int(i.text.replace(',', '')) for i in sp]
            else:
                sp = [0, 0]
            torrents.append({
                'url': item['href'],
                'name': info.text,
                'seeds': sp[0],
                'leechers': sp[1]
            })
        return torrents

if __name__ == '__main__':
    sites = [Mininova(), TPB(), Kickass(), L337x(), YTS(), Lime(), EZTV()]
    terms = 'transmission'
    if len(sys.argv) > 1:
        terms = sys.argv[1]
    print 'Searching for "' + terms + '"'
    for site in sites:
        print site.__class__.__name__.center(79, '=')
        torrents = site.search(terms)
        print 'Total found = ' + str(len(torrents))
        for counter, file in enumerate(torrents):
            print '[{:3},{:3}] {:33} "{:33}"'.format(file['seeds'], file['leechers'],
                                                     file['name'].encode('ascii', 'replace')[:33],
                                                     file['url'][:33])
            if counter == 9: break
