#!/bin/python3
import sys
import copy
import time

from ag import *
from ambot import *
from asol import *

xxx=Goaltree()
fname=sys.argv[2]
xxx.fromTxt(fname)
xxxstr=xxx.toStr()
print(xxxstr)
print("finals:",xxx.getFinals())
print("size:",xxx.size())
bbb=mb()
if 0!=0 or (len(sys.argv)>1 and sys.argv[1]=="1demo"):
	it=3
	step=int(sys.argv[it]) if len(sys.argv)>it and sys.argv[it].isdigit() else 8
	t0=time.time()
	res=genSol_v3(bbb,xxx,step=step,stateLimit=4095,verbose=True)
	print(time.time()-t0)
	if len(res['moves'])==0:
		print("GG")
	else:
		movesS=res['moves']
		mml=min([len(mv) for mv in movesS])
		print(movesS,mml)
		for msg in res['mvSep'][0]:
			print("from-to")
			print(msg[0][0])
			print(msg[0][1])
			print()
			for m in msg[1]:
				move=m[1]
				print("move")
				print(move)
				print()
				bbb.move(move)
				print("board")
				bbb.print()
				print()
		print("move end")
		print()
		print(mml)
		for mv in movesS: print([x for m in mv for x in m[1]])
	pass
	exit()
