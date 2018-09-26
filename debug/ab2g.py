#!/bin/python3
from ab import *
from ag import *

def b2g(b,emptyAsGoal=False):
	rtv=goal()
	barr=b.rawBoard()
	dcn=b.dontcareNum()
	en=b.emptyNum()
	for i in range(len(barr)):
		x=barr[i]
		if x!=dcn and ( x!=en or emptyAsGoal!=False ):
			rtv.add(x,label=i,arrangeLater=True)
	rtv.arrange()
	return rtv

###########

def matchGoal(b,g):
	barr=b.rawBoard()
	for x in g.constraints:
		if str(barr[x[0]])!=str(x[1]):
			return False
	return True

def matchGoaltree_find_inSet(b,goals):
	for g in goals:
		if matchGoal(b,g):
			return True
	return False

def matchGoaltree_find(b,gt):
	barr=b.rawBoard()
	rtv=[]
	for k in gt.keys():
		if matchGoaltree_find_inSet(b,gt.getGoals(k)):
			rtv.append(k)
	return rtv

def matchGoaltree_trim(mv,gt):
	mv=set(mv)
	rtv=[]
	tmpv=[]
	for k in mv:
		tmps=""
		tmpk=k
		while 0==0:
			tmps+=tmpk
			succ=gt.getSucc(tmpk)
			if succ=='-': break
			tmpk=succ
		tmpv.append((k,tmps))
	# TODO: need suffix array to speedup
	rg=range(len(tmpv))
	delSet=set()
	for i1 in rg:
		for i2 in rg:
			if i1==i2: continue
			if tmpv[i1][1] in tmpv[i2][1]:
				delSet.add(tmpv[i2][0])
	rtv+=[ k for k in mv if not k in delSet]
	return rtv

def matchGoaltree(b,gt):
	return matchGoaltree_trim(matchGoaltree_find(b,gt),gt)

###########

def genSol_bfsMatchStates(bfsRes,goals):
	# goaltree.getGoals
	# return minDists
	cand=[]
	for k,v in bfsRes.items():
		if matchGoaltree_find_inSet(v[0],goals):
			cand.append((k,v))
	minDist=min([ x[1][1] for x in cand ])
	return [ x for x in cand if x[1][1]==minDist ]

def genSol_bfsTopMatch(bfsRes,gt):
	#bfsRes=b.bfs(8)
	matches=[]
	for i in bfsRes:
		mv=matchGoaltree(bfsRes[i][0],gt)
		matches+=matchGoaltree_trim(mv,gt)
	return matchGoaltree_trim(matches,gt)

def genSol_1(b,gt,step=8):
	# return: [ (goalName,[ (stateNum,(state,stepCnt,(move,stateNum))), ]) ]
	bfsRes=b.bfs(step)
	mv=genSol_bfsTopMatch(bfsRes,gt)
	return [ (k,genSol_bfsMatchStates(bfsRes,gt.getGoals(k))) for k in mv ]

def genSol(b,gt,step=8,currStep=0):
	# TODO should return each move
	immediateMatched=matchGoaltree(b,gt)
	print('genSol',immediateMatched)
	b.print()
	finalGoals=gt.getFinals()
	tmp=genSol_1(b,gt,step)
	goalsInFinals=[ x for x in tmp if x[0] in finalGoals ]
	if len(goalsInFinals)!=0:
		minDistItem=min(goalsInFinals,key=(lambda x:x[1][0][1][1]))
		print('goal!',minDistItem)
		return [minDistItem]
	else:
		tmp=[ x for x in tmp if not x[0] in immediateMatched ]
		res=[ genSol(x[1][0][1][0],gt,step,currStep=x[1][0][1][1]) for x in tmp ]
		return res

