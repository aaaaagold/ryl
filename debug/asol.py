#!/bin/python3
import re

from shorthand import *
from amyhead import *

from aexpand import *

token_itemWithouLabelSplit="([0-9]+):([^ \b\t\n\r]+)"
parser_itemWithouLabelSplit=re.compile(token_itemWithouLabelSplit)

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
			#p=re.compile("([0-9]+):([^ \b\t\n\r]+)")
			p=parser_itemWithouLabelSplit
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

def matchGoal_v4(b,g):
	barr=b.rawBoard()
	for x in g.constraints:
		isKW=False
		negate=x[2]
		matched=False # if a cosntraint is matched
		if x[0]==g.__class__.KW_include_label:
			isKW=True
			for name in x[1][1].getFinals():
				goals=x[1][1].getGoals(name)
				if matchGoaltree_find_inSet(b,goals):
					matched=True
					break
		if isKW==False:
			#p=re.compile("([0-9]+):([^ \b\t\n\r]+)")
			p=parser_itemWithouLabelSplit
			item=p.split(str(x[1])) # may have several constraints, just one of them
			for i in range(1,len(item),p.groups+1):
				loc = int(item[i  ])
				pn  = item[i+1]
				if str(barr[loc])==str(pn):
					matched=True
					break
		#if (negate!=False and matched!=False) or (matched==False and negate==False):
		if negate==matched:
			return False
	return True

matchGoal=matchGoal_v4

def matchGoaltree_find_inSet(b,goals):
	for g in goals:
		if matchGoal(b,g):
			return True
	return False

def matchGoaltree_find(b,gt,notBelow=None):
	#barr=b.rawBoard()
	rtv=[]
	for k in gt.keys(notBelow=notBelow):
		if matchGoaltree_find_inSet(b,gt.getGoals(k)):
			rtv.append(k)
	return rtv

def matchGoaltree_trim_v1(mv,gt):
	#mv=set(mv)
	mv=[ x for x in mv ]
	mv.sort()
	mv=[ mv[i] for i in range(len(mv)) if i==0 or mv[i-1]!=mv[i] ]
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

def matchGoaltree_trim_v2(mv,gt):
	#mv=set(mv)
	mv=[ x for x in mv ]
	mv.sort()
	mv=[ mv[i] for i in range(len(mv)) if i==0 or mv[i-1]!=mv[i] ]
	sv=[ (gt.getSuccs(k)|set([k]),k) for k in mv]
	#rtv=[]
	delSet=set()
	rg=range(len(sv))
	for i1 in rg:
		for i2 in rg:
			if i1==i2: continue
			s1,s2 = sv[i1][0],sv[i2][0]
			ss=s1&s2
			if len(ss)==len(s1): delSet.add(sv[i2][1])
			#if len(ss)==len(s2): delSet.add(sv[i1][1])
			del s1,s2,ss
	rtv=[ k for k in mv if not k in delSet ]
	return rtv

def matchGoaltree_trim_v3(mv,gt):
	#mv=list(set(mv))
	mv=[ x for x in mv ]
	mv.sort()
	mv=[ mv[i] for i in range(len(mv)) if i==0 or mv[i-1]!=mv[i] ]
	sv=[ (gt.getSuccsStr(k),k) for k in mv]
	# TODO: need suffix array to speedup
	rg=range(len(mv))
	delSet=set()
	for i1 in rg:
		for i2 in rg:
			if i1==i2: continue
			s1,s2 = sv[i1],sv[i2]
			if s1[0] in s2[0]:
				delSet.add(s2[1])
			del s1,s2
	rtv=[ k for k in mv if not k in delSet]
	return rtv

matchGoaltree_trim=matchGoaltree_trim_v3
# arg: match-v, goaltree

def matchGoaltree(b,gt,notBelow=None):
	return matchGoaltree_trim(matchGoaltree_find(b,gt,notBelow),gt)

def matchGoaltree_checkNegate(b,gt,k):
	pass

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
	'''
		the function tries to match every results in limited bfs with a goal in gt.
		if a goal is matched with by several results, it will choose the one with the least steps.
		several results may be chosen if they have same steps.
		stored in rtvM2b (i.e. rtv,matches to board)
		;
		problem: whole-goals search takes time.  nevertheless this will be operated after each limited bfs.
		;
		the upper layer function takes the result and choose the topper (of the goal tree) one
		;
		;
		want the first choose is correct and do not need to match others in the same bfs results.
	'''
	#bfsRes=b.bfs(8)
	matches=[]
	rtvM2b={}
	for i in bfsRes:
		bRes=bfsRes[i]
		mv=matchGoaltree(bRes[0],gt,notBelow) # try not match all, use previous experiences
		mvt=mv #mvt=matchGoaltree_trim(mv,gt) # matchGoaltree_trim is in matchGoaltree
		matches+=mvt
		for m in mvt:
			if (not m in rtvM2b) or len(rtvM2b[m])==0 or (bRes[1]<rtvM2b[m][0][1][1]):
				rtvM2b[m]=[(i,bRes)]
			elif rtvM2b[m][0][1][1]==bRes[1]:
				rtvM2b[m].append((i,bRes))
	rtvMv=matchGoaltree_trim(matches,gt)
	#return rtvMv
	rtv = [ (m,rtvM2b[m]) for m in rtvMv ] # [ (goalName,[ (stateHash,bfsRes[stateHash]) ... ]) ... ]
	return rtv

