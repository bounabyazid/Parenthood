#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Wed Feb 27 04:46:24 2020

@author: Yazid BOUNAB
"""
import re
import time
import pickle

import random
from datetime import datetime
import requests

from urllib.request import urlopen
from bs4 import BeautifulSoup

from afinn.afinn import Afinn
from googletrans import Translator

Ontology = {
'parenthood' : ['Vanhemmuus', 'vanhemmuudesta', 'vanhemmuuteen', 'vanhemmuudelta', 'vanhemmuudelle', 'vanhemmuutena', 'vanhemmuudeksi'],
'Mother' : ['Äiti', 'äidistä', 'äitiin', 'äidiltä', 'äidille', 'äitinä', 'äidiksi'],
'Mothers' : ['Äidit', 'äideistä,äiteihin', 'äideiltä', 'äideille', 'äiteinä', 'äideiksi'],
'Father' : ['Isä', 'isästä', 'isään', 'isältä', 'isälle', 'isänä', 'isäksi'],
'Fathers' : ['Isät', 'isistä', 'isiin', 'isiltä', 'isille', 'isinä', 'isiksi'],
'Child' : ['Lapsi', 'lapsesta', 'lapseen', 'lapselta', 'lapselle', 'lapsena', 'lapseksi'],
'Children' : ['Lapset', 'lapsista', 'lapsiin', 'lapsilta', 'lapsille', 'lapsina', 'lapsiksi'],
'Adolescent' : ['Nuori', 'nuoresta', 'nuoreen', 'nuorelta', 'nuorelle', 'nuorena', 'nuoreksi'],
'adolescents' : ['Nuoret', 'nuorista', 'nuoriin', 'nuorilta', 'nuorille', 'nuorina', 'nuoriksi'],
'Childhood' : ['Lapsuus', 'lapsuudesta', 'lapsuuteen', 'lapsuudesta', 'lapsuudelle', 'lapsuutena', 'lapsuudeksi']}

class Debate:
      def __init__(self):
          self.BASE_URL = 'https://www.vauva.fi'
          self.Sections = {}

      def getMenuSectins(self, Section):
          soup = BeautifulSoup(urlopen(BASE_URL+Section), 'lxml')
          MainMenu = soup.find('nav')
    
          for SubMenu in MainMenu.find('ul', class_='menu').find_all('li'):
              #print(SubMenu,'\n___________________________')
              title = SubMenu.find('a', class_='menu__link').text
              link = SubMenu.find('a', class_='menu__link')['href']
              self.Sections[title] = {'link':link, 'Discussions':{}}     

      def get_sleep_time(self):
          return random.randrange(100, 221) / 1000
      
      def get_Section_page_count(self, url):
          page_number = 1
          while True:
                link = url + '?page=' + str(page_number)
                if requests.get(link).status_code != 200:
                   return page_number
                else:
                    page_number += 1
                time.sleep(self.get_sleep_time())


      def get_Topic_page_count(self, url):
          soup = BeautifulSoup(urlopen(url), 'lxml')
          last_page_bullet = soup.find('li', {'class': 'pager-last last'}).text
          if last_page_bullet is not None:
             return int(last_page_bullet)
          return 1
      
      def getSections(self):
          soup = BeautifulSoup(urlopen('https://www.vauva.fi/keskustelu/alue/aihe_vapaa'), 'lxml')
          MainMenu = soup.find('div', class_='discussion-sections-list')
   
          for SubMenu in MainMenu.find('ul').find_all('li'):
              title = SubMenu.find('a').text
              link = SubMenu.find('a')['href']
              self.Sections[title] = {'link':self.BASE_URL+link, 'Discussions':{}}
      
      def getTopic(self,url):
          soup = BeautifulSoup(urlopen(url), 'lxml')
          html = soup.find('article', class_=re.compile('^node node-discussion-topic'))
          Topic = {'title':html.find('h3', class_='comment-title').text.strip()}
          
          S = html.find('div', class_='sanoma-comment')
          Topic['user'] = S.find('div', class_='wrapper').text.strip()
          Topic['time'] = S.find('div', class_='field-item even').text.strip()
          Topic['text'] = S.find('p').get_text().strip()
          
          rate  = S.find('div', class_=re.compile('^rate-node'))
          Topic['up'] = rate.find('li', class_='first').find('span', class_='rate-voting-count').text
          Topic['down'] = rate.find('li', class_='last').find('span', class_='rate-voting-count').text
          Topic['Discussion'] = []
          
          NB_pages = self.get_Topic_page_count(url)
          for page_number in range(1,NB_pages+1):
              html = BeautifulSoup(urlopen(url+'?page='+str(page_number)), 'lxml')
              Comments = html.find('div', class_='comments-list-wrapper')
              for article in Comments.find_all('article'):
                  if article.find('blockquote') != None:
                     article.find('blockquote').decompose()
                  Comment = {}
                  Comment['user'] = article.find('div', class_='top').find('span', class_='username-wrapper').text.strip()
                  Time = article.find('div', class_='top').find('div', class_= re.compile('^field field-name-post-date')).text.strip()
                  Comment['time'] = datetime.strptime(Time, 'klo %H:%M | %d.%m.%Y')
                  Comment['text'] = article.find('div', class_='middle clearfix').text.strip()

                  Topic['Discussion'].append(Comment)
              time.sleep(self.get_sleep_time())
          return Topic
                
      def getTopics(self,url):
          Topics = []
          soup = BeautifulSoup(urlopen(url), 'lxml')
          Table = soup.find('div', class_='region main').find('div',class_='view-content ds-view-content')
          for row in Table.find_all('div', class_=re.compile("^row odd" or "^row even")):
              print('\n___________________________')
              link = self.BASE_URL+row.find('a')['href']
              print(link)
              Topics.append(self.getTopic(link))
          return Topics
      
def Scraping():
    
    D = Debate()
    D.getSections()
    return D.Sections
#    Topics = D.getTopics('https://www.vauva.fi/keskustelu/alue/aihe_vapaa')
#    return Topics

Topics = Scraping()