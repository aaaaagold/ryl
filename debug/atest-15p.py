#!/bin/python3
import sys
import copy

from ag import *
from ab import *
from ab2g import *

xxx=goaltree()
xxx.fromTxt("ainput-15p/main.txt")
print(xxx)
print("toStr")
xxxtxt=xxx.toStr()
xxx.fromStr(xxxtxt,cd='ainput-15p/')
print(xxx.toStr())
print("#end")
print("finals:",xxx.getFinals())
bbb=board((4,4))
if 0==0:
	pass
# TODO 

if 0!=0:
	notSolved=[
		#[0,1,11,13,4,14,6,10,12,2,8,15,9,3,5,7],
		#[0,1,2,3,4,8,15,12,6,9,14,7,10,11,5,13],
		#[0,1,15,2,4,12,7,10,11,14,9,6,5,8,13,3],
	]
	print("notSolved")
	for i in range(len(notSolved)):
		arr=notSolved[i]
		bbb.setNums(arr,arr.index(15))
		print(bbb.solvable())
		bbb.print()
		res=genSol(bbb,xxx,step=8,verbose=True)
		movesS=res['moves']
		nodesS=res['nodes']
		print(movesS)
		print(nodesS)
		print(i)
		print()
else:
	step=int(sys.argv[1]) if len(sys.argv)>1 and sys.argv[1].isdigit() else 8
	print("need appearing 'goal!'.  %s=%s"%("step",str(step)))
	print("board.random()")
	bbb.random()
	while bbb.solvable()==False: bbb.random()
	bbb.print()
	res=genSol(bbb,xxx,step=8,stateLimit=4095,verbose=True)
	movesS=res['moves']
	nodesS=res['nodes']
	print(nodesS)
	print(movesS)
	for i in range(len(nodesS)):
		moves=movesS[i]
		nodes=nodesS[i]
		print(nodes)
		print(moves)
		bbb.print()
		bbb.moveSeq(moves)
		print(len(moves))

