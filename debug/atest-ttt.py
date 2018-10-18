#!/bin/python3
import sys
import copy
import time

from ag import *
from ab2g import *
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
bbb=ttt()
if 0==0:
	step=3
	stateLimit=4095
	p=re.compile("^[ \t]*(q|quit|exit|[0-8])[ \t]*$")
	bbb.print()
	print("q to end")
	print("loc(0..8)")
	bye=False
	while bye==False:
		res=genSol(bbb,xxx,step=step,stateLimit=stateLimit,verbose=True)
		moves=res['moves'] if len(res['moves'])!=0 else res['possible']
		print(moves)
		move=res['possible'][0][0] if len(moves)==0 else moves[0][0]
		bbb.move(move)
		while bye==False:
			bbb.print()
			print(bbb.turn())
			try:
				res=input("> ")
			except EOFError:
				bye=True
			m=p.match(res)
			if isNone(m): continue
			s=m.group(0)
			if not s.isdigit():
				bye=True
			elif bbb.move((None,int(s)))==False:
				break
	pass
	exit()
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

