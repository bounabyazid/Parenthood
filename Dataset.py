#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#cd /home/polo/.local/lib/python3.6/site-packages
"""
Created on Wed Feb 27 04:46:24 2020

@author: Yazid BOUNAB
"""
import re
import os
import spacy
import pickle

from Birth import Birth
from pprint import pprint

from wordcloud import WordCloud
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize

from senti_client import sentistrength

senti = sentistrength('EN')

def Senti_List(List):
    Score = []
    for label in List:
        res = senti.get_sentiment(label)
        Score.append(res['neutral'])
    
    pickle_out = open("BirthDataset Sentiments.pkl","wb")
    pickle.dump(Score, pickle_out)
    pickle_out.close()
     
    return Score

def MergeTextFiles(FolderName, FileName):
    filenames = sorted(list(set([f for f in os.listdir(FolderName) if f.endswith('.txt')])))
    print(filenames)
    with open(FileName+'.txt', 'w') as outfile: 
         for name in filenames: 
             with open(FolderName+'/'+name) as infile: 
                  outfile.write(infile.read()) 
                  outfile.write("\n")

def Dict2List(Dataset, keys = []):
    List = []
    
    for Topic in Dataset:
        for key in keys:
            if isinstance(Topic[key], list):
               List.extend(Topic[key])
            else:
                List.append(Topic[key])
    return List

def List_Punctuations(text):
    text = re.sub('[A-Za-z]|[0-9]|[\n\t]|[£€$%& ]','',text)
    SymbList = list(dict.fromkeys(text).keys())
    return SymbList

def CLeanDataset(FileName):
    with open(FileName+'/'+FileName+' ENG.txt','r') as f:
         Texts = f.read()
    'https://github.com/yoonkim/CNN_sentence/blob/master/process_data.py'
    'https://note.nkmk.me/en/python-str-replace-translate-re-sub/'
    
    Texts = re.sub('(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-?=%.]+', ' ', Texts)
    Texts = re.sub(r'[\w\.-]+@[\w\.-]+', ' ', Texts)
    Texts = re.sub(r'\n\n', '\n', Texts)

    print('Done ...')    
    with open(FileName+'/Clean_'+FileName+'.txt', "w") as outfile:
         outfile.write(Texts)   

def Text2NER(FileName):
    with open(FileName+'/Clean_'+FileName+'.txt','r') as f:
         lines = f.readlines()
         
    Dataset_NER = {}
    nlp =spacy.load('en_core_web_sm')
    
    for line in lines:
        doc = nlp(line.strip())
        for ent in doc.ents:
            if not ent.label_ in Dataset_NER.keys():
               Dataset_NER[ent.label_] = [ent.text]
            else:
                Dataset_NER[ent.label_].append(ent.text)
                           
    pickle_out = open('Dataset'+FileName+' NER.pkl','wb')
    pickle.dump(Dataset_NER, pickle_out)
    pickle_out.close()
     
    return Dataset_NER

def Dataset2Pickle():
    #with open('Dataset ENG.txt','r') as f:
    #     Texts = f.read()
    #re.sub(r'Title ____', 'Title____', Texts)
    #re.sub(r'____ Title', '____Title', Texts)
    #re.sub('Text ____', 'Text____', Texts)
    #re.sub('____ Text', '____Text', Texts)
    #re.sub(r'____Item____\n', '____Item____', Texts)
    
    with open('Dataset.txt','r') as f:
         lines = f.readlines()
         
    Dataset = []
    Topic = {}
    for line in lines:
        if 'Title____' in line:
           if Topic:
              Dataset.append(Topic)
           Topic = {}
           Topic['Title'] = re.sub('Title____|____Title', '', line).strip()
           Topic['Text'] = ''
           Topic['Comments'] = []
        if 'Text____' in line:
           Topic['Text'] = re.sub('Text____|____Text', '', line).strip()
        if '____Item____' in line:
           Topic['Comments'].append(re.sub('____Item____', '', line).strip())
    pickle_out = open("Dataset.pkl","wb")
    pickle.dump(Dataset, pickle_out)
    pickle_out.close()
     
    return Dataset

