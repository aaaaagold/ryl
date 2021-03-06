#!/bin/python3
import sys
import copy
import time

from ag import *
#from ab import *
from a15p_rev import *
#from ab2g import *
from asol import *
	
def sol1(q,elgt,oriNodes,step):
	print("sol1 strt")
	res=genSol_v4(q,elgt,step=step,stateLimit=4095,verbose=False)
	print("sol1 genSol ende")
	print(res,oriNodes)
	if len(res["moves"])!=0: return len(oriNodes)+1
	trans=[(0,"")]+[ (oriNodes.index(n)+1,n) for nv in res['possible'] for n in nv if n in oriNodes ]
	print("trans",trans)
	return max(trans)

def demo1(argv):
	pass

def sol_thread(newpopPartial,qv,oriNodes,step):
	for p in newpopPartial:
		#print("P:",p)
		p[0][0]&=0
		p[2].clear()
		for q in qv:
			res=sol1(q,p[1],oriNodes,step)
			p[0][0]+=res[0]
			p[2].append(res)
			#print(res)

def main(argv):
	if len(argv)>1 and argv[1]=="1demo":
		demo1(argv[1:])
	else:
		tests=[
			[4, 8, 7, 0, 12, 11, 14, 2, 6, 15, 1, 13, 10, 3, 5, 9],
		]
		
		args={
			"manual":"ainput-15p-rev/very-sparse.txt",
			"popsize":11,
			"r-mutate":10,
			"r-cross":10,
			"r-total":100,
			"r-change":10,
			"addedRatio":2.0,
			"qsize":1,
			"step":8,
			"__dummy":0
		}
		if "--help" in argv or "-h" in argv or "?" in argv:
			print(args)
			return 0
		for k in args:
			if k in argv:
				args[k]=argv.index(k)+1
		manual=args["manual"]
		popsize=int(args["popsize"])
		r_mutate=int(args["r-mutate"])
		r_cross=int(args["r-cross"])
		r_total=int(args["r-total"])
		r_change=int(args["r-change"])
		addedRatio=float(args["addedRatio"])
		qsize=int(args["qsize"])
		step=int(args["step"])

		gt=Goaltree()
		gt.fromTxt(manual)
		elgt=goaltree_edgeless(gt)
		oriNodes=elgt.wkeys("")
		oriNodes.sort()
		oriNodes=[ x[1] for x in oriNodes ]
		print(oriNodes)
		pop=[ ([0,0],elgt.copy(),[]) for _ in range(popsize) ]
		# [ ([solve count,gen],idv) , ... ]
		bbb=board((4,4))
		qv=[bbb.random().copy() for _ in range(qsize)]
		qv.extend([bbb.setNums(arr,arr.index(15)) for arr in tests])
		strt=[]
		for q in qv:
			res=sol1(q,elgt,oriNodes,step)
			strt.append(res)
		pop[0][0][0]+=sum([x[0] for x in strt])
		pop[0][2].extend(strt)
		for _ in range(r_total):
			untilSize=int(len(pop)*addedRatio)
			newpop=[]
			newpop.extend(pop)
			while len(newpop)<untilSize:
				basesrc=random.choice(pop)
				baseGenNum=basesrc[0][1]
				base=([0,baseGenNum],basesrc[1].copy(),[])
				best="" if len(base[2])==0 else max(base[2])[1]
				for _r_change in range(r_change):
					if random.random()<0.5:
						# mutate
						base[1].mutate(best)
					else:
						# cross
						rhs=random.choice(pop)
						base[0][1]=max(base[0][1],rhs[0][1])
						base[1].cross(rhs[1])
				base[0][1]+=1 # inc genNum
				newpop.append(base)
			for q in qv: print(q.rawBoard()),q.print("\n") # debug
			for i in range(popsize,len(newpop)):
				p=newpop[i]
				print("P:",p)
				p[0][0]&=0
				p[2].clear()
				for q in qv:
					res=sol1(q,p[1],oriNodes,step)
					p[0][0]+=res[0]
					p[2].append(res)
					print(res)
			newpop.sort(reverse=True,key=lambda x:x[0])
			pop=newpop[:popsize]
			print(newpop[0])
	return 0
		
if __name__=='__main__':
	exit(main(sys.argv))



