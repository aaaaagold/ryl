#!/bin/python3
import re
#import decimal

from shorthand import *
from amyhead import *

from aexpand import *

token_itemWithouLabelSplit=r"([0-9]+|" + charset_namespace + r"):([^ \b\t\n\r]+)"
parser_itemWithouLabelSplit=re.compile(token_itemWithouLabelSplit)
token_itemVal_number=r"(-?[0-9]+\.?[0-9]*)"
token_itemVal_rangeNum=token_itemVal_number+r","+token_itemVal_number
parser_itemVal_rangeNum=re.compile(r"^"+token_itemVal_rangeNum+r"$")

def matchGoal_v4(b,g):
	oarr=b.outputs()
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
			#p=re.compile(r"([0-9]+):([^ \b\t\n\r]+)")
			p=parser_itemWithouLabelSplit
			item=p.split(str(x[1])) # may have several constraints, just one of them
			for i in range(1,len(item),p.groups+1):
				err=False
				isDirect=item[i].isdigit()
				if isDirect:
					#view = int(item[i])
					observedVal = oarr[int(item[i])]
				elif (not isNone(g.extendedView)) and hasattr(g.extendedView,item[i]):
					#view = getattr(g.extendedView,item[i])
					observedVal = getattr(g.extendedView,item[i])(oarr)
				else:
					print("WARNING: cannot find",item[i])
					print("\t constraint omitted")
					err=True
				#print(observedVal),exit() # debug
				if err: matched=not negate
				else:
					targetVal = item[i+1]
					isOneObj=True
					# min,max
					p=parser_itemVal_rangeNum
					try_rangeNum=p.split(targetVal)
					if len(try_rangeNum)==p.groups+2:
						# is rangeNum: matched exactly 1
						isOneObj=False
						rg=[ float(n) for n in try_rangeNum[1:3] ]
						if rg[0]<=observedVal<=rg[1]:
							matched=True
							break
					# a string
					if isOneObj and str(observedVal)==str(targetVal):
						matched=True
						break
				####
		#if (negate!=False and matched!=False) or (matched==False and negate==False):
		if negate==matched:
			return False
	return True

matchGoal=matchGoal_v4

def matchGoaltree_find_inSet(b,goals):
	for g in goals:
		res=matchGoal(b,g)
		if res!=0:
			return res
	return False

def matchGoaltree_trim_v3(mv,gt):
	# preserve topest matched node(s)
	# i.e. trim below node(s)
	#mv=list(set(mv))
	mv=[ x for x in mv ]
	mv.sort()
	mv=[ mv[i] for i in range(len(mv)) if i==0 or mv[i-1]!=mv[i] ]
	sv=[ (gt.getSuccsStr(k),k) for k in mv]
	# TODO?: need suffix array to speedup
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

def matchGoaltree_trim_selectPossible(possibleV,gt):
	rtv=[]
	tmparr=[]
	lessNode={}
	for p in possibleV:
		if len(p)==0: continue
		if (not p[-1] in lessNode) or len(lessNode[p[-1]])>len(p):
			lessNode[p[-1]]=p
	res=matchGoaltree_trim([ n for n in lessNode ],gt)
	for n in res:
		rtv.append(lessNode[n])
	return rtv

###########

