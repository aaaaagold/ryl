#!/bin/python3
import sys
import copy
import time

from ag import *
from ab import *
from ab2g import *

xxx=goaltree()
xxx.fromTxt("ainput-15p/main.txt")
#print(xxx)
print("toStr")
xxxtxt=xxx.toStr()
xxx.fromStr(xxxtxt,cd='ainput-15p/')
#print(xxx.toStr())
print("#end")
print("finals:",xxx.getFinals())
print("size:",xxx.size())
bbb=board((4,4))
if 0==0:
	pass
# TODO 

if 0!=0:
	notSolved=[
		#[15, 5, 10, 12, 1, 6, 11, 8, 4, 2, 9, 7, 3, 0, 13, 14],
		#[2, 12, 13, 5, 9, 14, 6, 1, 11, 8, 4, 7, 15, 0, 10, 3],
		#[0, 14, 3, 15, 12, 13, 9, 5, 8, 6, 11, 10, 7, 1, 2, 4],
		#[15, 14, 4, 2, 1, 12, 6, 10, 5, 0, 9, 3, 8, 13, 7, 11],
		#[11, 15, 2, 13, 12, 1, 6, 3, 0, 14, 9, 10, 4, 5, 8, 7],
		#[5, 11, 6, 0, 12, 3, 8, 2, 10, 1, 15, 9, 4, 7, 13, 14],
		#[15, 9, 2, 10, 3, 12, 1, 13, 4, 14, 11, 8, 5, 7, 6, 0],
		#[0,1,11,13,4,14,6,10,12,2,8,15,9,3,5,7],
		#[0,1,2,3,4,8,15,12,6,9,14,7,10,11,5,13],
		#[0,1,15,2,4,12,7,10,11,14,9,6,5,8,13,3],
		#[0,1,15,12,4,14,13,7,11,6,9,10,8,2,5,3],
		#[0,1,8,7,4,3,5,13,15,11,2,9,6,14,12,10],
		#[6, 5, 10, 4, 2, 0, 8, 11, 12, 9, 13, 3, 1, 15, 14, 7],
		#[0, 12, 8, 3, 2, 7, 4, 15, 6, 5, 11, 1, 14, 10, 9, 13],
		#[13, 2, 5, 4, 0, 8, 14, 6, 7, 11, 3, 10, 1, 15, 12, 9],
		#[5, 10, 9, 12, 0, 6, 8, 1, 2, 4, 3, 15, 7, 13, 14, 11],
		#[12, 15, 6, 9, 13, 3, 5, 7, 10, 4, 14, 11, 2, 8, 1, 0],
		#[9, 5, 10, 12, 0, 2, 14, 13, 4, 11, 15, 1, 8, 3, 6, 7],
		#[15, 7, 11, 5, 2, 6, 9, 12, 1, 13, 4, 10, 14, 8, 0, 3],
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
