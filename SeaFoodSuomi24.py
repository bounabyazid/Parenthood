#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Wed Feb 27 04:46:24 2020

@author: Yazid BOUNAB
"""
import pickle
from urllib.request import urlopen
from bs4 import BeautifulSoup

from afinn.afinn import Afinn

from googletrans import Translator

BaseLink = 'https://keskustelu.suomi24.fi'
Section = 'ruoka-ja-juoma/kala-ja-ayriaiset'

Russialist = ['venäläinen','Venäjä','ryssä','venäjän']

def getReplyofReplay(element):
    Replies = []
    elements = element.find_all('p')
    for elem in elements:
        Replies.append(elem.text)
        Replies.extend(getReplyofReplay(elem))
    return list(set(Replies))

def getReplies(link):
    Replies = []
    print(link)
    soup = BeautifulSoup(urlopen(link), 'lxml')
    Table = soup.find('section', class_='ThreadComments__ThreadCommentsContainer-xoykri-1 bBdsfj')
    Table = Table.find('ul', class_='ThreadComments__CommentsList-xoykri-3 fPfGZn')
    for replay in Table.find_all('li'):
        Replies.append(replay.find('p').text)
        Replies.extend(getReplyofReplay(replay))
    return list(set(Replies))

def getPage(PageNumber):
    page = {}
    Discussions = []
    link = BaseLink+'/'+Section+'?page='+PageNumber
    soup = BeautifulSoup(urlopen(link), 'lxml')
    Table = soup.find('div', class_='row threads-list-container')
    
    page['page'+PageNumber] = []    
    for Discussion in Table.find_all('li', class_='thread-list-item thread-list-item-small'):
        Data = {}
        
        Data['Title'] = Discussion.find('div', class_='thread-list-item-title text-overflow').text
        Data['Link'] = Discussion.find('a', class_='thread-list-item-container')['href']
        Data['Date'] = Discussion.find('div', class_='thread-list-item-timestamp text-secondary text-bold-2 smaller pull-right').text
        Data['Text'] = Discussion.find('div', class_='thread-list-item-body text-black text-overflow').text
        Data['Replies'] = getReplies(Data['Link'])
        
        Discussions.append(Data)

    return Discussions

def getAllPages(BaseLink,Section,pages):
    
    link = BaseLink+'/'+Section
    soup = BeautifulSoup(urlopen(link), 'lxml')
    NbPages = int(soup.find('span', class_='pagination-page-count').text)
    NbPages = 88
    for PageNumber in range(61,NbPages+1):
        print('_________________',PageNumber,'_________________')
        pages['page'+str(PageNumber)] = getPage(PageNumber=str(PageNumber))
        
def getAllText(pages):
    AllText = []
    NbPages = 88
    for PageNumber in range(1,NbPages+1):
        for Discution in pages['page'+str(PageNumber)]:
            AllText.append(Discution['Title'])
            AllText.append(Discution['Text'])
            AllText.extend(Discution['Replies'])
    
    return AllText

def getCommentaboutRussia():
    RusiaComments = []
    EnglishComments = []
    pickle_in = open('Fish and SeaFood.pkl',"rb")
    pages = pickle.load(pickle_in)
    AllText = getAllText(pages)
    
    translator = Translator()

    for Text in AllText:
        if any(item in Text for item in Russialist):
           RusiaComments.append(Text)
           EnglishComments.append(translator.translate(Text).text)
    
    return RusiaComments, EnglishComments

def Sentiments(TargetTextList):
    'https://medium.com/@himanshu_23732/sentiment-analysis-with-afinn-lexicon-930533dfe75b'
    af = Afinn(language='fi',emoticons=True)

    sentiment_scores = [af.score(comment) for comment in TargetTextList[0:10]]
    
    sentiment_category = ['positive' if score > 0 
                          else 'negative' if score < 0 
                              else 'neutral' 
                                  for score in sentiment_scores]
    
    return sentiment_scores
    

pages = {}

pickle_in = open('Fish and SeaFood.pkl',"rb")
pages = pickle.load(pickle_in)

#getAllPages(BaseLink,Section,pages)
#
#pickle_out = open("Fish and SeaFood.pkl","wb")
#pickle.dump(pages, pickle_out)
#pickle_out.close()

#AllText = getAllText(pages)
#sentiment_scores = Sentiments()

RusiaComments, EnglishComments = getCommentaboutRussia()