#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess, os, pprint, re, copy, math, sqlite3

def mecab(sentence):
	sentence = sentence.strip().replace("\n", "").replace("\t", "")
	sentence = sentence.replace(" ", "").replace("　", "")
	sentence = sentence.replace("(", "").replace(")", "")
	path = os.path.dirname(os.path.abspath(__file__))
	command = path + "/mecabing.bash" + " " + sentence
	proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
	mecabed = proc.stdout.read().decode()
	#mecabed = unicode(proc.stdout.read(), 'utf-8')
	return mecabed

def mecab2obj(sentence):
	"""MECAB RESULT"""
	data = []
	mecabed = mecab(sentence)
	for mcb in mecabed.split("\n"):
		"""ONE DATA"""
		mcb = mcb.replace("\t", ",")
		mcb_split = mcb.split(",")
		if len(mcb_split) > 1:
			datum = {}
			word = mcb_split[0]
			attr1 = mcb_split[1]
			attr2 = mcb_split[2]
			datum["word"] = word
			datum["attr1"] = attr1
			datum["attr2"] = attr2

			is_counted = False

			if not data:
				datum["count"] = 1

			for d in data:
				if d["word"] == word and d["attr1"] == attr1 and d["attr2"] == attr2:
					d["count"] = d["count"] + 1
					is_counted = True
					continue
				else:
					datum["count"] = 1
			if not is_counted:
				data.append(datum)
	for datum in data:
		pattern = re.compile("^(、|。|　|「|」|（|）|・)$")
		if pattern.match(datum["word"]):
			data.remove(datum)

		#if "助詞" in datum["attr1"]:
		#	data.remove(datum)
		#elif datum["attr2"] == "句点":
		#	data.remove(datum)
	sorted_data = sorted(data, key=lambda x: x["count"], reverse=True)
	return sorted_data


def tf(doc):
	data = mecab2obj(doc)
	freq_sum = 0
	for d in data:
		freq_sum = freq_sum + d["count"]
	for d in data:
		d["tf"] = float(d["count"])/freq_sum
	return data


def has_word(word, doc):
	data = mecab2obj(doc)
	for d in data:
		if d["word"] in word:
			return True
	return False


def tf_idf(docs_list):
	docs_N = len(docs_list)
	data_list = []
	doc_id = 1
	for doc in docs_list:
		datum = {}
		datum["id"] = doc_id
		datum["doc"] = doc
		datum["meta"] = tf(doc)
		doc_id = doc_id + 1
		data_list.append(datum)

	data_clone = copy.deepcopy(data_list)
	for datum in data_list:
		meta = datum["meta"]
		for m in meta:
			for d in data_clone:
				if has_word(m["word"], d["doc"]):
					if "doc_count" in m:
						m["doc_count"] = m["doc_count"] + 1
					else:
						m["doc_count"] = 1

	for datum in data_list:
		for m in datum["meta"]:
			if "doc_count" in m:
				each_idf = math.log(float(docs_N)/m["doc_count"] )
				m["idf"] = each_idf
				m["tf_idf"] = m["tf"] * m["idf"]
	return data_list


def tf_idf_sql(docs_list):
	docs_N = len(docs_list)
	conn = sqlite3.connect('mecabing.db')
	c = conn.cursor()
	for doc in docs_list:
		insert_doc = (doc,)
		c.execute('INSERT INTO mecabing_docs ("doc") VALUES (?)', insert_doc)
		conn.commit()
		last_doc_id = c.lastrowid
		data = tf(doc)
		for datum in data:
			insert_meta = (last_doc_id, datum["word"], datum["attr1"], datum["attr2"], datum["count"], datum["tf"], None, None, None)
			c.execute('INSERT INTO mecabing_meta VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', insert_meta)
			conn.commit()

	c.execute("SELECT * FROM mecabing_docs")
	doc_rows = c.fetchall()
	for doc_row in doc_rows:
		doc_N = len(doc_rows)
		c.execute("SELECT * FROM mecabing_meta WHERE doc_id=?", (doc_row[0],))
		meta_rows = c.fetchall()
		for meta_row in meta_rows:
			cm = conn.cursor()
			cm.execute('SELECT * FROM mecabing_meta WHERE word=? AND attr1=? AND attr2=?', (meta_row[1], meta_row[2], meta_row[3]))
			duplicates = cm.fetchall()
			dup_num = len(duplicates)
			for dup in duplicates:
				cm.execute("UPDATE mecabing_meta SET doc_count=? WHERE word=? AND attr1=? AND attr2=?", (dup_num, meta_row[1], meta_row[2], meta_row[3]))
				conn.commit()

			cm.execute('SELECT * FROM mecabing_meta WHERE word=? AND attr1=? AND attr2=?', (meta_row[1], meta_row[2], meta_row[3]))
			duplicates = cm.fetchall()
			for dup in duplicates:
				dup_doc_count = dup[6]
				dup_idf = math.log(float(doc_N)/dup_doc_count)
				dup_tf_idf = dup[5] * dup_idf
				cm.execute("UPDATE mecabing_meta SET idf=?, tf_idf=? WHERE word=? AND attr1=? AND attr2=?", (dup_idf, dup_tf_idf, meta_row[1], meta_row[2], meta_row[3]))
				conn.commit()
			
	conn.close()

#tf_idf_sql([sentence, sentence2])
#data_result = tf_idf([sentence, sentence2])

#pprint.pprint(data_result)

#pprint.pprint(mecab2obj(sentence))



