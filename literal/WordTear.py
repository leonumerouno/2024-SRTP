from time import sleep

import requests
import re
from collections import defaultdict

class WordTear(object):
    def __init__(self):
        self.url = "http://localhost/SegAPI/rest/seg"
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
        }
        self.Param = {}
        # self.stopwords = []
        # self.getStopWords()

    # def getStopWords(self):
    #     stop_words = set()
    #     with open('cn_stopwords.txt', 'r', encoding='utf-8') as f:
    #         for line in f.readlines():
    #             stop_words.add(line.split("\n")[0])
    #     with open('scu_stopwords.txt', 'r', encoding='utf-8') as f:
    #         for line in f.readlines():
    #             stop_words.add(line.split("\n")[0])
    #     self.stopwords = list(stop_words)

    def get_value(self, key, segstr):
        self.Param = {
            'secret': 'qt80oh3psexeifkh5don6jxidicygz4ibbq5um3z',
            'segstr': segstr,
            'mode': 1
        }
        resp = requests.get(self.url, params=self.Param, headers=self.header)
        split_words = resp.text.split(" ")
        word_list = []
        for split_word in split_words:
            if split_word != "":
                word, tag = split_word.split("/")
                if tag == key:
                    word_list.append(word)
        if len(word_list) == 1:
            return word_list[0]
        elif len(word_list) == 0:
            return ""
        else:
            return word_list

    def get_result(self, segstr):
        self.Param = {
            'secret': 'qt80oh3psexeifkh5don6jxidicygz4ibbq5um3z',
            'segstr': segstr,
            'mode': 1
        }
        resp = requests.get(self.url, params=self.Param, headers=self.header)
        return resp

    def get_names(self,segstr):
        self.Param = {
            'secret': 'qt80oh3psexeifkh5don6jxidicygz4ibbq5um3z',
            'segstr': segstr,
            'mode': 1
        }
        resp = requests.get(self.url, params=self.Param, headers=self.header)
        split_words = resp.text.split(" ")
        entities = []
        for split_word in split_words:
            split_word = split_word.split("/")
            if len(split_word) < 2:
                continue
            else:
                split_word_type = split_word[1]
                if split_word_type[0] == 'n':
                    entities.append(split_word[0])
        return entities

    def tear_context(self,segstr):
        self.Param = {
            'secret': 'qt80oh3psexeifkh5don6jxidicygz4ibbq5um3z',
            'segstr': segstr,
            'mode': 0
        }
        resp = requests.get(self.url, params=self.Param, headers=self.header)
        split_words = resp.text.split(" ")

        tot = 0
        word_list = set()
        dict = defaultdict(float)

        for split_word in split_words:
            if split_word == '':
                continue
            split_word = split_word.split("/")
            if '[' in split_word[0]:
                split_word[0] = split_word[0].split('[')[1]
            if ']' in split_word[0]:
                split_word[0] = split_word[0].split(']')[0]
            if split_word[1] == 'w' or split_word[0] in self.stopwords:
                continue
            tot+=1
            word_list.add(split_word[0])
            dict[split_word[0]] += 1

        for split_word in word_list:
            dict[split_word] = dict[split_word] / tot

        return dict

    def tear_entity(self,sentence_list):
        word_list = set()
        for sentence in sentence_list:
            self.Param = {
                'secret': 'qt80oh3psexeifkh5don6jxidicygz4ibbq5um3z',
                'segstr': sentence,
                'mode': 0
            }
            resp = requests.get(self.url, params=self.Param, headers=self.header)
            sleep(0.01)
            split_words = resp.text.split(" ")
            for split_word in split_words:
                if split_word == '':
                    continue
                split_word = split_word.split("/")
                if '[' in split_word[0]:
                    split_word[0] = split_word[0].split('[')[1]
                if ']' in split_word[0]:
                    split_word[0] = split_word[0].split(']')[0]
                if len(split_word) > 1 and split_word[1] == 'w' or split_word[0] in self.stopwords:
                    continue
                word_list.add(split_word[0])
        return list(word_list)



