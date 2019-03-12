#!/bin/python3
import sys
import copy
import time

from ag import *
#from ab import *
#from a15p_arranged import *
from a15p_rev import *
#from ab2g import *
from asol import *


def search():
	return
	# mutate
	#  minimize(max([distance of 2 nodes which are nearby]))
	#   try several mids # subset of delta-constraint become mids
	#    and mids of two, probability related to distance
	#     and mids ( repeat )
	#

def reproduce():
	return
	# cross
	#  exchange partial solution?
	#

def turn():
	return
	# several_reproduce
	# 

def solving():
	return
	#

def sol1(q,elgt,oriNodes,step):
	def c2ii(c): return [ int(x) for x in c[1].split(":") ]
	def cs2d(cs): return dict([c2ii(c) for c in cs])
	print("sol1 strt") # debug
	res=genSol_v3(q,elgt,step=step,stateLimit=4095,shortcut=False,onlyFirst=True,verbose=True)
	print("sol1 genSol ende") # debug
	print(res,oriNodes)
	rtv=len(oriNodes)+1
	if len(res["moves"])!=0: return (rtv,"Final")
	trans=[(0,"")]+[ (oriNodes.index(n)+1,n) for nv in res['possible'] for n in nv if n in oriNodes ]
	tmp=max(trans)
	tmp2=[nv[nv.index(tmp[1]):] for nv in res['possible'] if tmp[1] in nv]
	tmp2.sort(key=lambda x:len(x))
	return (tmp[0],tmp2[0])
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
			[4, 2, 9, 3, 12, 13, 15, 10, 5, 11, 1, 6, 8, 7, 14, 0], # B23
		]
		tests=tests[-1:]
		tests=[]
		
		args={
			"manual":"ainput-15p-rev-sparse/main.txt",
			"popsize":11,
			"maxAddedNodes":10,
			"r-mutate":10,
			"r-cross":10,
			"r-total":10000,
			"r-change":20,
			"addedRatio":2.0,
			"qsize":1,
			"step":11,
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
		oriNodes=[n for n in elgt.goal_nodes_names]
		oriNodes.sort(key=lambda x:elgt.goal_nodes[x][0])
		print(oriNodes)
		pop=[ ([0,0],elgt.copy(),[]) for _ in range(1) ]
		# [ ([scoreTotal,gen],idv,[score1,node]) , ... ]
		bbb=board((4,4))
		qv=[bbb.random().copy() for _ in range(qsize)]
		qv.extend([bbb.setNums(arr,arr.index(15)).copy() for arr in tests])
		print(qv[0].outputs()),qv[0].print() # debug
		if 0!=0: # debug test: ok if it's original
			res=genSol_v3(qv[0],elgt,step=step,stateLimit=4095,shortcut=False,onlyFirst=True,verbose=True)
			print(res)
			exit()
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

