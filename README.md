# ricoping-ML
My tools for analyzing dairy life data.

## Requirements

- bs4
- requests

You also need to get *clusters.py* *numpredict.py* from https://github.com/arthur-e/Programming-Collective-Intelligence/tree/master/ and need to change *readfile* function to: 

~~~
def readfile(filename):
    lines = open(filename).readlines()
    colnames = lines[0].strip().split('|||')[1:]
    rownames = []
    data = []
    for line in lines[1:]:
        p = line.strip().split('|||')
        rownames.append(p[0])
        data.append([float(x) for x in p[1:]])
    return (rownames, colnames, data)
~~~


- *\t* and *\n* didn't work, so change "|||" (Actually I don't think this is best though.)
- You had better use python 3.x because many unicode problems occur.So you need to :
  - change all *print ""* to *print("")*
  - *lines = [line for line in file(filename)]* to just *open(filename).readlines()*
