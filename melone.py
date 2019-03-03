import codecs
import clusters,random
import shelve
sh = shelve.open("melone_data")
standnames, words, data = clusters.readfile("jojodata.txt")
datasize=len(data)
sh["standnames"]=standnames
sh["words"]=words
sh["data"]=data

tmpvec=[]

def geneticoptimize(costf,popsize=50,\
					mutprob=0.3,elite=0.3,maxiter=100):
	def mutate(vec):
		j=random.randint(1,len(vec)-1)
		except_vec=[y for y in filter(lambda x: x not in vec,[x for x in range(datasize)])]
		new_dna=random.sample(except_vec, j)

		return new_dna+vec[j:]

	def crossover(r1,r2):
		i=random.randint(1,datasize-2)
		result=r1[0:i]+r2[i:]
		while len(set(result))!=5:
			result=r1[0:i]+r2[i:]
			print(result)
		return result

	pop=[]
	for i in range(popsize):
		vec=random.sample(range(datasize), k=5)
		pop.append(vec)

	topelite=int(elite*popsize)
	for i in range(maxiter):
		scores=[(costf(v),v) for v in pop]
		scores.sort()
		ranked=[v for (s,v) in scores]

		pop=ranked[0:topelite]

		while len(pop)<popsize:
			if random.random()<mutprob:
				c=random.randint(0,topelite)
				pop.append(mutate(ranked[c]))
			else:
				c1=random.randint(0,topelite)
				c2=random.randint(0,topelite)
				pop.append(crossover(ranked[c1],ranked[c2]))

		print("score",scores[0][0])
		tmpvec.append(scores[0][1])
	return (scores[0][1], tmpvec)


def stand_cost(standids):
	field=0; totalvar=0
	for col in [[data[j][i] for j in standids] for i in range(6)]:

		avg=sum(col)/len(col)
		var=sum([pow((x - avg),2) for x in col])/len(col)
		totalvar+=var

	totalavg=sum([sum(data[i])/len(data[i]) for i in standids])

	print("TOTAL VARIANCE: ", totalvar)
	print("TOTAL AVERAGE: ", totalavg)

	return 100 + totalvar - totalavg*0.4

def printresult(vec):
	print(words)
	for standid in vec:
		print(standnames[standid],data[standid])
	print("COST: " + str(stand_cost(vec)))

standids=random.sample(range(datasize), k=5)

gene=geneticoptimize(stand_cost)
s=gene[0]
printresult(s)
print(s)

sh["tmpvec"]=tmpvec
sh.close()
