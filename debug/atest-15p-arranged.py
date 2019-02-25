#!/bin/python3
import sys
import copy
import time

from ag import *
#from ab import *
from a15p_arranged import *
#from ab2g import *
from asol import *
	
def sol1(q,elgt,oriNodes,step):
	print("sol1 strt") # debug
	res=genSol_v3(q,elgt,step=step,stateLimit=4095,shortcut=False,onlyFirst=True,verbose=False)
	print("sol1 genSol ende") # debug
	print(res,oriNodes)
	if len(res["moves"])!=0: return len(oriNodes)+1
	trans=[(0,"")]+[ (oriNodes.index(n)+1,n) for nv in res['possible'] for n in nv if n in oriNodes ]
	print("trans",trans) # debug
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
			[1, 6, 12, 9, 14, 4, 11, 3, 0, 10, 5, 13, 2, 8, 7, 15],
		]
		
		args={
			"manual":"ainput-15p-arranged/main.txt",
			"popsize":11,
			"maxAddedNodes":100,
			"r-mutate":10,
			"r-cross":10,
			"r-total":10000,
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
		maxAddedNodes=int(args["maxAddedNodes"])
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
		print(qv[0].outputs()),qv[0].print() # debug
		strt=[]
		for q in qv:
			res=sol1(q,elgt,oriNodes,step)
			strt.append(res)
		pop[0][0][0]+=sum([x[0] for x in strt])
		pop[0][2].extend(strt)
		print(pop[0]) # debug
		for _ in range(r_total):
			print(_)
			untilSize=int(len(pop)*addedRatio)
			newpop=[]
			newpop.extend(pop)
			while len(newpop)<untilSize:
				basesrc=random.choice(pop)
				baseGenNum=basesrc[0][1]
				base=([0,baseGenNum],basesrc[1].copy(),[])
				best="" if len(base[2])==0 else min(base[2])[1]
				for _r_change in range(r_change):
					if random.random()<0.5:
						# mutate
						base[1].mutate(best,maxAddedNodes=maxAddedNodes)
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
			from pprint import pprint
			pprint(pop[0][1].goal_nodes)
			print(pop[0])
			print(pop[-1])
	return 0
		
if __name__=='__main__':
	exit(main(sys.argv))

