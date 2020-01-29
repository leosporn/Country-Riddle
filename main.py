import os
from html.parser import HTMLParser

import matplotlib.image as img
import matplotlib.pyplot as plt
import numpy as np
import requests

url = 'https://www.worldometers.info/geography/alphabetical-list-of-countries/'

upper_case_letters = set(chr(i) for i in range(ord('A'), ord('A') + 26))
lower_case_letters = {s.lower() for s in upper_case_letters}
other_accepted_characters = {' '}

accepted_characters = upper_case_letters | lower_case_letters | other_accepted_characters

no_holes = set()


class customHTMLParser(HTMLParser):

    def error(self, message):
        pass

    def __init__(self):
        super().__init__()
        self.raw_data = []

    def handle_data(self, data):
        self.raw_data.append(data)


if __name__ == '__main__':
    from time import time

    start = time()
    for letter in upper_case_letters:
        plt.clf()
        plt.text(0, 0, letter, {'fontsize': 20})
        plt.axis('off')
        plt.savefig('letter.png')
        X = 1 - img.imread('letter.png')
        X = X[:, :, :3].mean(2)
        X = X[(X > 0).any(1), :]
        X = X[:, (X > 0).any(0)]
        X[X > 0] = 1
        X[:, 0] = 0
        X[0, :] = 0
        X[:, -1] = 0
        X[-1, :] = 0
        X = X.astype(np.int)
        stack = [(0, 0)]
        while len(stack) > 0:
            x, y = stack.pop()
            X[x, y] = 1
            for dx, dy in ((0, -1), (0, +1), (-1, 0), (+1, 0)):
                try:
                    if X[x + dx, y + dy] == 0:
                        stack.append((x + dx, y + dy))
                except IndexError:
                    continue
        if (X == 1).all():
            no_holes.add(letter)
    os.remove('letter.png')

    parser = customHTMLParser()
    parser.feed(requests.get(url).text)

    countries = filter(lambda line: len(line) > 1, parser.raw_data)
    countries = filter(lambda line: all(s in accepted_characters for s in line), countries)
    countries = filter(lambda line: any(s in lower_case_letters for s in line), countries)
    countries = filter(lambda line: any(s in upper_case_letters for s in line), countries)
    countries = filter(lambda line: 'population' not in line.lower(), countries)
    countries = filter(lambda line: 'countries' not in line.lower(), countries)
    countries = filter(lambda line: 'country' not in line.lower(), countries)
    countries = filter(lambda line: 'area' not in line.lower(), countries)
    countries = filter(lambda line: 'density' not in line.lower(), countries)
    countries = filter(lambda line: all(letter in no_holes for letter in line.upper()), countries)

    for country in countries:
        print(country)
