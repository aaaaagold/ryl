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
	rtvM2b={}
	for i in bfsRes:
		bRes=bfsRes[i]
		mv=matchGoaltree(bRes[0],gt,notBelow)
		mvt=matchGoaltree_trim(mv,gt)
		matches+=mvt
		for m in mvt:
			if (not m in rtvM2b) or len(rtvM2b[m])==0 or (bRes[1]<rtvM2b[m][0][1][1]):
				rtvM2b[m]=[(i,bRes)]
			elif rtvM2b[m][0][1][1]==bRes[1]:
				rtvM2b[m].append((i,bRes))
	rtvMv=matchGoaltree_trim(matches,gt)
	#return rtvMv
	rtv = [ (m,rtvM2b[m]) for m in rtvMv ] # [ (goalName,[ (stateHash,bfs[stateHash]) ... ]) ... ]
	return rtv

# TODO: try fixedBlockIts if unable to reach next subgoal
def genSol_1(b,gt,step=8,stateLimit=4095,notBelow=None,fixedBlockIts=[]):
	# return: [ (goalName,[ (stateNum,(state,stepCnt,(move,stateNum))), ]) ]
	bfsRes=b.bfs(step,stateLimit=stateLimit)
	mvb=genSol_bfsTopMatch(bfsRes,gt,notBelow)
	#return ([ (k,genSol_bfsMatchStates(bfsRes,gt.getGoals(k))) for k in mv ],bfsRes)
	return (mvb,bfsRes)

def genSol(b,gt,step=8,stateLimit=4095,currStep=0,fixedBlockIts=[],
	notBelow=None,
	lastMatch=set(),
	_isBegin=True,
	_moves=[],_rtvMoves=[],
	_nodes=[],_rtvNodes=[],
	verbose=False,
	__dummy=None):
	if _isBegin:
		del _rtvMoves,_rtvNodes
		_rtvMoves=[]
		_rtvNodes=[]
	#verbose=True # debug
	#immediateMatched=matchGoaltree(b,gt,notBelow)
	#notBelow = None if len(immediateMatched)==0 else set(immediateMatched)
	#if verbose: print('genSol',immediateMatched) # debug
	if verbose: print('genSol',lastMatch) # debug
	if verbose: b.print() # debug
	finalGoals=gt.getFinals()
	matches,bfs=genSol_1(b,gt,step,stateLimit,notBelow=notBelow)
	stateMatch=set([ (b[0],m[0]) for m in matches for b in m[1] ])
	#stateMatch.sort()
	goalsInFinals=[ x for x in matches if x[0] in finalGoals ]
	if len(goalsInFinals)!=0:
		minDistItem=min(goalsInFinals,key=(lambda x:x[1][0][1][1]))
		if verbose: print('goal!',minDistItem) # debug
		if verbose: minDistItem[1][0][1][0].print() # debug
		_rtvMoves.append(_moves+bfs2moveSeq(bfs,minDistItem[1][0][0]))
		_rtvNodes.append(_nodes+[minDistItem[0]])
		#return [minDistItem]
	else:
		#res=[ genSol(bfsNode[1][0],gt,step,stateLimit=stateLimit,currStep=bfsNode[1][1],
		#	notBelow=notBelow,
		#	lastMatch=stateMatch,
		#	_isBegin=False,
		#	_moves=_moves+bfs2moveSeq(bfs,bfsNode[0]),_rtvMoves=_rtvMoves,
		#	_nodes=_nodes+[x[0]],_rtvNodes=_rtvNodes,
		#	verbose=verbose) for x in matches if not x[0] in immediateMatched for bfsNode in x[1] ]
		
		#res=[ genSol(x[1][0][1][0],gt,step,stateLimit=stateLimit,currStep=x[1][0][1][1],
		#	notBelow=notBelow,
		#	lastMatch=stateMatch,
		#	_isBegin=False,
		#	_moves=_moves+bfs2moveSeq(bfs,x[1][0][0]),_rtvMoves=_rtvMoves,
		#	_nodes=_nodes+[x[0]],_rtvNodes=_rtvNodes,
		#	verbose=verbose) for x in matches if not x[0] in immediateMatched]
		
		#res=[ genSol(x[1][0][1][0],gt,step,stateLimit=stateLimit,currStep=x[1][0][1][1],
		#	notBelow=notBelow,
		#	lastMatch=stateMatch,
		#	_isBegin=False,
		#	_moves=_moves+bfs2moveSeq(bfs,x[1][0][0]),_rtvMoves=_rtvMoves,
		#	_nodes=_nodes+[x[0]],_rtvNodes=_rtvNodes,
		#	verbose=verbose) for x in matches if not (x[1][0][0],x[0]) in lastMatch ]

		for x in matches:
			if len(_rtvMoves)!=0:
				# route to goal found
				break
			if (x[1][0][0],x[0]) in lastMatch:
				# (statehash,matchGoalName) seen
				continue
			genSol(x[1][0][1][0],gt,step,stateLimit=stateLimit,currStep=x[1][0][1][1],
				notBelow=notBelow,
				lastMatch=stateMatch,
				_isBegin=False,
				_moves=_moves+bfs2moveSeq(bfs,x[1][0][0]),_rtvMoves=_rtvMoves,
				_nodes=_nodes+[x[0]],_rtvNodes=_rtvNodes,
				verbose=verbose)
		
		#return res
	if _isBegin:
		return {"moves":_rtvMoves,"nodes":_rtvNodes}

