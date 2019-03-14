#!/bin/python3
import sys
import copy
import time

from ag import *
#from ab import *
from a15p_rev import *
#from ab2g import *
from asol import *

xxx=Goaltree()
xxx.fromTxt("ainput-15p-rev/main.txt")
bbb=board((4,4))

def test(n,qv,gt,hweights=[],opts={}):
	steps=opts["steps"] if "steps" in opts else 2323
	stateLimit=opts["stateLimit"] if "stateLimit" in opts else 4095
	rtv=0 # meaning: step # sum or max
	wh=(n,n)
	
	arr=[]
	for i in range(0,n*n,n+1):
		if i&1:
			for x in range((i//n+1)*n-1,i-1,-1):
				arr.append([x])
			for x in range(i+n,n*n,n):
				arr.append([x])
		else:
			for x in range(n*n+i%n-n,i+n-1,-n):
				arr.append([x])
			for x in range(i,(i//n+1)*n):
				arr.append([x])
		#arr.append([i])
		#s=set()
		#for x in range(i+1,(i//n+1)*n): s.add(x)
		#for x in range(i+n,n*n,n): s.add(x)
		#if len(s)!=0: arr.append(list(s))
	
	edge=[x for x in arr[::-1] if len(x)!=0]
	print(edge)
	wtbl={}
	for i in range(len(edge)):
		arr=edge[i]
		for e in arr:
			wtbl[e]=i*hweights[i]+1
	print(wtbl)
	def h(b):
		rtv=0
		sz=1
		for i in wh: sz*=i
		for i in range(sz):
			p=b[i]
			xy=[p%wh[0],p//wh[1]]
			to=[i%wh[0],i//wh[1]]
			distance=int(sum([abs(to[i]-xy[i]) for i in range(2)]))
			rtv+=wtbl[i]**distance
		return rtv
	pulls=gt.sets['Final'][5]['-pull'][1]
	pulls.clear()
	pulls.append([h])
	for q in qv:
		res=genSol_v3(q,gt,step=steps,stateLimit=stateLimit,verbose=True)
		if len(res['moves'])==0: rtv+=steps+1
		else: rtv+=min([len(mv) for mv in res['moves']])
	return rtv

goldRate=(5**0.5-1)/2

class idv:
	def __init__(self,w=0,sz=1):
		self.w=[random.random()*w+1 for _ in range(sz)]
	def copy(self):
		rtv=self.__class__(sz=len(self.w))
		rtv.w=[w for w in self.w]
		return rtv
	def __lt__(self,rhs):
		return False
	def reserve(self,sz,w=1):
		for _ in range(len(self.w),sz):
			self.w.append(random.random()*w)
		return self
	def mutate(self):
		r=random.random()+goldRate
		self.w=[random.random()*w+goldRate for w in self.w]
		self.w=[w+random.random() for w in self.w]
		self.w=[0 if w<0 else w for w in self.w]
		return self
	def cross(self,rhs):
		for i in range(len(self.w)):
			if random.random()<0.5:
				self.w[i]=rhs.w[i]
		return self

def test2(gt,psize=11):
	maxstep=2323
	pop=[ [None,idv(),0] ]
	for n in range(2,7):
		for p in pop: p[1].reserve(n*n)
		gs=gt.sets['Final'][0]
		gs.clear()
		g=Goal()
		for i in range(n*n): g.add(item=str(i)+":"+str(i),label=0)
		gs.append(g)
		bbb=board((n,n))
		for _ in range(11):
			print("size",n)
			print("batch",_)
			# split cases
			qv=[bbb.random().copy() for _ in range(1+(n+_)*2)]
			print("qv done")
			# clear results
			for p in pop: p[0]=None
			print("result cleaned")
			for rud in range(3):
				print("round",rud)
				newpop=[]
				newpop+=pop
				while len(newpop)<psize:
					p=random.choice(pop)
					ch=p[1].copy()
					tmp=[None]
					if len(pop)>1 and random.random()>0.5:
						ch2=random.choice(pop)[1]
						tmp+=[ch.cross(ch2)]
					else:
						tmp+=[ch.mutate()]
					tmp+=[p[2]+1]
					newpop.append(tmp)
				print("new pop done")
				for i in range(len(newpop)):
					p=newpop[i]
					if not isNone(p[0]): continue
					print("P",i)
					res=test(n,qv,gt,hweights=p[1].w,opts={"steps":maxstep})
					p[0]=res
					print(res)
				print("score done")
				newpop.sort()
				pop=newpop[:int(len(newpop)//3)]
				print("best",newpop[0],newpop[2])
			pass
		pass
	pass

if 0==0 or (len(sys.argv)>1 and sys.argv[1]=="1demo"):
	#for k in xxx.sets:
	#	if k!='Final':
	#		print(xxx.sets[k][5])
	delArr=[k for k in xxx.sets if k!='Final']
	for k in delArr: del xxx.sets[k]
	test2(xxx),exit()

