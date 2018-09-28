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
print("finals:",xxx.getFinals())
bbb=board((3,3))
# TODO 

if 0!=0:
	notSolved=[
		[1,6,3,5,8,2,7,0,4],
	]
	for arr in notSolved:
		print("notSolved")
		bbb.setNums(arr,arr.index(8))
		print(bbb.solvable())
		bbb.print()
		genSol(bbb,xxx,step=8)
		print()
else:
	print("board.random()")
	bbb.random()
	while bbb.solvable()==False: bbb.random()
	bbb.print()
	genSol(bbb,xxx,step=8)

