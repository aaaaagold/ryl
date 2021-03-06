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
	res=genSol_v3(q,elgt,step=step,stateLimit=4095,shortcut=False,onlyFirst=True,verbose=True)
	print("sol1 genSol ende") # debug
	trans=[(0,"")]+[ (oriNodes.index(n)+1,n) for nv in res['possible'] for n in nv if n in oriNodes ]
	tmp=max(trans)
	print(res,oriNodes)
	rtv=len(oriNodes)+1
	if len(res["moves"])!=0: return (rtv,"Final")
	# /*
	node=elgt.goal_nodes[oriNodes[tmp[0]]] if tmp[0]<len(oriNodes) else elgt.goal_final[ [k for k in elgt.goal_final][0] ]
	fd=cs2d(node[1][0].constraints)
	rtv=nINF_v1[0]
	for p in res['possible']:
		gs=elgt.goal_nodes[p[-1]][1]
		M=-(len(fd)<<8)*(len(gs)==0)
		for g in gs:
			cd=cs2d(g.constraints)
			S=0
			for k in fd: S-=(4 if not k in cd else abs(fd[k]-cd[k]))*4*(int((k//2)**0.5))**4
			print(fd)
			print(cd)
			if S<M: M=S
		M*=20
		M-=len(p)
		if rtv<M: rtv=M
	# */
	print("trans",trans) # debug
	# /*
	print(rtv)
	return (rtv+tmp[0]*1000000,tmp[1])
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
			[1, 10, 3, 14, 6, 7, 8, 15, 4, 12, 2, 11, 0, 13, 5, 9], # D
			[12, 6, 8, 13, 5, 10, 0, 4, 1, 11, 3, 7, 14, 2, 9, 15], # E
			[12, 4, 13, 0, 14, 3, 5, 9, 1, 10, 8, 15, 7, 6, 11, 2], # E
			[5, 10, 4, 6, 7, 8, 15, 12, 14, 13, 3, 1, 11, 0, 2, 9], # E
			[11, 14, 1, 15, 9, 5, 3, 0, 6, 4, 7, 8, 10, 13, 2, 12], # E
		]
		tests=tests[-1:]
		tests=[]
		
		args={
			"manual":"ainput-15p-arranged/main.txt",
			"popsize":11,
			"maxAddedNodes":10,
			"r-mutate":10,
			"r-cross":10,
			"r-total":10000,
			"r-change":20,
			"addedRatio":2.0,
			"qsize":1,
			"step":23,
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
		pop=[ ([0,0],elgt.copy(),[]) for _ in range(1) ]
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
			untilSize=int(popsize*addedRatio)+popsize
			newpop=[]
			newpop.extend(pop)
			while len(newpop)<untilSize:
				basesrc=random.choice(pop)
				baseGenNum=basesrc[0][1]
				base=([0,baseGenNum],basesrc[1].copy(),[])
				best="" if len(basesrc[2])==0 else min(basesrc[2])[1]
				for _r_change in range(r_change):
					if random.random()<0.9:
						# mutate
						base[1].mutate(best,maxAddedNodes=maxAddedNodes,
							p_nodeNoise=0.1,
							p_nodeNoiseDiff=0.9,
							p_nodePartialFinal=0.1,
							p_nodeSparse=0.01,
							#p_nodeMerge=0.5,
							p_nodeRandWeight=0.9
							)
					else:
						# cross
						rhs=random.choice(pop)
						base[0][1]=max(base[0][1],rhs[0][1])
						base[1].cross(rhs[1])
				base[0][1]+=1 # inc genNum
				newpop.append(base)
			for q in qv: print(q.rawBoard()),q.print("\n") # debug
			for i in range(len(pop),len(newpop)):
				p=newpop[i]
				print("P:",p)
				print(i)
				print(p[1].goal_nodes_names)
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
				print("initScore",initScore)
			print("execute")
			newpop.sort(reverse=True,key=lambda x:x[0])
			pop=[newpop[0]]
			for p in newpop:
				if p[1].similar(pop[-1][1]): continue
				pop.append(p)
				print(p[1].goal_nodes_names)
				if len(pop)>=popsize: break
			from pprint import pprint
			pprint(pop[0][1].goal_nodes)
			print(len(pop))
			print(pop[0])
			print(pop[0][1].goal_nodes_names)
			print(pop[-1])
			print(pop[-1][1].goal_nodes_names)
			print("initScore",initScore)
	return 0
		
if __name__=='__main__':
	exit(main(sys.argv))

