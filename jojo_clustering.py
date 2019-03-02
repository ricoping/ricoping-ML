import os, mecabing, re, clusters, bs4, requests, shelve
from pprint import pprint

# ATTENTION: 'SS' is half-width, others are full-width.
def alpha2degit(alphabet):
	if 'SS' in alphabet:
		return 7.0
	elif 'Ｓ' in alphabet:
		return 6.0
	elif 'Ａ' in alphabet:
		return 5.0
	elif 'Ｂ' in alphabet:
		return 4.0
	elif 'Ｃ' in alphabet:
		return 3.0
	elif 'Ｄ' in alphabet:
		return 2.0
	elif 'Ｅ' in alphabet:
		return 1.0

def degit_filter(d):
	new_d = {}
	new_d["name"] = d["name"]
	for status in [x for x in d.keys() if not x == "name"]:
		new_d[status] = alpha2degit(d[status])
	return new_d

def categorize_result(kclust):
	for i in range(len(kclust)):
		print("\nカテゴリー: " + str(i+1) + "\n")
		print(", ".join([standnames[r] for r in kclust[i]]))


url = "http://www.geocities.co.jp/AnimeComic-Pastel/2053/stand.html"

response = requests.get(url)
response.encoding = response.apparent_encoding
response.raise_for_status()
source = response.text

#geocities service is going to end 2019/3/31. In that case, use source code though it's a secret...
#source = shelve.open("source")["source"]

sp = bs4.BeautifulSoup(source,"html.parser")
tables = sp.select('table')

data = []
for table in tables[1:]:
	d = {}
	trs = table.select('tr')
	if trs[0]["bgcolor"] == "white":
		continue

	d["name"] = trs[0].text

	stand_type = trs[1].select("td")[0].text

	status1_td = trs[2].select("td")
	status1 = [status1_td[1].text, status1_td[3].text, status1_td[5].text,]
	d["power"] = status1[0]
	d["speed"] = status1[1]
	d["defense"] = status1[2]

	status2_td = trs[3].select("td")
	status2 = [status2_td[1].text, status2_td[3].text, status2_td[5].text,]

	d["endurance"] = status2[0]
	d["technique"] = status2[1]
	d["flexibility"] = status2[2]

	data.append(d)

final_data = [x for x in filter(lambda d: "レクイエム" not in d["name"], map(degit_filter, data))]

f = open("jojodata.txt", "w")
fields = "|||".join([key for key in final_data[0].keys() if not key == "name"])

rows = "\n".join([d["name"] + "|||" + "|||".join([str(v) for v in d.values() if type(v) is float]) for d in final_data])

f.write(fields + "\n" + rows);f.close()

standnames, words, data = clusters.readfile("jojodata.txt")
kclust = clusters.kcluster(data, k=3)

print(categorize_result(kclust))