xxx=Goaltree()
xxx.fromTxt("ainput-15p-rev/main.txt")
xxx.fromTxt("ainput-15p-rev/very-sparse.txt")
gt=xxx
xxx=goaltree_edgeless(gt)
learnDir="alearn-15p-rev/"
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
	it=2
	step=int(sys.argv[it]) if len(sys.argv)>it and sys.argv[it].isdigit() else 8
	bbb.random()
	while bbb.solvable()==False: bbb.random()
	arr=[]
	#arr=[1, 3, 7, 12, 5, 15, 10, 0, 2, 4, 8, 11, 9, 6, 13, 14]
	#arr=[12, 8, 7, 6, 9, 13, 15, 3, 0, 1, 11, 10, 2, 14, 5, 4]
	#arr=[3, 0, 1, 6, 12, 7, 9, 11, 5, 10, 8, 15, 14, 2, 13, 4]
	#arr=[3, 10, 13, 1, 9, 4, 12, 7, 15, 14, 6, 0, 11, 8, 5, 2]
	#arr=[8, 13, 9, 5, 3, 15, 1, 11, 10, 14, 12, 7, 6, 4, 0, 2]
	#arr=[8, 5, 15, 4, 13, 1, 10, 7, 12, 3, 6, 9, 11, 2, 0, 14]
	#arr=[11, 1, 7, 13, 5, 6, 12, 10, 15, 8, 0, 2, 9, 14, 3, 4]
	#arr=[9, 3, 2, 7, 11, 4, 14, 8, 13, 10, 1, 15, 6, 0, 5, 12]
	#arr=[14, 13, 12, 1, 7, 3, 15, 10, 4, 5, 0, 11, 6, 9, 2, 8]
	#arr=[0, 4, 14, 2, 13, 1, 10, 15, 11, 8, 3, 7, 6, 12, 9, 5] # cause: the manifest is 3 then 2 but this suits "2 then 3"
	#arr=[7, 6, 15, 11, 8, 1, 2, 5, 9, 14, 10, 12, 0, 4, 3, 13] # slow # appear exactly same board in the solution path.
	#arr=[13, 14, 0, 4, 5, 1, 15, 7, 6, 10, 12, 8, 9, 11, 2, 3] # slow # appear exactly same board in the solution path.
	#arr=[6, 4, 11, 1, 5, 14, 12, 0, 7, 13, 2, 10, 15, 3, 9, 8] # very slow
	#arr=[15, 12, 14, 13, 4, 11, 9, 0, 1, 2, 7, 6, 8, 10, 5, 3]
	#arr=[5, 1, 11, 6, 3, 9, 10, 4, 14, 2, 12, 7, 8, 13, 15, 0] # fail
	#arr=[5, 1, 11, 6, 3, 9, 10, 4, 14, 2, 12, 7, 8, 13, 15, 0] # test: 91@step=8 79@step=79
	#arr=[4, 9, 6, 14, 11, 2, 1, 8, 7, 15, 12, 3, 10, 13, 0, 5] # test: 91@step=8 123@step=23
	#arr=[10, 7, 15, 14, 11, 12, 2, 6, 9, 5, 4, 13, 3, 1, 8, 0] # test: 98@step=8 150@step=23
	#arr=[0, 9, 7, 8, 11, 10, 2, 1, 14, 6, 12, 3, 4, 5, 15, 13] # fail@step=8
	#arr=[2, 8, 11, 12, 0, 1, 4, 15, 6, 7, 3, 10, 13, 5, 9, 14] # 58@step=8 108@step=23 ; slow@step=8 fast@step=23
	#arr=[10, 5, 15, 7, 4, 13, 1, 11, 9, 2, 6, 3, 0, 8, 14, 12] # 78@step=8 90@step=23 ; slow@step=8 fast@step=23
	#arr=[14, 15, 2, 12, 9, 8, 11, 5, 7, 6, 1, 10, 3, 13, 4, 0] # 109@step=8 139@step=23 ; fast@step=8 slow@step=23
	#
	if len(arr)!=0: bbb.setNums(arr,arr.index(15))
	bbb.print()
	#print(bbb.output()) , print(bbb.outputs()) , exit()
	print(bbb.rawBoard())
	t0=time.time()
	res=genSol_v3(bbb,xxx,step=step,stateLimit=4095,verbose=True)
	print(time.time()-t0)
	if len(res['moves'])==0:
		print("GG")
	else:
		movesS=res['moves']
		mml=min([len(mv) for mv in movesS])
		print(movesS,mml)
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
		print(mml)
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
	failCnt=0
	while 0==0:
		print(len(succList))
		if len(succList)>99 or learnFile!="":
			for t in boardInitHistory:
				print(t[0].rawBoard(),t[1],t[2])
			def getmmm(arr):
				sarr=sorted(arr)
				return sarr[-1],sarr[len(sarr)>>1],sarr[0]
			print("time: max,mid,min =",getmmm([x[1] for x in boardInitHistory]))
			print("step: max,mid,min =",getmmm([x[3] for x in boardInitHistory]))
			print("fail count =",failCnt)
			#print("time: max,mid =",(lambda sarr:(sarr[-1],sarr[len(sarr)>>1]))(sorted( (lambda arr:[x[1] for x in arr])(boardInitHistory) )) ) # deprecated
			exit() # TODO
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
					res=genSol(bbb,xxx,step=step,stateLimit=stateLimit,endBefore=t0+h[1]+60,info={"failmemCnt":1023})
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
			boardInitHistory.clear()
			failCnt*=0
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
		mml=max([len(mv) for mv in res['moves']]+[-1])
		failCnt+=(mml<0)
		boardInitHistory.append((bbb.copy(),t1,res['nodes'],mml))
		print(t1,(res['moves']),mml)
		if len(res['moves'])==0:
			#res=genSol_v3(bbb,xxx,step=step,stateLimit=stateLimit,verbose=True)
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

