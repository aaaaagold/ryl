#!/bin/python3
from shorthand import *
from amyhead import *

def _bfs(obj,step=8,turn=0,stateLimit=4095,notViolate=None,info={}):
	#if "h" in info: print(info["h"]) # debug
	#hvv=info["hvv"] if "hvv" in info else []
	#hv=[ h for hv in hvv for h in hv ]
	hv=info['hv']
	stateCnt=0
	rtv={}
	t=(obj.copy(),0,(-1,None)) # ( ; , total_puts , ((turn,last_put_loc) , lastStatHash) )
	#q=queue()
	#q.push(t)
	orderNum=0
	#hInfo=tuple([0 for _ in range(len(hv))])
	hInfo=tuple([0 for _ in range(len(hv))])
	hDistinct,hDF=[[],[]],[min,max] # [ min_arr , max_arr ]
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
				if len(hDistinct[0])==0:
					for arr in hDistinct:
						arr.extend(hInfo)
				else:
					for m in range(len(hDF)):
						for i in range(len(hInfo)):
							hDistinct[m][i]=hDF[m](hDistinct[m][i],hInfo[i])
				cmpInfo=(hInfo,orderNum)
				heappush(heap,( cmpInfo , (stat,currstep+1,(actinfo,currstatNum)) ))
				orderNum+=1
	return (rtv,hDistinct)
	return rtv # rtv[stateHash]=(state,step,(actInfo,prevState))
	# hDistinct = [ [min_of_hi_appeared],[max_of_hi_appeared] ]
	pass

def bfs(obj,step=8,turn=0,stateLimit=4095,notViolate=None,info={}):
	rtv={}
	INFO={}
	INFO.update(info)
	hvv=info['hvv']+[[]]
	blankTested=False
	for i in range(len(hvv)):
		if blankTested!=False and len(hvv)==i+1: continue
		hv=hvv[i]
		INFO['hv']=hv
		res=_bfs(obj,step=step,turn=turn,stateLimit=stateLimit,notViolate=notViolate,info=INFO)
		blankTested|=(res[1][0]==res[1][1])
		res=res[0]
		delSet=set([ k for k in res if k in rtv and rtv[k][1]<=res[k][1] ])
		for k in delSet: del res[k]
		rtv.update(res)
	return rtv

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

