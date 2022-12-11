from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, urljoin
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd

from indexer import Indexer

class Parser:
    def __init__(self):
        self.indexer = Indexer()

    def __get_links(self, soup):
        links = []
        for link in soup.find_all('a', attrs={'href': re.compile("^https://")}):
            url = link['href']
            links.append(urljoin(url, urlparse(url).path))
        return links
    
    def __get_word_frequency(self, soup):
        text = soup.get_text()
        cv = CountVectorizer(stop_words='english') 
        cv_matrix = cv.fit_transform([text]) 
        word_freq = pd.DataFrame(cv_matrix.toarray(), columns=cv.get_feature_names_out()).to_dict('dict')
        word_freq = {word: stats[0] for word, stats in word_freq.items() }
        return word_freq

    def parse(self, url, html):
        soup = BeautifulSoup(html, 'html.parser')

        links = self.__get_links(soup)

        word_freq = self.__get_word_frequency(soup)

        new_links = []
        for link in links:
            refs = self.indexer.increment_num_references(link)
            if refs == 1:
                new_links.append(link)

        self.indexer.insert_data(url, word_freq)

        return new_links, word_freq
