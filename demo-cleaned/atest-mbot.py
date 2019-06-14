#!/bin/python3
import sys
import copy
import time

from ag import *
from ambot import *
from asol import *

xxx=Goaltree()
fname=sys.argv[2].replace("\\",'/')
xxx.fromTxt(fname)
xxxstr=xxx.toStr()
print(xxxstr)
print("finals:",xxx.getFinals())
print("size:",xxx.size())
bbb=mb()
if __name__=='__main__':
	it=3
	step=int(sys.argv[it]) if len(sys.argv)>it and sys.argv[it].isdigit() else 8
	t0=time.time()
	info={
		# formed basic steps
		"moves":[
			# deg90n
			[(100, -100), (100, -100), (100, -100), (100, -100), (100, -100), (100, -100), (100, -100)],
			# deg90p
			[(-100, 100), (-100, 100), (-100, 100), (-100, 100), (-100, 100), (-100, 100), (-100, 100)],
			# forward
			[(100, 100), (100, 100), (100, 100), (100, 100), (100, 100), (100, 100), (100, 100)],
		]
	}
	info={}
	res=genSol_v3(bbb,xxx,step=step,stateLimit=4095,verbose=True,info=info)
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
		
		if len(sys.argv)>1 and sys.argv[1]=='bot':
			from lib.mBot import *
			def doAct(act,bot):
				dt=0.125
				bot.doMove(act[0],act[1])
				sleep(dt)
				bot.doMove(0,0)
				sleep(dt)
			bot = mBot()
			bot.startWithSerial("COM3")
			sleep(4)
			print("start")
			acts=[x for m in movesS[0] for x in m[1]]
			for act in acts: doAct(act,bot)
			print("exit")
			bot.close()
			bot.exit(0,0)
	pass
	exit()
