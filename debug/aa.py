#!/bin/python3
import copy
import random
import sys
from ab import *

class A:
	def __init__(self,constraints=None):
		self.__rawc=[]
		self.reset(constraints)
	def __eq__(self,rhs):
		rtv=len(self.__rawc)==len(rhs.__rawc) and len(self.__ord)==len(rhs.__ord)
		if rtv:
			for ii in range(len(self.__ord)):
				(arr1,arr2)=(self.__ord[ii],rhs.__ord[ii])
				arr1.sort()
				arr2.sort()
				if arr1!=arr2: return False
		return rtv
	def same(self,rhs,satCnt=None):
		# satCnt: prefix satisfied
		rtv=len(self.__rawc)==len(rhs.__rawc)
		if rtv:
			if not satCnt>0:
				return self==rhs
			else:
				cnt=0
				for ii in range(len(self.__ord)):
					(arr1,arr2)=(self.__ord[ii],rhs.__ord[ii])
					arr1.sort()
					arr2.sort()
					if arr1!=arr2: return False
					cnt+=len(arr2)
					if cnt>=satCnt: return True
		return rtv
		pass
	def __arrange_ord(self):
		neword=[ x for x in self.__ord if len(x)!=0 ]
		#print("a b",self.__ord)
		self.__ord=neword
		#print("a a",self.__ord)
	def copy(self):
		rtv=A()
		rtv.__rawc=copy.deepcopy(self.__rawc)
		rtv.__ord=copy.deepcopy(self.__ord)
	def reset_from_ord(self,ordarr):
		self.__ord=copy.deepcopy(ordarr)
		pass
		#self.__sub=[[] for _ in range(len(self.__ord))] # used when unable to use self.__ord only to solve
		#self.lastv=[] # used by next layer when idv change to be able to solve, train nn( i:history[n];o:history[n+1] )
	def reset(self,constraints=None,p=0.5):
		if type(constraints)==type([]):
			self.__rawc=[ x for x in constraints ]
			for i in range(len(self.__rawc)**2):
				ch1=int(random.random()*len(self.__rawc))
				ch2=int(random.random()*len(self.__rawc))
				(self.__rawc[ch1],self.__rawc[ch2]) = (self.__rawc[ch2],self.__rawc[ch1])
		ordarr=[]
		tmp=[]
		for c in self.__rawc:
			tmp.append(c)
			if random.random()<p:
				ordarr.append(tmp)
				tmp=[]
		if len(tmp)!=0:
			ordarr.append(tmp)
		self.reset_from_ord(ordarr)
	def rawOrd(self):
		return self.__ord
	def mutate1(self,p=0.5):
		# choose C
		tmps=set()
		for arr in self.__ord:
			for x in arr:
				if random.random()<p:
					tmps.add(x)
		#print("m",tmp) # debug
		if len(tmps)==0: return
		# remove C from self.__ord
		for i in range(len(self.__ord)):
			arr=self.__ord[i]
			tmpv=[]
			for x in arr:
				if not x in tmps:
					tmpv.append(x)
			arr.clear()
			self.__ord[i]=tmpv
			del tmpv,arr
		# clear empty
		self.__arrange_ord()
		# put C to arbitary place
		ch=int(random.random()*((len(self.__ord)<<1)|1))
		if (ch&1)!=0:
			ch>>=1
			for x in tmps: self.__ord[ch].append(x)
		else:
			ch>>=1
			neword=[]
			for i in range(ch): neword.append(self.__ord[i])
			neword.append([x for x in tmps])
			for i in range(ch,len(self.__ord)): neword.append(self.__ord[i])
			self.__ord=neword
	def mutate(self,p=0.5):
		for _ in range(len(self.__rawc)):
			self.mutate1(p)
	def cross(self,rhs):
		# one-point crossover
		cut=int(random.randint(0,len(rhs.__ord))) # [,]
		#print("c",cut) # debug
		refer=[ rhs.__ord[i] for i in range(cut) ]
		chc=set()
		for arr in refer:
			for x in arr:
				chc.add(x)
		for i in range(len(self.__ord)):
			arr=self.__ord[i]
			tmp=[]
			for x in arr:
				if not x in chc:
					tmp.append(x)
			arr.clear()
			for x in tmp: arr.append(x)
			del tmp,arr
		self.__arrange_ord()
		self.__ord=copy.deepcopy(refer)+self.__ord
	def __genSubgoal1(self,goal,dontcare,fixed):
		tmpgoal=goal.copy()
		tmpgoal.setDontcare(dontcare)
		return (tmpgoal,[goal.rawBoard()[i] for i in dontcare],fixed)
		# ( fuzzy state, the dontcare numbers presented on board, fixed loc)
	def __genSubgoal(self,goal):
		# gen all subgoal according to self.__ord
		rtv=[]
		sz=goal.size()
		allIts=set()
		for i in range(sz): allIts.add(i)
		cs=set()
		cspre=set() # fixedBlockIts
		for i in range(len(self.__ord)):
			for j in self.__ord[i]:
				cs.add(j)
			rtv.append(self.__genSubgoal1(goal,cs^allIts,cspre))
			del cspre
			cspre=copy.deepcopy(cs)
		del cspre,cs,allIts,sz
		return rtv
	def __findsol_ord1(self,curr,g,numOf_evalStates=4095):
		# will move curr if success
		rtvm=[]
		# g[0] = goal state, empty=dontcare
		# g[1] = list(dontcare numbers)
		# g[2] = set(fixedBlockIts)
		hg=g[0].hash()
		#print("goal dontcare"),g[0].print() # debug
		# dontcare set current
		ds_curr=set()
		for i in range(curr.size()):
			if curr.rawBoard()[i] in g[1]:
				ds_curr.add(i)
		tmpcurr=curr.copy()
		tmpcurr.setDontcare(ds_curr,True)
		#print("curr dontcare"),tmpcurr.print() # debug
		res=tmpcurr.bfs(step=111,fixedBlockIts=g[2],stateLimit=numOf_evalStates)
		# statHash => (stat,stepCnt,(move,prevstat))
		tmpres={}
		# (originalHash,(stat,step,(move,prevstat)) )
		for i in res:
			tmpstat=res[i][0].copy()
			tmpstat.setDontcare([tmpstat.emptyAt()])
			h=tmpstat.hash()
			if (not h in tmpres) or tmpres[h][1][1]>res[i][1]: tmpres[h]=(i,res[i])
		if not hg in tmpres: return (len(self.__rawc)-len(g[2]),rtvm,tmpcurr) # (howManyNotFixed,
		moves=bfs2moveSeq(res,tmpres[hg][0])
		#print(moves) # debug
		for m in moves:
			curr.move(m)
			rtvm.append(m)
			#curr.print('\n') # debug
		#print("found"),curr.print() # debug
		#exit() # debug
		return (0,rtvm,tmpcurr)
	def __findsol_ord(self,strt,goal,numOf_evalStates=4095):
		rtvm=[]
		curr=strt.copy()
		gv=self.__genSubgoal(goal)
		# divide and conquer
		for ig in range(len(gv)):
			g=gv[ig]
			# g[0] = goal state, empty=dontcare
			# g[1] = list(dontcare numbers)
			# g[2] = set(fixedBlockIts)
			res=self.__findsol_ord1(curr,g,numOf_evalStates) # will move curr if success
			if res[0]!=0: return (res[0],rtvm,(res[2],gv,ig)) # (howManyNotFixed,
			rtvm+=res[1]
			del res
		return (0,rtvm,(curr,gv,len(gv))) # (0,moves,())
	def findmove1block(self,curr,g):
		pass
	def __findsol_mid(self,strt,goal,g,remain=4):
		pass
	def findsol_mid(self,curr,goal,g,cnt=7,tries=11):
		if cnt<3:
			self.__findsol(curr,goal)
			pass
		cnt-=1 # current node cost 1
		tmpmidv=[]
		for _ in range(tries):
			# choose mid
			# try going to mid chosen
			#	self.__findsol(curr,midl)
			# if fail: next level
			#	self.findsol_mid(self,curr,tmpmid,g,cnt>>1)
			# if finally succeed: # good
			# try going to goal
			#	self.__findsol(mid,goal)
			# if fail: next level
			#	#update cnt
			#	remained_cnt
			#	# remained cnt for right subtree
			#	self.findsol_mid(self,tmpmid,goal,g,remained_cnt)
			# if finally succeed: learn how to choose
			#	???
			break
			#try
			tmpmid # current node
			# half of cnt for left subtree
			self.findsol_mid(self,curr,tmpmid,g,cnt>>1)
			if not found: continue
			#update cnt
			remained_cnt
			# remained cnt for right subtree
			self.findsol_mid(self,tmpmid,goal,g,remained_cnt)
			if found: break
		return tmpmidv
	def findsol(self,strt,goal,numOf_evalStates=4095):
		rtv=self.__findsol_ord(strt,goal,numOf_evalStates)
		(remained,rtvm,(tmpcurr,gv,ig))=rtv
		if remained!=0:
			#self.findmid(tmpcurr,gv[ig])
			# record subgoals to self.__sub if found
			#if found: self.__sub[ig]
			pass
		return (rtv[0],rtv[1])
	def printord(self):
		print(self.__ord)
	def logact(self,act):
		pass
	
