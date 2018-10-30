#!/bin/python3
import sys
import copy

from ag import *
from ab import *
#from ab2g import *
from asol import *

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

try:
	xxx=goaltree()
	xxx.fromTxt("ainputtest.txt")
	print(xxx)
except Exception as inst:
	print(inst)

print()
xxx=goaltree()
xxx.fromTxt("ainput-8puzzle.txt")
print(xxx)
print("toStr")
print(xxx.toStr())
print("#end")
bbb=board((3,3))
print("bd"),bbb.print()
keys=matchGoaltree(b,xxx)
print("matches:",keys)
print("finals:",xxx.getFinals())
# TODO 

if 0==0:
	notSolved=[
		[8,4,2,6,5,0,1,7,3],
		[1,3,6,5,4,0,2,8,7],
		[2,3,4,1,7,0,8,5,6],
	]
	for arr in notSolved:
		print("notSolved")
		bbb.setNums(arr,arr.index(8))
		bbb.print()
		genSol(bbb,xxx,step=8)
		print()

print("board.random()")
bbb.random()
while bbb.solvable()==False: bbb.random()
bbb.print()
genSol(bbb,xxx,step=8)