def genSol_v3(b,gt,step=8,stateLimit=4095,currStep=0,
	notBelow=None,
	info={},
	_lastMatches={},_lastMatch="",
	_isBegin=True,
	_moves=[],_rtvMoves=[],
	_nodes=[],_rtvNodes=[],
	_possible=[],
	__internal_data=None,
	shortcut=True,
	endBefore=None,
	verbose=False,
	__lv=0,
	__dummy=None):
	#print("__lv",__lv) # debug
	# init
	genSol=genSol_v3
	#print(_lastMatch) # debug
	if _isBegin:
		del _rtvMoves,_rtvNodes,_possible,__internal_data
		_rtvMoves=[]
		_rtvNodes=[]
		_possible=[]
		__internal_data={
			"finals":gt.getFinals(),
			"fail":{
				"arr":[],
				"set":set(),
				"cnt":info["failmemCnt"] if ("failmemCnt" in info) else 1023
			},
			"__dummy":None}
	# skip by time
	if isNone(endBefore)==False and endBefore<time.time():
		print("skip by time") # debug
		return
	# skip by seen fail
	currentRawBoard=tuple(b.rawBoard())
	if (currentRawBoard,_lastMatch) in __internal_data["fail"]["set"]:
		#print("skip by seen") # debug
		return
	# start
	expInfo={
		"finals":__internal_data["finals"],
		"nodes":_nodes,
		"__dummy":None}
	keys=gt.wkeys(currentKey=_lastMatch,beforeKeys=set(_nodes)) # rtv = [ (weight,nodeName) , ... ]
	if shortcut==False: keys.sort()
	else: keys.sort(reverse=True)
	#if verbose: print("?",keys) # debug
	hvv=[]
	hvv+=gt.pushs(currentKey=_lastMatch)+gt.pulls(currentKey=_lastMatch,wkeys=keys) # it's slow
	# [ [foo1,foo2, ... ] , [foo3,foo4, ... ] , ... ]
	# will be used in min heap, so the value is the smaller the better
	INFO={}
	INFO.update(info)
	INFO.update(expInfo)
	INFO['hvv']=hvv
	#print(INFO) # debug
	# try different heuristic function
	for _ in range(len(hvv)+1):
		#if _!=0: break # debug
		bfsRes=bfs(b,step,stateLimit=stateLimit,notViolate=gt.getGoals('__notViolate'),info=INFO)
		#if _isBegin: print(keys) # debug
		#minProb=keys[len(keys)>>1][0]
		matchesDict={}
		matchedKeys=[]
		#print(keys) # debug
		# verify if a node can match
		for i in range(len(keys)):
			#if keys[i][0]<minProb:
			#	#break
			#	pass
			#	# omit < 50%-th.  # keys is sorted
			key=keys[i][1]
			goalSet=gt.getGoals(key)
			
			# check if it floods to some nodes
			matchedBfsRes=[]
			# go through flooding results
			for i in bfsRes:
				bRes=bfsRes[i]
				if matchGoaltree_find_inSet(bRes[0],goalSet):
					# matched
					if len(matchedBfsRes)==0 or bRes[1]<matchedBfsRes[0][1][1]:
						matchedBfsRes=[(i,bRes)]
					elif bRes[1]==matchedBfsRes[0][1][1]:
						matchedBfsRes.append((i,bRes))
			if len(matchedBfsRes)==0: continue
			#
			# check final
			if key in __internal_data["finals"]:
				_rtvMoves.append(_moves+bfs2moveSeq(bfsRes,matchedBfsRes[0][0]))
				_rtvNodes.append(_nodes+[key])
				break
				pass
			else:
				# find path (dfs)
				#print('***') # debug
				for x in matchedBfsRes:
					#print('*',x) # debug
					# {(stateHash,key):totalStep}
					stateMatch={(x[0],key):currStep+x[1][1]}
					stateMatch.update(_lastMatches)
					genSol(x[1][0],gt,step,stateLimit=stateLimit,currStep=currStep+x[1][1],
						notBelow=notBelow,
						info=info,
						_lastMatches=stateMatch,_lastMatch=key,
						_isBegin=False,
						_moves=_moves+bfs2moveSeq(bfsRes,x[0]),_rtvMoves=_rtvMoves,
						_nodes=_nodes+[key],_rtvNodes=_rtvNodes,
						_possible=_possible,
						__internal_data=__internal_data,
						shortcut=shortcut,
						endBefore=endBefore,
						verbose=verbose,
						__lv=__lv+1)
					if len(_rtvMoves)!=0: break
				#
			if len(_rtvMoves)!=0: break
			#
			# node appearsa, but previously path not found
			matchesDict[key]=matchedBfsRes
			matchedKeys.append(key)
		# nothing match, need adjust or record as best
		if len(_rtvMoves)==0: # try next
			sureFail=False
			if "next" in info:
				# try next
				tryInfo={}
				tryInfo.update(info)
				res=info["next"](tryInfo)
				if res:
					genSol(b,gt,step=step,stateLimit=stateLimit,currStep=currStep,
						notBelow=notBelow,
						info=tryInfo,
						_lastMatches=_lastMatches,_lastMatch=_lastMatch,
						_isBegin=False,
						_moves=_moves,_rtvMoves=_rtvMoves,
						_nodes=_nodes,_rtvNodes=_rtvNodes,
						_possible=_possible,
						__internal_data=__internal_data,
						shortcut=shortcut,
						endBefore=endBefore,
						verbose=verbose,
						__lv=__lv+1)
				else:
					sureFail|=True
				del tryInfo
			else:
				sureFail|=True
			if sureFail:
				# fail situation cache
				failinfo=__internal_data["fail"]
				failkey=(currentRawBoard,_lastMatch)
				heappush(failinfo["arr"],(time.time(),failkey))
				failinfo["set"].add(failkey)
				while len(failinfo["set"])>failinfo["cnt"]:
					tmp=heappop(failinfo["arr"])
					failinfo["set"].remove(tmp[1])
				# record possible
				_possible.append(_nodes+[key])
				newPoss=matchGoaltree_trim_selectPossible(_possible,gt)
				_possible.clear()
				_possible.extend(newPoss)
	del expInfo,INFO ####
	if len(_rtvMoves)==0: # after try next
		#print(_lastMatch) # debug
		# all candidate nodes cannot find a path to final(s)
		if verbose:
			print("GG",_nodes,len(hvv)) # debug
			b.print()
	if _isBegin:
		return {"moves":_rtvMoves,"nodes":_rtvNodes,"possible":_possible}
	# END OF FUNC.

genSol=genSol_v3