class P:
	def __init__(self,sz,constraints):
		if sz<1: sz=1
		# basic
		self.sz=sz
		self.genId=1
		self.constraintsOri=[i for i in constraints]
		self.av=[([len(constraints),0,0],A(constraints)) for i in range(sz)] # individuals
		#[ ([restMatchCnt,restMatchCnt if fail else stepCnt,-genId],A()) ]
		#[].sort()
		#? max,min,unchanged
		# for nn
		'''
		'''
	def score(self,b,ans,numOf_evalStates=4095):
		# nn
		'''
		'''
		# general
		for i in range(len(self.av)):
			print("A[",i,"]")
			a=self.av[i] # i-th individual
			#for b in bv:
			if 0==0:
				q=b.copy()
				res=a[1].findsol(q,ans,numOf_evalStates)
				#a[0][0]=1-res[0] # edit
				a[0][0]=res[0] # edit
				#print('','',"fail" if res[0]==False else "succ")
				'''
				# edit
				if res[0]==0: a[0][1]=len(res[1]) # edit
				else:
					if len(res[1])==0: a[0][1]=0
					else:
						q.moveSeq(res[1],verbose=False)
						a[0][1]=-q.sameCnt(ans,self.constraintsOri)
				'''
				if res[0]!=0: a[0][1]=res[0]
				else: a[0][1]=len(res[1])
			print('',a[0],a[1].rawOrd()) # ('',(howManyNotFixed,howManyNotFixed or len(moves),-serial),
			del a
	def next(self,rsrvRate=0.25):
		if rsrvRate>1: rsrvRate=1
		rsrv=int(self.sz*rsrvRate)
		if rsrv<0: rsrv=0
		self.av.sort(key=lambda x:x[0])
		chit=1
		newav=[self.av[chit-1]]
		while len(newav)<rsrv and chit<len(self.av):
			# find if self.av[chit] exists
			existIt=-1
			for i in range(len(newav)):
				if newav[i][1].same(self.av[chit][1],len(self.constraintsOri)-newav[i][0][0]):
					existIt=i
					break
			if existIt==-1:
				# not exist
				newav.append(self.av[chit])
				#elif len(newav[existIt][1].rawOrd())>len(self.av[chit][1].rawOrd()):
				# shorter ord
				#newav[existIt]=self.av[chit]
			elif -newav[existIt][0][2]>-self.av[chit][0][2]:
				# exist but current's age is bigger, change to smaller one
				newav[existIt]=self.av[chit]
			chit+=1
		newavlen=len(newav)
		for _ in range(rsrv):
			tmpA=copy.deepcopy(newav[int(random.random()*newavlen)][1])
			tmpA.mutate()
			newav.append(([len(self.constraintsOri),0,-self.genId],tmpA))
			self.genId+=1
			del tmpA
		for _ in range(rsrv):
			# reversed, take prefix of not so good
			# increase diversity
			tmpA=copy.deepcopy(newav[int(random.random()*newavlen)][1])
			tmpA.cross(self.av[int(random.random()*self.sz)][1])
			newav.append(([len(self.constraintsOri),0,-self.genId],tmpA))
			self.genId+=1
			del tmpA
		del rsrv
		while len(newav)<self.sz:
			newav.append(([len(self.constraintsOri),0,-self.genId],A(self.constraintsOri)))
			self.genId+=1
		self.av=newav
		del newav
	def bestA(self,it=0):
		a=self.av[it]
		return (a[0],a[1].rawOrd())
	def printBest(self):
		print(self.bestA())
	