# TODO: try fixedBlockIts if unable to reach next subgoal
def genSol_1(b,gt,step=8,stateLimit=4095,notBelow=None,fixedBlockIts=[]):
	# return: [ (goalName,[ (stateNum,(state,stepCnt,(move,stateNum))), ]) ]
	#bfsRes=b.bfs(step,stateLimit=stateLimit,notViolate=gt.getGoals('__notViolate'))
	bfsRes=bfs(b,step,stateLimit=stateLimit,notViolate=gt.getGoals('__notViolate'))
	mvb=genSol_bfsTopMatch(bfsRes,gt,notBelow)
	#return ([ (k,genSol_bfsMatchStates(bfsRes,gt.getGoals(k))) for k in mv ],bfsRes)
	return (mvb,bfsRes)

def genSol_v1(b,gt,step=8,stateLimit=4095,currStep=0,fixedBlockIts=[],
	notBelow=None,
	lastMatch=set(),
	_isBegin=True,
	_moves=[],_rtvMoves=[],
	_nodes=[],_rtvNodes=[],
	_possible=[],
	verbose=False,
	__internal_data=None,
	__dummy=None):
	genSol=genSol_v1
	if _isBegin:
		del _rtvMoves,_rtvNodes,_possible
		_rtvMoves=[]
		_rtvNodes=[]
		_possible=[]
	#verbose=True # debug
	#if verbose: print('_moves',_moves) # debug
	#immediateMatched=matchGoaltree(b,gt,notBelow)
	#notBelow = None if len(immediateMatched)==0 else set(immediateMatched)
	#if verbose: print('genSol',immediateMatched) # debug
	if verbose: print('genSol',lastMatch) # debug
	if verbose: b.print() # debug
	finalGoals=gt.getFinals()
	matches,bfsRes=genSol_1(b,gt,step,stateLimit,notBelow=notBelow)
	if 0==0:
		pass
		# TODO
		'''
			change matches to 
				for g in goals:
					if not match(g): continue
			the order of goals is decided by experience
			therefore, the following judge should be rewrited
		'''
	stateMatch=set([ (b[0],m[0]) for m in matches for b in m[1] ])
	#stateMatch.sort()
	goalsInFinals=[ x for x in matches if x[0] in finalGoals ]
	if len(goalsInFinals)!=0:
		minDistItem=min(goalsInFinals,key=(lambda x:x[1][0][1][1]))
		if verbose: print('goal!',minDistItem) # debug
		if verbose: minDistItem[1][0][1][0].print() # debug
		_rtvMoves.append(_moves+bfs2moveSeq(bfsRes,minDistItem[1][0][0]))
		_rtvNodes.append(_nodes+[minDistItem[0]])
		#return [minDistItem]
	else:
		#res=[ genSol(bfsNode[1][0],gt,step,stateLimit=stateLimit,currStep=bfsNode[1][1],
		#	notBelow=notBelow,
		#	lastMatch=stateMatch,
		#	_isBegin=False,
		#	_moves=_moves+bfs2moveSeq(bfsRes,bfsNode[0]),_rtvMoves=_rtvMoves,
		#	_nodes=_nodes+[x[0]],_rtvNodes=_rtvNodes,
		#	verbose=verbose) for x in matches if not x[0] in immediateMatched for bfsNode in x[1] ]
		
		#res=[ genSol(x[1][0][1][0],gt,step,stateLimit=stateLimit,currStep=x[1][0][1][1],
		#	notBelow=notBelow,
		#	lastMatch=stateMatch,
		#	_isBegin=False,
		#	_moves=_moves+bfs2moveSeq(bfsRes,x[1][0][0]),_rtvMoves=_rtvMoves,
		#	_nodes=_nodes+[x[0]],_rtvNodes=_rtvNodes,
		#	verbose=verbose) for x in matches if not x[0] in immediateMatched]
		
		#res=[ genSol(x[1][0][1][0],gt,step,stateLimit=stateLimit,currStep=x[1][0][1][1],
		#	notBelow=notBelow,
		#	lastMatch=stateMatch,
		#	_isBegin=False,
		#	_moves=_moves+bfs2moveSeq(bfsRes,x[1][0][0]),_rtvMoves=_rtvMoves,
		#	_nodes=_nodes+[x[0]],_rtvNodes=_rtvNodes,
		#	verbose=verbose) for x in matches if not (x[1][0][0],x[0]) in lastMatch ]
		
		# TODO
		'''
			change to 
				for g in goals:
					if not match(g): continue
			the order of goals is decided by experience
		'''

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
				_moves=_moves+bfs2moveSeq(bfsRes,x[1][0][0]),_rtvMoves=_rtvMoves,
				_nodes=_nodes+[x[0]],_rtvNodes=_rtvNodes,
				_possible=_possible,
				verbose=verbose)
		if len(_rtvMoves)==0 and len(_moves)!=0:
			_possible.append(_moves)
		
		#return res
	if _isBegin:
		return {"moves":_rtvMoves,"nodes":_rtvNodes,"possible":_possible}

