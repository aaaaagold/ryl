#!/bin/python3
import sys
import copy
import time

from ag import *
from attt import *

xxx=goaltree()
xxx.fromTxt("ainput-ttt/main-first.txt")
print(xxx)
print("toStr")
xxxtxt=xxx.toStr()
xxx.fromStr(xxxtxt,cd='ainput-ttt/')
print(xxx.toStr())
print("#end")
print("finals:",xxx.getFinals())
print("size:",xxx.size())
exit()
bbb=ttt()
if 0==0:
	pass
# TODO 

if 0!=0:
	notSolved=[
	]
	print("notSolved")
	for i in range(len(notSolved)):
		arr=notSolved[i]
		bbb.setNums(arr,arr.index(15))
		print(i,bbb.solvable())
		t0=time.time()
		res=genSol(bbb,xxx,step=8)
		print(time.time()-t0)
		movesS=res['moves']
		nodesS=res['nodes']
		if len(movesS)==0:
			bbb.print()
			res=genSol(bbb,xxx,step=8,verbose=True)
			movesS=res['moves']
			nodesS=res['nodes']
		else:
			print(movesS)
			print(nodesS)
		print(i)
		print()
else:
	step=int(sys.argv[1]) if len(sys.argv)>1 and sys.argv[1].isdigit() else 8
	stateLimit=int(sys.argv[2]) if len(sys.argv)>2 and sys.argv[2].isdigit() else 4095
	print("need appearing 'goal!'."+
		("  %s=%s"%("step",str(step)))+
		("  %s=%s"%("stateLimit",str(stateLimit)))
		)
	while 0==0:
		print("board.random()")
		bbb.random()
		while bbb.solvable()==False: bbb.random()
		bbb.print()
		print(bbb.rawBoard())
		t0=time.time()
		res=genSol(bbb,xxx,step=step,stateLimit=stateLimit)
		print(time.time()-t0)
		if len(res['moves'])==0:
			res=genSol(bbb,xxx,step=step,stateLimit=stateLimit,verbose=True)
			print(bbb.rawBoard())
			break
		elif 0!=0:
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

