#!/bin/python3
import sys
import copy

from ag import *
from ab import *
from ab2g import *

xxx=goaltree()
xxx.fromTxt("ainput-8puzzle-2.txt")
print(xxx)
print("toStr")
print(xxx.toStr())
print("#end")
bbb=board((3,3))
print("bd"),bbb.print()
keys=matchGoaltree(bbb,xxx)
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
		print(bbb.solvable())
		bbb.print()
		genSol(bbb,xxx,step=8)
		print()
	exit()

print("board.random()")
bbb.random()
while bbb.solvable()==False: bbb.random()
bbb.print()
genSol(bbb,xxx,step=8)