def genSol_v2(b,gt,step=8,stateLimit=4095,currStep=0,fixedBlockIts=[],
	notBelow=None,
	_lastMatches={},_lastMatch="",
	_isBegin=True,
	_moves=[],_rtvMoves=[],
	_nodes=[],_rtvNodes=[],
	_possible=[],
	__internal_data=None,
	verbose=False,
	__dummy=None):
	genSol=genSol_v2
	if _isBegin:
		del _rtvMoves,_rtvNodes,_possible,__internal_data
		_rtvMoves=[]
		_rtvNodes=[]
		_possible=[]
		__internal_data={
			"finals":gt.getFinals(),
			"__dummy":None}
	bfsRes=bfs(b,step,stateLimit=stateLimit,notViolate=gt.getGoals('__notViolate'))
	keys=gt.wkeys(_lastMatch) # [ (weight,nodeName) , ... ]
	keys.sort(reverse=True)
	minProb=keys[len(keys)>>1][0]
	matchesDict={}
	matchedKeys=[]
	for i in range(len(keys)):
		if keys[i][0]<minProb:
			break
			# omit < 50%-th.  # keys is sorted
		key=keys[i][1]
		goalSet=gt.getGoals(key)
		
		#matches=genSol_bfsTopMatch(bfsRes,gt,notBelow)
		matchedBfsRes=[]
		for i in bfsRes:
			bRes=bfsRes[i]
			#mv=matchGoaltree(bRes[0],gt,notBelow) # try not match all, use previous experiences
			if matchGoaltree_find_inSet(bRes[0],goalSet):
				# matched
				if len(matchedBfsRes)==0 or bRes[1]<matchedBfsRes[0][1][1]:
					matchedBfsRes=[(i,bRes)]
				elif bRes[1]==matchedBfsRes[0][1][1]:
					matchedBfsRes.append((i,bRes))
		if len(matchedBfsRes)!=0:
			matchesDict[key]=matchedBfsRes
			matchedKeys.append(key)

		# choose only upper nodes
		betterMatchedKeys=set(matchGoaltree_trim(matchedKeys,gt))
		delSet=set()
		for k in matchesDict:
			if k not in betterMatchedKeys:
				delSet.add(k)
		matches=[ (k,matchesDict[k]) for k in matchesDict if not k in delSet ]
		#
		
		# check if reach final
		hasFinals=[ x for x in matches if x[0] in __internal_data["finals"] ]
		if len(hasFinals):
			minDistItem=min(hasFinals,key=(lambda x:x[1][0][1][1]))
			if verbose: print('goal!',minDistItem) # debug
			if verbose: minDistItem[1][0][1][0].print() # debug
			_rtvMoves.append(_moves+bfs2moveSeq(bfsRes,minDistItem[1][0][0]))
			_rtvNodes.append(_nodes+[minDistItem[0]])
			#break
		#
		#stateMatch=set([ (b[0],m[0]) for m in matches for b in m[1] ])
		stateMatch=dict([ ((b[0],m[0]),b[1][1]) for m in matches for b in m[1] ])
		# TODO: add step record to stateMatch
		# find path (dfs)
		for x in matches:
			if len(_rtvMoves)!=0:
				# route to goal found
				break
			curr_record=(x[1][0][0],x[0])
			if curr_record in _lastMatches and _lastMatches[curr_record]<stateMatch[curr_record]:
				# (statehash,matchGoalName) seen
				continue
			genSol(x[1][0][1][0],gt,step,stateLimit=stateLimit,currStep=x[1][0][1][1],
				notBelow=notBelow,
				_lastMatches=stateMatch,_lastMatch=x[0],
				_isBegin=False,
				_moves=_moves+bfs2moveSeq(bfsRes,x[1][0][0]),_rtvMoves=_rtvMoves,
				_nodes=_nodes+[x[0]],_rtvNodes=_rtvNodes,
				_possible=_possible,
				__internal_data=__internal_data,
				verbose=verbose)
		#
		if len(_rtvMoves)==0 and len(_moves)!=0:
			_possible.append(_moves)
	
	if _isBegin:
		return {"moves":_rtvMoves,"nodes":_rtvNodes,"possible":_possible}
	# END OF FUNC.

genSol=genSol_v2

