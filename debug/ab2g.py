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

def matchGoal(b,g):
	barr=b.rawBoard()
	for x in g.constraints:
		if str(barr[x[0]])!=str(x[1]):
			return False
	return True

def matchGoaltree_find(b,gt):
	barr=b.rawBoard()
	rtv=[]
	for k in gt.keys():
		for g in gt.getGoals(k):
			if matchGoal(b,g):
				rtv.append(k)
				break
	return rtv

def matchGoaltree_trim(mv,gt):
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

def genSol(b,gt):
	# TODO
	pass

