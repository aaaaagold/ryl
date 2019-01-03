#!/bin/python3
import sys
import copy
import time

from ag import *
from asol import *

from afunc import *

xxxv=[]
for i in range(3):
	xxx=goaltree()
	xxx.fromTxt("ainput-func/t"+str(i)+"/main.txt")
	print("#end")
	print("finals:",xxx.getFinals())
	print("size:",xxx.size())
	xxxv.append(xxx)
foo=func(x_init=[0],coef_X=[2,-3],coef_T=[5],copyArg=False)
def moving(movesS,foo):
	#movesS=res['moves']
	print(movesS)
	#nodesS=res['nodes']
	for msg in movesS[0]:
		print("msg")
		print(msg)
		move=msg[1]
		time.sleep(0.25)
		foo.move(move)
		print("board")
		foo.print()
		print()
	
def move1(xxx,foo,info={},rtv={}):
	#foo.random()
	#while bbb.solvable()==False: bbb.random()
	#arr=[1, 3, 7, 12, 5, 15, 10, 0, 2, 4, 8, 11, 9, 6, 13, 14]
	#arr=[12, 8, 7, 6, 9, 13, 15, 3, 0, 1, 11, 10, 2, 14, 5, 4]
	#bbb.setNums(arr,arr.index(15))
	foo.print(end='\n')
	#print(foo.rawBoard())
	t0=time.time()
	res=genSol_v3(foo,xxx,step=8,stateLimit=4095,info=info,verbose=True)
	print(time.time()-t0)
	rtv['res']=res
	if len(res['moves'])==0:
		print("GGGG")
		print(res)
		return True
	else:
		moving(res['moves'],foo)
	return False
if 0!=0 or (len(sys.argv)>1 and sys.argv[1]=="1demo"):
	moves=[]
	nodes=[]
	possi=[]
	prcs=[]
	t0=time.time()
	for i in range(len(xxxv)):
		print("xxxv",i)
		res={}
		tmp_possi=[]
		err=True
		info={"precision":2**3}
		for _ in range(11):
			flag=move1(xxxv[i],foo,info=info,rtv=res)
			err&=flag
			if flag==False: break
			info["precision"]/=2.0
			tmp_possi.append(res['res']['possible'])
		tmp_possi=matchGoaltree_trim_selectPossible(tmp_possi,xxxv[i])
		if err:
			possi.append(tmp_possi)
			break
		else: tmp_possi=[]
		nodes.append(res['res']['nodes'][0])
		moves.append(res['res']['moves'][0])
		possi.append(tmp_possi)
		prcs.append(info["precision"])
		foo.nextStage()
	from pprint import pprint
	pprint(nodes)
	pprint(moves)
	pprint(possi)
	pprint(prcs)
	t1=time.time()
	print("time:",t1-t0,"sec.")
	exit()
# TODO

