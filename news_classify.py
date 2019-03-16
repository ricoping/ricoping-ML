#!/usr/bin/env python
# -*- coding: utf-8 -*-
import docclass,mecabing,os,shelve,re,random
from pprint import pprint
sh=shelve.open("news_classify")


############ DATA

fc={}
cc={}

#Thanks----> https://hacknote.jp/archives/19937/
def cleaner(text):
	text=re.sub(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-…]+', "", text)
	text=re.sub('RT', "", text)
	text=re.sub('お気に入り', "", text)
	text=re.sub('まとめ', "", text)
	text=re.sub(r'[!-~]', "", text)
	text=re.sub(r'[︰-＠]', "", text)
	text=re.sub('\n', " ", text)
	text=text.replace("■","")
	return text
"""
for genre in ["it-life-hack/", "sports-watch/"]:
	for file in os.listdir(genre)[:300]:
		try:
			f=open(genre+file); text=f.read(); f.close()
			text=cleaner(text)
			for d in mecabing.mecab2obj(text[:3000]):
				word=d["word"]
				if len(word)<2: continue
				fc.setdefault(word,{})
				fc[word].setdefault(genre,0)
				fc[word][genre]+=1
				cc.setdefault(genre,0)
				cc[genre]+=1
		except:
			continue
sh["fc"]=fc; sh["cc"]=cc
"""

############### NAIVE BAYESIAN
fc=sh["fc"]; cc=sh["cc"]

def fcount(f,cat):
	if f in fc and cat in fc[f]:
		return float(fc[f][cat])

	return 0.0

def catcount(cat):
	if cat in cc:
		return float(cc[cat])
	return 0

totalcount=sum(cc.values())
categories=cc.keys()

def fprob(f, cat): #P(Fn|Cm)
	if catcount(cat)==0: return 0
	return fcount(f,cat)/catcount(cat)

init_weight=20.0; init_ap=1.5
def weightedprob(f,cat,prf):
	basicprob=prf(f,cat)
	totals=sum([fcount(f,c) for c in categories])

	bp=((weight*ap)+(totals*basicprob))/(weight+totals)
	return bp

def docprob(item, cat):
	p=1
	for f in [d["word"] for d in mecabing.mecab2obj(item)]:
		p*=weightedprob(f,cat,fprob)
	return p

def prob(item, cat): #P(C1|Fn) = P(C1)/P(Fn)P(Fn|C1)
	catprob=catcount(cat)/totalcount
	return docprob(item, cat)*catprob


def classify(item, default=None):
	probs={}; max_=0.0

	for cat in categories:
		probs[cat]=prob(item, cat)
		if probs[cat]>max_:
			max_=probs[cat]
			best=cat

	return best

def cost(results):
	return sum(results)/len(results)

###########OPTIMIZATION
"""
max_=0.0
for i in range(100):
	results=[]
	genre="sports-watch/"
	weight=init_weight+random.randint(-15,15)
	ap=init_ap+random.random()*random.sample([-1,1],1)[0]
	print("weight",weight,"ap",ap)
	for file in os.listdir(genre)[400:600]:
		f=open(genre+file); text=f.read(); f.close()
		classified=classify(cleaner(text))
		if classified==genre:
			results.append(1)
		else:
			results.append(0)
	cost_=cost(results)
	if cost_>max_:
		max_=cost_

print(max_*100,"%")
"""

#############CLASSIFICATION
#These are best!
weight=32.0; ap=1.080623651768369

for genre in ["it-life-hack/","sports-watch/"]:
	files=os.listdir(genre)[600:]
	print(genre+"に関する記事を" + str(len(files)) + "つ分類します")
	for file in files:
		try:
			results=[]
			f=open(genre+file); text=f.read(); f.close()
			classified=classify(cleaner(text))

			if classified==genre:
				results.append(1)
			else:
				results.append(0)
		except:
			continue

	print("正しく判別できた確率は",cost(results)*100,"%です！") 
