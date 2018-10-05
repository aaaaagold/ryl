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
xxxtxt=xxx.toStr()
xxx.fromStr(xxxtxt)
print(xxx.toStr())
print("#end")
print("finals:",xxx.getFinals())
bbb=board((3,3))
if 0==0:
	def permutationAll(items):
		rg=range(len(items))
		rtv=[]
		def innerFoo(rtv,rtvitem,markedSelected):
			if not False in markedSelected:
				rtv.append([ i for i in rtvitem ])
			for i in rg:
				if markedSelected[i]: continue
				rtvitem.append(items[i])
				markedSelected[i]=True
				innerFoo(rtv,rtvitem,markedSelected)
				rtvitem.pop()
				markedSelected[i]=False
		innerFoo(rtv,[],[ False for _ in rg ])
		return rtv
	tmp=permutationAll([ x for x in range(9)])
	bd33all=[]
	for x in tmp:
		tmpbd=board((3,3))
		tmpbd.setNums(x,x.index(8))
		if tmpbd.solvable():
			bd33all.append(tmpbd)
	print(len(bd33all))
	#
	#
	for i in range(( int(sys.argv[1]) if len(sys.argv)>1 else 0 ),len(bd33all)):
		print(i,end='\r')
		bd=bd33all[i]
		res=genSol(bd,xxx,step=8,stateLimit=4095)
		movesS=res['moves']
		nodesS=res['nodes']
		if 0<len(movesS): pass
		else:
			bd.print()
			print(len(genSol(bd,xxx,step=8,stateLimit=65535,verbose=True)['moves']))
			print(bd.rawBoard())
			print(i)
			print()
	#
	exit()
# TODO 

if 0==0:
	notSolved=[
		[3,0,8,2,4,1,5,7,6],
		[1,6,8,5,7,3,0,2,4],
		[0, 1, 2, 8, 4, 3, 5, 7, 6],
	]
	for arr in notSolved:
		print("notSolved")
		bbb.setNums(arr,arr.index(8))
		print(bbb.solvable())
		bbb.print()
		res=genSol(bbb,xxx,step=8,verbose=True)
		print(res['moves'])
		print()
else:
	step=int(sys.argv[1]) if len(sys.argv)>1 and sys.argv[1].isdigit() else 8
	print("need appearing 'goal!'.  %s=%s"%("step",str(step)))
	print("board.random()")
	bbb.random()
	while bbb.solvable()==False: bbb.random()
	bbb.print()
	res=genSol(bbb,xxx,step=8,stateLimit=4095)
	movesS=res['moves']
	nodesS=res['nodes']
	print(nodesS)
	print(movesS)
	for i in range(len(nodesS)):
		moves=movesS[i]
		nodes=nodesS[i]
		print(nodes)
		print(moves)
		bbb.moveSeq(moves)