def main(argv):
	qsz=int(argv[1]) if len(argv)>1 else 11111 # question size
	psz=int(argv[2]) if len(argv)>2 else 33 # population size
	rsz=int(argv[3]) if len(argv)>3 else 111111 # round
	bsz=int(argv[4]) if len(argv)>4 else 4 # edge length
	useAll=argv[5]=='all' if len(argv)>5 else False
	if len(argv)>5 and argv[5]=='test': useAll='test'
	esz=int(argv[6]) if len(argv)>6 else 4095 # #eval_state
	# question
	bi=0
	bv=[board((bsz,bsz))]
	ans=bv[0].copy()
	for _ in range(qsz):
		bv[-1].random()
		tmp=bv[-1].copy()
		if bv[-1].solvable(ans)==False:
			p1=(0,bsz)
			p2=(1,bsz+1)
			p=p2 if bv[-1].emptyAt() in p1 else p1
			bv[-1].swap(p)
			if bv[-1].solvable(ans)==False: bv.pop() #
		bv.append(tmp)
		del tmp
	bv.pop()
	# constraint
	carr=[]
	if 0==0:
		tmps=set()
		for i in range(bsz):
			tmps.add(i*bsz)
			tmps.add(i)
		carr+=[i for i in tmps if i!=ans.emptyAt()]
	if not 0==0:
		tmps=set()
		for i in range(1,bsz):
			tmps.add(i*bsz+1)
			tmps.add(i+bsz)
		carr+=[i for i in tmps if i!=ans.emptyAt()]
	if useAll!=False:
		for i in range(bsz*bsz):
			if i!=ans.emptyAt():
				tmps.add(i)
		carr=[i for i in tmps]
	p=P(psz,carr)
	if useAll=='test':
		arr=p.av[0][1].rawOrd()
		arr.clear()
		for e in range(bsz-1):
			if bsz-e<3:
				tmps=set()
				for x in range(e,bsz):
					tmps.add(x+e*bsz)
					tmps.add(e+x*bsz)
				arr.append([i for i in tmps if i!=ans.emptyAt()])
			else:
				base=e+e*bsz
				length=bsz-e
				cut1=((length-1)>>1)+e
				cut2=cut1+2
				for x in range(e,cut1): arr.append([x+e*bsz])
				for x in range(cut2,bsz): arr.append([x+e*bsz])
				arr.append([x+e*bsz for x in range(cut1,cut2)])
				for x in range(e+1,cut1): arr.append([e+x*bsz])
				for x in range(cut2,bsz): arr.append([e+x*bsz])
				arr.append([e+x*bsz for x in range(cut1,cut2)])
	for R in range(rsz):
		banner="round "+str(R)+" b "+str(bi)+" / "+str(len(bv))
		print(banner)
		bi%=len(bv)
		tmpb=bv[bi].copy()
		bi+=1
		if useAll=='test': tmpb.print()
		p.score(tmpb,ans,esz)
		p.next()
		# nn
		'''
		'''
		best=p.bestA()
		print(best)
		tmpb.print('\n')
		moves=p.av[0][1].findsol(tmpb,ans)[1]
		print(moves)
		tmpb.moveSeq(moves,verbose=False)
		tmpb.print('\n')
		#if best[0][0]==0: bi+=1
		#if bi>=(len(bv)<<2): break
	exit()

if __name__=='__main__':
	main(sys.argv)

