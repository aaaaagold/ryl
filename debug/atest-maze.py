#!/bin/python3
import sys
import copy
import time

from ag import *
from amaze import *
#from ab2g import *
from asol import *

xxx=goaltree()
xxx.fromTxt("ainput-maze/main.txt")
learnDir="alearn-maze/"
#print(xxx)
#print("toStr")
#xxxtxt=xxx.toStr()
#xxx.fromStr(xxxtxt,cd='ainput-15p/')
#print(xxx.toStr())
print("#end")
print("finals:",xxx.getFinals())
print("size:",xxx.size())
bbb=maze().fromFile("ainput-maze/mazes/m-1-adjlist.txt")
if 0!=0 or (len(sys.argv)>1 and sys.argv[1]=="1demo"):
	bbb.random()
	#while bbb.solvable()==False: bbb.random()
	bbb.print()
	t0=time.time()
	res=genSol_v1(bbb,xxx,step=8,stateLimit=4095)
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
			time.sleep(0.5)
			bbb.move(move)
			print("board")
			bbb.print()
			print()
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
		res=genSol_v1(bbb,xxx,step=8)
		print(time.time()-t0)
		movesS=res['moves']
		nodesS=res['nodes']
		if len(movesS)==0:
			bbb.print()
			res=genSol_v1(bbb,xxx,step=8,verbose=True)
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
						#while bbb.solvable()==False: bbb.random()
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
		#while bbb.solvable()==False: bbb.random()
		bbb.print()
		print(bbb.rawBoard())
		t0=time.time()
		res=genSol_v1(bbb,xxx,step=step,stateLimit=stateLimit)
		t1=time.time()-t0
		succList+=res['nodes']
		boardInitHistory.append((bbb.copy(),t1,res['nodes']))
		print(t1)
		if len(res['moves'])==0:
			res=genSol_v1(bbb,xxx,step=step,stateLimit=stateLimit,verbose=True)
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