def NER():
    Dataset_NER = {}
    nlp =spacy.load('en_core_web_sm')

    pickle_in = open('Dataset.pkl',"rb")
    Dataset = pickle.load(pickle_in)
    
    for Topic in Dataset:
        Texts = Topic['Title']+Topic['Text']
        if len(Topic['Comments']) > 0:
           Texts += '\n'.join(comment for comment in Topic['Comments'])
        
        doc = nlp(Texts)
        for ent in doc.ents:
            if not ent.label_ in Dataset_NER.keys():
               Dataset_NER[ent.label_] = [ent.text]
            else:
                Dataset_NER[ent.label_].append(ent.text)
    pickle_out = open("Dataset NER.pkl","wb")
    pickle.dump(Dataset_NER, pickle_out)
    pickle_out.close()
    return Dataset_NER

def BirthDataset():
    with open('Vauva/Clean_Vauva.txt','r') as f:
         Dataset = f.readlines()

    BirthDataset = []
    for line in Dataset:
        if any(keyword in line for keyword in Birth):
           BirthDataset.append(line)
    
    pickle_out = open("BirthDataset.pkl","wb")
    pickle.dump(BirthDataset, pickle_out)
    pickle_out.close()
    
    return BirthDataset

def NER(BirthDataset):
    BirthDataset_NER = {}
    nlp =spacy.load('en_core_web_sm')
    Sentences = []
    for Topic in BirthDataset:
        Sentences.append(Topic['Title'])
        Sentences.append(Topic['Text'])
        if len(Topic['Comments']) > 0:
           Sentences.extend(Topic['Comments'])
    for sentence in Sentences:  
        doc = nlp(sentence)
        for ent in doc.ents:
            if not ent.label_ in BirthDataset_NER.keys():
               BirthDataset_NER[ent.label_] = [ent.text]
            else:
                BirthDataset_NER[ent.label_].append(ent.text)
    pickle_out = open("BirthDataset NER.pkl","wb")
    pickle.dump(BirthDataset_NER, pickle_out)
    pickle_out.close()
    return BirthDataset_NER

def NER_Birth():
    pickle_in = open('BirthDataset Sentiments.pkl',"rb")
    Sentiments = pickle.load(pickle_in)

    Pos_BirthDataset_NER = {}
    Neg_BirthDataset_NER = {}
    nlp =spacy.load('en_core_web_sm')
    Sentences = []
    Birth_Pos_Sentences = []
    Birth_Neg_Sentences = []

    for Topic in BirthDataset:
        Sentences.append(Topic['Title'])
        Sentences.append(Topic['Text'])
        if len(Topic['Comments']) > 0:
           Sentences.extend(Topic['Comments'])
    for i in range(0, len(Sentences)):  
        doc = nlp(Sentences[i])
        if int(Sentiments[i]) > 0:
           Birth_Pos_Sentences.append(Sentences[i])
           for ent in doc.ents:
               if not ent.label_ in Pos_BirthDataset_NER.keys():
                  Pos_BirthDataset_NER[ent.label_] = [ent.text]
               else:
                   Pos_BirthDataset_NER[ent.label_].append(ent.text)
        if int(Sentiments[i]) < 0:
           Birth_Neg_Sentences.append(Sentences[i])
           for ent in doc.ents:
               if not ent.label_ in Neg_BirthDataset_NER.keys():
                  Neg_BirthDataset_NER[ent.label_] = [ent.text]
               else:
                    Neg_BirthDataset_NER[ent.label_].append(ent.text)

    pickle_out = open("Pos BirthDataset NER.pkl","wb")
    pickle.dump(Pos_BirthDataset_NER, pickle_out)
    pickle_out.close()

    pickle_out = open("Neg BirthDataset NER.pkl","wb")
    pickle.dump(Neg_BirthDataset_NER, pickle_out)
    pickle_out.close()
    
    return Pos_BirthDataset_NER, Neg_BirthDataset_NER, Birth_Pos_Sentences, Birth_Neg_Sentences

