#!/bin/python3
import re
from attt import *
from ag import *

# TODO: all

def t2g(b,blocks=[]):
	rtv=goal()
	return rtv

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

def genSol_bfsTopMatch(bfsRes,gt,notBelow=None):
	#bfsRes=b.bfs(8)
	matches=[]
	for i in bfsRes:
		mv=matchGoaltree(bfsRes[i][0],gt,notBelow)
		matches+=matchGoaltree_trim(mv,gt)
	return matchGoaltree_trim(matches,gt)

# TODO: try fixedBlockIts if unable to reach next subgoal
def genSol_1(b,gt,step=8,stateLimit=4095,notBelow=None,fixedBlockIts=[]):
	# return: [ (goalName,[ (stateNum,(state,stepCnt,(move,stateNum))), ]) ]
	bfsRes=b.bfs(step,stateLimit=stateLimit)
	mv=genSol_bfsTopMatch(bfsRes,gt,notBelow)
	return ([ (k,genSol_bfsMatchStates(bfsRes,gt.getGoals(k))) for k in mv ],bfsRes)

def genSol(b,gt,step=8,stateLimit=4095,currStep=0,fixedBlockIts=[],
	notBelow=None,
	_isBegin=True,
	_moves=[],_rtvMoves=[],
	_nodes=[],_rtvNodes=[],
	verbose=False,
	__dummy=None):
	if _isBegin:
		del _rtvMoves,_rtvNodes
		_rtvMoves=[]
		_rtvNodes=[]
	# TODO should return each move
	immediateMatched=matchGoaltree(b,gt,notBelow)
	notBelow = None if len(immediateMatched)==0 else set(immediateMatched)
	if verbose: print('genSol',immediateMatched) # debug
	if verbose: b.print() # debug
	# TODO: notBelow = None if len(immediateMatched)==0 else immediateMatched
	finalGoals=gt.getFinals()
	tmp,bfs=genSol_1(b,gt,step,stateLimit,notBelow=notBelow)
	goalsInFinals=[ x for x in tmp if x[0] in finalGoals ]
	if len(goalsInFinals)!=0:
		minDistItem=min(goalsInFinals,key=(lambda x:x[1][0][1][1]))
		if verbose: print('goal!',minDistItem) # debug
		if verbose: minDistItem[1][0][1][0].print() # debug
		_rtvMoves.append(_moves+bfs2moveSeq(bfs,minDistItem[1][0][0]))
		_rtvNodes.append(_nodes+[minDistItem[0]])
		#return [minDistItem]
	else:
		tmp=[ x for x in tmp if not x[0] in immediateMatched ]
		res=[ genSol(x[1][0][1][0],gt,step,stateLimit=stateLimit,currStep=x[1][0][1][1],
			notBelow=notBelow,
			_isBegin=False,
			_moves=_moves+bfs2moveSeq(bfs,x[1][0][0]),_rtvMoves=_rtvMoves,
			_nodes=_nodes+[x[0]],_rtvNodes=_rtvNodes,
			verbose=verbose) for x in tmp ]
		#return res
	if _isBegin:
		return {"moves":_rtvMoves,"nodes":_rtvNodes}

