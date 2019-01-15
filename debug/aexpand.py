#!/bin/python3
from shorthand import *
from amyhead import *

def bfs(obj,step=8,turn=0,stateLimit=4095,notViolate=None,info={}):
	#if "h" in info: print(info["h"]) # debug
	hvv=info["hvv"] if "hvv" in info else []
	hv=[ h for hv in hvv for h in hv ]
	stateCnt=0
	rtv={}
	t=(obj.copy(),0,(-1,None)) # ( ; , total_puts , ((turn,last_put_loc) , lastStatHash) )
	#q=queue()
	#q.push(t)
	orderNum=0
	#hInfo=tuple([0 for _ in range(len(hv))])
	hInfo=tuple([0 for _ in range(len(hv))])
	cmpInfo=(hInfo,orderNum)
	heap=[]
	heappush(heap,(cmpInfo,t))
	orderNum+=1
	del t
	#while q.size()!=0:
	while len(heap)!=0:
		#t=q.pop()
		t=heappop(heap)[1]
		currstat=t[0]
		currstep=t[1]
		last_put=t[2][0]
		currstatNum=currstat.hash()
		if currstatNum in rtv: continue
		rtv[currstatNum]=t
		del t
		stateCnt+=1
		if stateCnt>stateLimit: break
		near1=currstat.near1(info=info)
		for near in near1:
			stat=near[2]
			#if stat.turn()==-1 and not (isNone(notViolate) or matchGoaltree_find_inSet(stat,notViolate)):
			#	continue
			actinfo=near[:2] # (who does, does what)
			if currstep<step:
				#q.push((stat,currstep+1,(actinfo,currstatNum)))
				hInfo=tuple([ h(stat.outputs()) for h in hv ])
				cmpInfo=(hInfo,orderNum)
				heappush(heap,( cmpInfo , (stat,currstep+1,(actinfo,currstatNum)) ))
				orderNum+=1
	return rtv # rtv[stateHash]=(state,step,(actInfo,prevState))
	pass

def bfs2moveSeq(bfs,goalHash):
	moves=[]
	if (type(bfs)==type({}) and (goalHash in bfs)) or (type(bfs)==type([]) and type(bfs[goalHash])!=type(None)):
		pre=bfs[goalHash][2]
		preStat=pre[1]
		#print(type(preStat)),exit() # debug
		while not isNone(preStat):
			moves.append(pre[0])
			pre=bfs[preStat][2]
			preStat=pre[1]
		#print("preStat",preStat),exit() # debug
		moves.reverse()
	return moves

###########

