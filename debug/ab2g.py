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

