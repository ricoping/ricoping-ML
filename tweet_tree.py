import shelve, pprint, re, numpredict
sh = shelve.open("tw_data")

tagReg=re.compile(r"<[^>]*?>")
hashReg=re.compile(r"#\w+")
kanjiReg=re.compile(r"[\u4E00-\u9FD0]")
kanaReg=re.compile(r'[あ-んア-ン一]')

tweet_data = sh['politics'] + sh['economy'] + sh['world']
tree_data = []
for d in tweet_data:
	rt=d["tl_rt_div"]
	fav=d["tl_fav_div"]
	rep_size=len(d["replies"])
	text_body=tagReg.sub("", d["text_body"])
	hash_size=len(hashReg.findall(text_body))
	has_img="yes" if "pic.twitter.com" in text_body else "no"

	kanji_size=len(kanjiReg.findall(text_body))
	hiragana_size=len(kanaReg.findall(text_body))
	
	try:
		kana_ratio=hiragana_size/(kanji_size+hiragana_size)
	except:
		kana_ratio=0

	row=[round(kana_ratio, 5), has_img, fav]

	tree_data.append(row)


def fav2genre(d):
	d[-1]="BUZZ!" if d[-1] > 10000 else "not buzz"
	d[0]=round(d[0]*10, 0)
	return d

tree_data = [td for td in map(fav2genre, tree_data)]

tree=numpredict.buildtree(tree_data)
#numpredict.prune(tree, 0.4)
numpredict.drawtree(tree, jpeg="tweettree.jpg")
