#!/bin/python3
import sys
import copy

from ag import *
from ab import *
from ab2g import *

a=goal()
b=goal()
a.add(1)
b.add(1)
print(a==b)
#print(a==0) raise err
a.fromTxt(sys.argv[0])
print(a.constraints)
'''
0 asd
0 0
  0 asd
	0 0
0
a
#
//
;
'''

del a,b
txt=goal()
bg=board((3,3))
bg.setDontcare(atHere=[4,5,7,8],excludeEmpty=False)
bgg=b2g(bg,emptyAsGoal=False)
print('bgg',bgg.constraints)
b=board((3,3))
b.print()
'''
0 0
1 1
2 2
3 3
6 6
'''
txt.fromTxt(sys.argv[0])
tmp=txt.constraints[-5:]
txt.constraints=tmp
del tmp
print('txt',txt)
from pprint import pprint
print('match b:txt',matchGoal(b,txt))
print('match bg:txt',matchGoal(bg,txt))
print('match b:bgg',matchGoal(b,bgg))

xxx=goaltree()
xxx.fromTxt("ainputtest.txt")
print(xxx)