def BirthDataset_Sentences():
    pickle_in = open('BirthDataset Sentiments.pkl',"rb")
    Sentiments = pickle.load(pickle_in)
    
    pickle_in = open('BirthDataset.pkl',"rb")
    Sentences = pickle.load(pickle_in)

    Birth_Pos_Sentences = []
    Birth_Neg_Sentences = []

    for i in range(0, len(Sentences)): 
        if len(Sentences[i].split()) > 1:
           if int(Sentiments[i]) > 0:
              Birth_Pos_Sentences.append(Sentences[i])
           if int(Sentiments[i]) < 0:
              Birth_Neg_Sentences.append(Sentences[i])
    
    pickle_out = open("Pos BirthDataset Sentences.pkl","wb")
    pickle.dump(Birth_Pos_Sentences, pickle_out)
    pickle_out.close()

    pickle_out = open("Neg BirthDataset Sentences.pkl","wb")
    pickle.dump(Birth_Neg_Sentences, pickle_out)
    pickle_out.close()
    
    return Birth_Pos_Sentences, Birth_Neg_Sentences


def ParseTree():
    nlp =spacy.load('en_core_web_sm')

    pickle_in = open('Pos BirthDataset Sentences.pkl',"rb")
    Birth_Pos_Sentences = pickle.load(pickle_in)

    pickle_in = open('Neg BirthDataset Sentences.pkl',"rb")
    Birth_Neg_Sentences = pickle.load(pickle_in)
    polo = []
    Pos_Relations = []
    for Sentence in Birth_Pos_Sentences:
        ADJ_NOUN = []
        doc = nlp(Sentence)
        for token in doc:
            if token.pos_ == ('ADJ' or 'INTJ'):
               polo.append((token.head.text, token.head.pos_))  
               ADJ_NOUN.append((token.text, token.head.text, token.head.pos_, Sentence))
        Pos_Relations.append(ADJ_NOUN)
    
    Neg_Relations = []
    for Sentence in Birth_Neg_Sentences:
        ADJ_NOUN = []
        doc = nlp(Sentence)
        for token in doc:
            if token.pos_ == 'ADJ':
               ADJ_NOUN.append((token.text, token.head.text))
        Neg_Relations.append(ADJ_NOUN)
        
    pickle_out = open("Pos BirthDataset Relations.pkl","wb")
    pickle.dump(Pos_Relations, pickle_out)
    pickle_out.close()    

    pickle_out = open("Neg BirthDataset Relations.pkl","wb")
    pickle.dump(Neg_Relations, pickle_out)
    pickle_out.close()    
    
    return Pos_Relations, Neg_Relations, polo

#________________Main Part____________________

#CLeanDataset('Vauva')
#Dataset_NER = Text2NER('Vauva')
    
with open('Vauva/Clean_Vauva.txt','r') as f:
     lines = f.readlines()
Sentences = []     
for line in lines:
    if len(line) > 0:
       Sentences.append(line)

pickle_out = open("Dataset.pkl","wb")
pickle.dump(lines, pickle_out)
pickle_out.close()    

Sentiments = Senti_List(Sentences)
     
#Sentiments = Senti_List(lines)

#BirthDataset = BirthDataset()
#Sentiments = Senti_List(BirthDataset)

#BirthDataset_NER = NER(BirthDataset())

#Birth_Pos_Sentences, Birth_Neg_Sentences = BirthDataset_Sentences()
#Pos_Relations, Neg_Relations, polo = ParseTree()

#List = Dict2List(BirthDataset(), keys=['Title', 'Text', 'Comments'])
#Sentiments = Senti_List(List)

#CLeanDataset()
#Dataset = Dataset2Pickle()
#Dataset_NER = NER()
#BirthDataset = BirthDataset()