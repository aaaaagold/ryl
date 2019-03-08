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
	def c2ii(c): return [ int(x) for x in c[1].split(":") ]
	def cs2d(cs): return dict([c2ii(c) for c in cs])
	print("sol1 strt") # debug
	res=genSol_v3(q,elgt,step=step,stateLimit=4095,shortcut=False,onlyFirst=True,verbose=False)
	print("sol1 genSol ende") # debug
	print(res,oriNodes)
	rtv=len(oriNodes)+1
	if len(res["moves"])!=0: return (rtv,"Final")
	# /*
	fd=cs2d(elgt.goal_final[ [k for k in elgt.goal_final][0] ][1][0].constraints)
	rtv=INF_v1[0]
	for p in res['possible']:
		gs=elgt.goal_nodes[p[-1]][1]
		M=-(len(fd)<<3)*(len(gs)==0)
		for g in gs:
			cd=cs2d(g.constraints)
			S=0
			for k in fd: S-=(4 if not k in cd else abs(fd[k]-cd[k]))*k*k
			if S<M: M=S
		M-=len(p)
		if M<rtv: rtv=M
	# */
	trans=[(0,"")]+[ (oriNodes.index(n)+1,n) for nv in res['possible'] for n in nv if n in oriNodes ]
	print("trans",trans) # debug
	# /*
	print(rtv)
	return (rtv,max(trans)[1])
	# */
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
			[6, 4, 9, 2, 8, 15, 11, 7, 12, 1, 10, 0, 3, 14, 13, 5],
			[0, 6, 1, 11, 7, 3, 2, 9, 4, 12, 13, 5, 14, 15, 10, 8],
		]
		tests=tests[-1:]
		
		args={
			"manual":"ainput-15p-arranged/main.txt",
			"popsize":11,
			"maxAddedNodes":20,
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
		# [ ([scoreTotal,gen],idv,[score1,node]) , ... ]
		bbb=board((4,4))
		qv=[bbb.random().copy() for _ in range(qsize)]
		qv.extend([bbb.setNums(arr,arr.index(15)).copy() for arr in tests])
		print(qv[0].outputs()),qv[0].print() # debug
		strt=[]
		for q in qv:
			res=sol1(q,elgt,oriNodes,step)
			strt.append(res)
		tmp=sum([x[0] for x in strt])
		for p in pop:
			p[0][0]+=tmp
			p[2].extend(strt)
		print("debug",pop[0]) # debug
		initScore=[]
		initScore+=pop[0][2]
		#maxIt=1
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
						base[1].mutate(best,maxAddedNodes=maxAddedNodes,
							p_nodeNoise=0.5,
							p_nodeNoiseDiff=0.9,
							p_nodePartialFinal=0.1,
							p_nodeSparse=0.1,
							#p_nodeMerge=0.5,
							p_nodeRandWeight=0.1
							)
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
				for x in range(len(qv)):
					#if x==maxIt: break
					q=qv[x]
					res=sol1(q,p[1],oriNodes,step)
					p[0][0]+=res[0]
					p[2].append(res)
					print(res)
				print(p)
			newpop.sort(reverse=True,key=lambda x:x[0])
			pop=newpop[:popsize]
			from pprint import pprint
			pprint(pop[0][1].goal_nodes)
			print(pop[0])
			print(pop[-1])
			print("initScore",initScore)
	return 0
		
if __name__=='__main__':
	exit(main(sys.argv))

