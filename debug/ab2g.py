#!/bin/python3
import re
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

def matchGoal_v1(b,g):
	barr=b.rawBoard()
	for x in g.constraints:
		if str(barr[x[0]])!=str(x[1]):
			return False
	return True

def matchGoal_v2(b,g):
	barr=b.rawBoard()
	print(g),exit()
	for x in g.constraints:
		p=re.compile("([0-9]+):([0-9]+)")
		item=p.split(str(x[1]))
		matched=False
		for i in range(1,len(item),p.groups+1):
			loc = int(item[i  ])
			pn  = item[i+1]
			if str(barr[loc])==str(pn):
				matched=True
				break
		if matched==False:
			return False
	return True

def matchGoal_v3(b,g):
	barr=b.rawBoard()
	for x in g.constraints:
		isKW=False
		matched=False # if a cosntraint is matched
		if x[0]==g.__class__.KW_include_label:
			isKW=True
			for name in x[1][1].getFinals():
				goals=x[1][1].getGoals(name)
				if matchGoaltree_find_inSet(b,goals):
					matched=True
					break
		if isKW==False:
			p=re.compile("([0-9]+):([0-9]+)")
			item=p.split(str(x[1])) # may have several constraints, just one of them
			for i in range(1,len(item),p.groups+1):
				loc = int(item[i  ])
				pn  = item[i+1]
				if str(barr[loc])==str(pn):
					matched=True
					break
		if matched==False:
			return False
	return True

matchGoal=matchGoal_v3

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

# TODO: try fixedBlockIts if unable to reach next subgoal
def genSol_1(b,gt,step=8,fixedBlockIts=[]):
	# return: [ (goalName,[ (stateNum,(state,stepCnt,(move,stateNum))), ]) ]
	bfsRes=b.bfs(step)
	mv=genSol_bfsTopMatch(bfsRes,gt)
	return ([ (k,genSol_bfsMatchStates(bfsRes,gt.getGoals(k))) for k in mv ],bfsRes)

def genSol(b,gt,step=8,currStep=0,fixedBlockIts=[],
	_isBegin=True,
	_moves=[],_rtvMoves=[],
	_nodes=[],_rtvNodes=[],
	__dummy=None):
	# TODO should return each move
	immediateMatched=matchGoaltree(b,gt)
	print('genSol',immediateMatched)
	b.print()
	finalGoals=gt.getFinals()
	tmp,bfs=genSol_1(b,gt,step)
	goalsInFinals=[ x for x in tmp if x[0] in finalGoals ]
	if len(goalsInFinals)!=0:
		minDistItem=min(goalsInFinals,key=(lambda x:x[1][0][1][1]))
		print('goal!',minDistItem)
		minDistItem[1][0][1][0].print()
		_rtvMoves.append(_moves+bfs2moveSeq(bfs,minDistItem[1][0][0]))
		_rtvNodes.append(_nodes+[minDistItem[0]])
		#return [minDistItem]
	else:
		tmp=[ x for x in tmp if not x[0] in immediateMatched ]
		res=[ genSol(x[1][0][1][0],gt,step,currStep=x[1][0][1][1],_isBegin=False,_moves=_moves+bfs2moveSeq(bfs,x[1][0][0]),_nodes=_nodes+[x[0]]) for x in tmp ]
		#return res
	if _isBegin:
		return {"moves":_rtvMoves,"nodes":_rtvNodes}

