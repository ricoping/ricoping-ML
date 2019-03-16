#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, mecabing, re, clusters
from pprint import pprint

rows = []
word_list = []
word_list.append("LIVEDOOR NEWS")
genre="it-life-hack/"
all_data = os.listdir(genre)[:400]
size = len(all_data)
print(size)

skip = 0
for file in all_data:
	try:
		f = open(genre+file);text = f.read();f.close()
		text = re.sub(r'(https?|ftp)(:\/\/[-_\.!~*\'()a-zA-Z0-9;\/?:\@&=\+\$,%#]+)', '', text)
		text = text.replace("\n", "。")
		text = re.sub(r'[!-/:-@[-`{-~\d]', '', text)
		text = text[3:]
		mecabed = mecabing.mecab2obj(text)

		row = {}
		row["TITLE"] = text[:60]
		for datum in mecabed:
			if not datum["word"] in word_list:
				word_list.append(datum["word"])

			row[datum["word"]] = datum["count"]

		rows.append(row)
	except:
		skip -= 1

size = size + skip
print(skip, size)
	#print(rows)

f = open("newsdata.txt", "w")
f.write("|||".join(word_list) + "\n")
for i in range(size):
	row = rows[i]

	last_row = []
	last_row.append(row["TITLE"])
	for word in word_list:
		if word in row:
			last_row.append(str(row[word]))
		else:
			last_row.append(str(0))
	f.write("|||".join(last_row) + "\n")

f.close()

# what's data :data.append([float(x) for x in p[1:]]) p:row
blognames, words, data = clusters.readfile("newsdata.txt")
clust = clusters.hcluster(data)

clusters.printclust(clust, labels=blognames) 
