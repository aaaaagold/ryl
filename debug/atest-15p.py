#!/bin/python3
import sys
import copy
import time

from ag import *
from ab import *
#from ab2g import *
from asol import *

xxx=goaltree()
xxx.fromTxt("ainput-15p/main.txt")
learnDir="alearn-15p/"
#print(xxx)
#print("toStr")
#xxxtxt=xxx.toStr()
#xxx.fromStr(xxxtxt,cd='ainput-15p/')
#print(xxx.toStr())
print("#end")
print("finals:",xxx.getFinals())
print("size:",xxx.size())
bbb=board((4,4))
if 0!=0 or (len(sys.argv)>1 and sys.argv[1]=="1demo"):
	bbb.random()
	while bbb.solvable()==False: bbb.random()
	arr=[1, 3, 7, 12, 5, 15, 10, 0, 2, 4, 8, 11, 9, 6, 13, 14]
	bbb.setNums(arr,arr.index(15))
	bbb.print()
	print(bbb.rawBoard())
	t0=time.time()
	res=genSol_v3(bbb,xxx,step=8,stateLimit=4095)
	print(time.time()-t0)
	if len(res['moves'])==0:
		print("GG")
	else:
		movesS=res['moves']
		print(movesS)
		nodesS=res['nodes']
		for msg in movesS[0]:
			print("msg")
			print(msg)
			move=msg[1]
			time.sleep(0.25)
			bbb.move(move)
			print("board")
			bbb.print()
			print()
	pass
	exit()
# TODO 

if 0!=0:
	notSolved=[
		#[15, 5, 10, 4, 6, 14, 9, 8, 13, 0, 11, 1, 2, 7, 3, 12],
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
		res=genSol_v3(bbb,xxx,step=8)
		print(time.time()-t0)
		movesS=res['moves']
		nodesS=res['nodes']
		if len(movesS)==0:
			bbb.print()
			res=genSol_v3(bbb,xxx,step=8,verbose=True)
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
	learnFile=""
	for i in range(len(sys.argv)):
		if sys.argv[i]=="-l":
			learnFile+=sys.argv[i+1]
			break
	print("need appearing 'goal!'."+
		("  %s=%s"%("step",str(step)))+
		("  %s=%s"%("stateLimit",str(stateLimit)))+
		("  %s=%s"%("learnFile",learnFile))
		)
	succList=[]
	boardInitHistoryAll=[]
	boardInitHistory=[]
	while 0==0:
		print(len(succList))
		if len(succList)>99 or learnFile!="":
			if learnFile!="":
				xxx.loadNextGoalFile(learnFile)
			xxx.saveNextGoal(succList)
			succList=[]
			tmp=xxx.saveNextGoalFile(learnDir+"test.learn")
			print(tmp)
			boardInitHistoryAll.append(boardInitHistory)
			if 0==0:
				#test
				logs_time=[("bylearn","notlearn")]
				logs_node=[("bylearn","notlearn")]
				for i in range(len(boardInitHistory)):
					print(i)
					h=boardInitHistory[i]
					bbb=h[0].copy()
					bbb.print()
					print("test",bbb.rawBoard())
					t0=time.time()
					res=genSol(bbb,xxx,step=step,stateLimit=stateLimit,endBefore=t0+h[1]+60)
					t1=time.time()-t0 if len(res['nodes'])!=0 else "tooLong/fail"
					print("test",t1,"prev",h[1])
					logs_time.append((t1,h[1]))
					logs_node.append((res['nodes'],h[2]))
					print("test",res['nodes'])
				prefix=learnDir+"log/logs-"+str(time.time())
				with open(prefix+"-time","w") as f:
					for l in logs_time:
						f.write(str(l[0])+"\t"+str(l[1])+"\n")
				with open(prefix+"-node","w") as f:
					for l in logs_node:
						f.write(str(l[0])+"\n"+str(l[1])+"\n\n")
				with open(prefix+"-board","w") as f:
					f.write("[\n")
					for h in boardInitHistory:
						f.write("\t"+str(h[0].rawBoard())+",\n")
					f.write("]\n")
				print("unseen boards")
				with open(prefix+"-unseen","w") as f:
					f.write("board"+"\t"+"time"+"\t"+"nodes"+"\n")
					for i in range(100):
						bbb.random()
						while bbb.solvable()==False: bbb.random()
						bbb.print()
						t0=time.time()
						res=genSol(bbb,xxx,step=step,stateLimit=stateLimit,endBefore=t0+60)
						t1=time.time()-t0 if len(res['nodes'])!=0 else "tooLong/fail"
						print("u",t1)
						f.write(str(bbb.rawBoard())+"\t"+str(t1)+"\t"+str(res['nodes'])+"\n")
						print("u",res['nodes'])
			boardInitHistory=[]
			exit()
		print("board.random()")
		bbb.random()
		while bbb.solvable()==False: bbb.random()
		bbb.print()
		print(bbb.rawBoard())
		t0=time.time()
		res=genSol_v3(bbb,xxx,step=step,stateLimit=stateLimit)
		t1=time.time()-t0
		succList+=res['nodes']
		boardInitHistory.append((bbb.copy(),t1,res['nodes']))
		print(t1)
		if len(res['moves'])==0:
			res=genSol_v3(bbb,xxx,step=step,stateLimit=stateLimit,verbose=True)
			print(bbb.rawBoard())
			#break
			boardInitHistory.pop()
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
		#print(res['nodes']) # debug - for developing learn file
		# [ [ "subgoal-path_A-1" , "subgoal-path_A-2" , ... ] , [ "subgoal-path_B-1" , "subgoal-path_B-2" , ... ] , ...]

