#!/bin/python3
import sys
import copy
import time

from ag import *
from amaze import *
from asol import *

filepairs=[
{"Goaltree":"ainput-maze/main.txt","maze":"ainput-maze/mazes/m-1-adjlist.txt"},
{"Goaltree":"ainput-maze/main-nowall.txt","maze":"ainput-maze/mazes/m-nowall-adjlist.txt"},
]
filepairsIt=0 if len(sys.argv)<2 else int(sys.argv[1])

xxx=Goaltree()
xxx.fromTxt(filepairs[filepairsIt]["Goaltree"])
learnDir="alearn-maze/"
#print(xxx)
#print("toStr")
#xxxtxt=xxx.toStr()
#xxx.fromStr(xxxtxt,cd='ainput-15p/')
#print(xxx.toStr())
print("#end")
print("finals:",xxx.getFinals())
print("size:",xxx.size())
bbb=maze().fromFile(filepairs[filepairsIt]["maze"])
if __name__=='__main__':
	bbb.random()
	#while bbb.solvable()==False: bbb.random()
	#arr=[0,0]
	#bbb.setBoard(arr)
	bbb.print()
	print(bbb.rawBoard())
	t0=time.time()
	res=genSol_v3(bbb,xxx,step=8,stateLimit=4095)
	print(time.time()-t0)
	if len(res['moves'])==0:
		print("GG")
	else:
		for k in res['nodes'][0]:
			print("goal")
			print(k)
			for g in xxx[k][0]:
				for c in g.constraints:
					print(("!=" if c[2] else "=="),c[1])
		print("goal\nEND")
		movesS=res['moves']
		print(movesS)
		nodesS=res['nodes']
		for msg in movesS[0]:
			print("msg")
			print(msg)
			move=msg[1]
			#time.sleep(0.25)
			bbb.move(move)
			print("board")
			bbb.print()
			print()
	pass
	exit()
