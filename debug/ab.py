#!/bin/python3
import copy
import sys
import time
import random

from shorthand import *
from amyhead import *
#from ah import *
'''
import resource
rsrc=resource.RLIMIT_DATA
soft,hard=resource.getrlimit(rsrc)
print("mem limit soft,hard",soft,hard)
resource.setrlimit(rsrc,(2**11,2**12))
soft,hard=resource.getrlimit(rsrc)
print("mem limit soft,hard",soft,hard)
del soft,hard
'''
'''
class queue:
	def __init__(self):
		self.__contI=[]
		self.__contO=[]
	def __dump(self):
		while len(self.__contI)!=0:
			self.__contO.append(self.__contI.pop())
	def front(self):
		return self.__contI[0] if len(self.__contO)==0 else self.__contO[-1]
	def back(self):
		return self.__contO[0] if len(self.__contI)==0 else self.__contI[-1]
	def push(self,obj):
		self.__contI.append(obj)
	def pop(self):
		if len(self.__contO)==0: self.__dump()
		return self.__contO.pop()
	def size(self):
		return len(self.__contI)+len(self.__contO)
	def toArr(self):
		return self.__contO+self.__contI
'''

class hfunc:
	def __init__(self,coefCnt):
		self.coefs=[ 0 for i in range(coefCnt) ]

class board:
	# a "question" like a 15-puzzle
	def size(self):
		return self.__wh[0]*self.__wh[1]
	def wh(self):
		return (self.__wh[0],self.__wh[1])
	def emptyNum(self):
		return self.__emptyNum
	def emptyAt(self):
		return self.__emptyAt
	def dontcareNum(self):
		return -1
	def setDontcare(self,atHere=[],excludeEmpty=False):
		'''
			if excludeEmpty!=False , then the empty is NOT set to dontcare
			/* or in other ways to say */
			if excludeEmpty==False , then the empty is included to set to dontcare
		'''
		sz=self.size()
		for i in atHere:
			if excludeEmpty!=False and i==self.emptyAt(): continue
			self.__board[i]=self.dontcareNum()
	def swap(self,ij):
		(i,j)=ij
		(self.__board[i],self.__board[j])=(self.__board[j],self.__board[i])
		if self.emptyAt() in ij: self.__emptyAt=i+j-self.__emptyAt
	def setNums(self,nums,emptyAt):
		if len(nums)!=self.size(): return False
		self.swap((self.emptyAt(),emptyAt))
		self.__board=copy.deepcopy(nums)
		self.__emptyNum=nums[emptyAt]
	def random(self,it=-1,solvable=True):
		sz=self.size()
		if it<0: it=sz*sz
		for _ in range(it):
			ch1=int(random.random()*sz)
			ch2=int(random.random()*sz)
			self.swap((ch1,ch2))
		if solvable and self.solvable()==False:
			ch=int(random.random()*(sz-2))
			if ch>=self.emptyAt(): ch+=1
			succ=1+(ch+1==self.emptyAt())
			self.swap((ch,ch+succ))
		return self
	def copyBoard(self):
		return copy.deepcopy(self.__board)
	def rawBoard(self):
		return self.__board
	def output(self,argv=()):
		return ()
	def outputs(self,argv=()):
		rtv=[]
		rtv+=self.output(argv)
		rtv+=self.rawBoard()
		return rtv
	def copy(self):
		rtv=board(self.__wh)
		rtv.__board=self.copyBoard()
		rtv.__emptyNum=copy.deepcopy(self.__emptyNum)
		rtv.__emptyAt=copy.deepcopy(self.__emptyAt)
		return rtv
	def setAs(self,rhs,noCopy=False):
		tmp=rhs.copy() if noCopy==False else rhs
		self.__board=tmp.__board
		self.__emptyNum=tmp.__emptyNum
		self.__emptyAt=tmp.__emptyAt
		return self
	def __init__(self,wh):
		self.__wh=(wh[0],wh[1])
		sz=self.size()
		self.__board=[ i for i in range(sz) ]
		self.__emptyNum=self.__board[-1]
		self.__emptyAt=sz-1
	def moves(self,info={}):
		'''
			return moves including invalid moves
		'''
		# return several move sequences
		# for example, 1 step forms a sequence
		# can be customized, or like a hypothesis, just return possible move sequences
		return [ [i] for i in range(4) ]
	def moveSeq(self,msgv,verbose=True):
		for msg in msgv:
			t,mSeq,s=msg
			self.move(mSeq)
			if verbose:
				print(mSeq)
				self.print('\n')
	def move1(self,m,fixedBlockIts=[]):
		'''
			m = an int means what kind of moves to take
			return True if ERROR else False
		'''
		rtv=False
		near=0
		wh=self.__wh
		# 0z:RL 1z:DU
		if (m&2)==0:
			# 0:R 1:L
			# R: wh[0]+1 # x+1
			if (m&1)==0:
				near+=self.__emptyAt+1
				rtv=near%wh[0]==0 # err
			else:
				near+=self.__emptyAt-1
				rtv=(self.__emptyAt)%wh[0]==0 # err
		else:
			# 0:D 1:U
			# D: wh[1]+1 # y+1
			if (m&1)==0:
				near+=self.__emptyAt+wh[0]
				rtv=near>=self.size() # err
			else:
				near+=self.__emptyAt-wh[0]
				rtv=near<0 # err
		if rtv==False and (not near in fixedBlockIts):
			# no err, swap
			self.swap((near,self.__emptyAt))
			self.__emptyAt=near
			return False
		else: return True
	def move(self,move_seq,fixedBlockIts=[]):
		if (len(move_seq)<<1)<len(self.rawBoard()):
			for i in range(len(move_seq)):
				m=move_seq[i]
				if self.move1(m,fixedBlockIts=fixedBlockIts):
					self.moveR(move_seq[:i])
					return True
			return False
		oriStat=self.copy()
		for m in move_seq:
			if self.move1(m,fixedBlockIts=fixedBlockIts):
				# invalid move, recover
				self.setAs(oriStat,noCopy=True)
				return True
		# all moves are valid
		return False
	def moveR(self,move_seq):
		# reversed move of the move sequence
		moveSeqR=[ move_seq[i]^1 for i in range(len(move_seq)-1,-1,-1) ]
		return self.move(moveSeqR)
	def near1(self,info={}):
		rtv=[]
		for mSeq in self.moves(info=info):
			if self.move(mSeq): continue
			rtv.append((0,mSeq,self.copy()))
			self.moveR(mSeq)
		return rtv
	def __fac(self):
		sz=self.size()
		fac=[1]
		for i in range(1,sz+1):
			tmp=fac[-1]*len(fac)
			fac.append(tmp)
			del tmp
		return fac
	def hash(self):
		rtv=0
		sz=self.size()
		fac=self.__fac()
		tmp=[ x for x in self.__board ]
		for i in range(sz-1,-1,-1):
			tmp.sort()
			order=tmp.index(self.__board[i])
			rtv+=order*fac[i]
			tmp[order]=tmp[-1]
			tmp.pop()
			del order
		del sz,fac,tmp
		return rtv
	def hashMax(self):
		return self.__fac()[-1]-1
	def bfs(self,step=8,fixedBlockIts=[],stateLimit=4095,notViolate=[]):
		#print(stateLimit) # debug
		rtv={} if self.size()>=10 else [ None for _ in range(self.hashMax()+1) ]
		rtvIsList=type(rtv)==type([])
		stateCnt=0
		t=(self.copy(),0,(-1,-1))
		q=queue()
		q.push(t)
		del t
		while q.size()!=0:
			t=q.pop()
			currstat=t[0]
			currstep=t[1]
			currstatNum=currstat.hash()
			if rtvIsList:
				if type(rtv[currstatNum])!=type(None): continue
			elif currstatNum in rtv: continue
			rtv[currstatNum]=t
			del t
			stateCnt+=1
			if stateCnt>stateLimit: break
			moves=currstat.moves()
			for m in moves:
				if currstat.move(m,fixedBlockIts): continue
				else:
					tmpstat=currstat.copy()
					tmpstatNum=tmpstat.hash()
					if currstep<step:
						t=(tmpstat,currstep+1,(m,currstatNum)) ####
						q.push(t)
						del t
					del tmpstat,tmpstatNum
				currstat.move(m^1)
			del currstat,currstep,currstatNum,moves
		del q
		if rtvIsList:
			newrtv={}
			for i in range(len(rtv)):
				if type(rtv[i])!=type(None):
					newrtv[i]=rtv[i]
			del rtv
			rtv=newrtv
		return rtv # rtv[stateHash]=(state,step,(move,prevState))
	def sameCnt(self,rhs,onlyTheseIts=None):
		sz=self.size()
		if sz!=rhs.size(): return -1
		rtv=0
		arr=range(sz) if type(onlyTheseIts)!=type([]) else onlyTheseIts
		for i in arr:
			rtv+=(self.__board[i]==rhs.__board[i])+0
		return rtv
	def guide(self,hfunc,hint):
		'''
			return a move
			hfunc(hint)
		'''
		return 0
		pass
	def score(self,goalConstraint):
		'''
			goalConstraint:
				a list, length = board
				ele.: "board[i] have to be goalConstraint[i]"
		'''
		pass
	def toGoal(self,constraint=[]):
		# constraint[n]: board[n] should be constraint[n]
		# None for not limited
		pass
	def print(self,end=''):
		for y in range(self.__wh[1]):
			for x in range(self.__wh[0]):
				num=self.__board[y*self.__wh[0]+x]
				s=""
				if num==self.emptyNum(): s+="[]"
				elif num==self.dontcareNum(): s+="--"
				else: s+="%d"%(num)
				print("%3s"%(s),end='')
			print("")
		print(end,end='')
	def __soltype(self):
		cnt=0
		bd=self.__board
		e=self.emptyAt()
		for p in range(len(bd)):
			if p==e: continue
			for n in range(p+1,len(bd)):
				if n!=e and bd[p]>bd[n]:
					cnt^=1
		cnt^=1
		wh=self.__wh
		return cnt!=0 if (wh[0]&1)!=0 else cnt==(int(wh[1]-int(e//wh[0]))&1)
	def solvable(self,goal=None):
		if type(goal)!=type(self):
			goal=board(self.__wh)
		return self.__soltype()==goal.__soltype()
	
def p9(goal,strt):
	self=p9
	if strt.size()!=9 or goal.size()!=9 or strt.solvable(goal)==False: return None
	if not hasattr(self,"cache"): self.cache=[ [] for _ in range(9) ]
	if len(self.cache[goal.emptyAt()])==0:
		self.cache[goal.emptyAt()]=[ None for i in range(362880) ]
		p9g=board((3,3))
		for _ in range(9):
			if p9g.emptyAt()!=goal.emptyAt():
				p9g.swap((p9g.emptyAt(),p9g.emptyAt()-1))
				continue
			res=p9g.bfs(step=33,stateLimit=362880)
			for i in res: self.cache[goal.emptyAt()][i]=res[i]
			break
	if not hasattr(self,"mapping"):
		def mapping(main,others=[]):
			arr=[ x for x in main.rawBoard() if x!=main.emptyNum() ]
			mp={}
			for i in range(len(arr)): mp[arr[i]]=i
			for b in [main]+others:
				arr=b.rawBoard()
				for i in range(len(arr)):
					arr[i]=mp[arr[i]] if arr[i]!=b.emptyNum() else b.size()-1
		self.mapping=mapping
	self.mapping(goal,[strt])
	rtv=bfs2moveSeq(self.cache[goal.emptyAt()],strt.hash())
	rtv.reverse()
	for i in range(len(rtv)): rtv[i]^=1
	return rtv

'''
def bfs2moveSeq(bfs,goalHash):
	moves=[]
	if (type(bfs)==type({}) and (goalHash in bfs)) or (type(bfs)==type([]) and type(bfs[goalHash])!=type(None)):
		pre=bfs[goalHash][2]
		preStat=pre[1]
		while preStat>=0:
			moves.append(pre[0])
			pre=bfs[preStat][2]
			preStat=pre[1]
		moves.reverse()
	return moves
'''

def test():
	# test
	print("hash")
	b=board((4,4))
	print(b.hash())
	b.print()
	bb=b.copy()
	bb.rawBoard().reverse()
	print(bb.hash())
	bb.print()
	bb=b.copy()
	bb.setDontcare(range(15))
	print(bb.hash())
	bb.print()
	b.setDontcare(range(1,15))
	print(b.hash())
	b.print()
	print(b.emptyAt())
	res1=b.bfs(25)
	b.swap((0,15))
	b.print()
	print(b.emptyAt())
	print("bfs")
	res1=b.bfs(25)
	res2=b.bfs(26)
	if not 0==0:
		for i in res2:
			print(res2[i][1])
			res2[i][0].print()
	print(len([0 for i in res1]))
	print(len([0 for i in res2]))
	for i in res2:
		if not i in res1:
			print(res2[i][1],i)
			res2[i][0].print()
	print()
	del b,bb,res1,res2

	q=board((4,4))
	q.setDontcare([5,6,7]+[9,10,11]+[13,14])
	q2=q.copy()
	q.setDontcare([1,2,3])
	print("target")
	q.print()
	targetHash=q.hash()
	print("start from")
	q.swap((4,3))
	q.swap((8,11))
	q.print()
	lastLen=-1
	for i in range(26,111,1):
		res=q.bfs(i,[0,12])
		newLen=len([0 for i in res])
		print(i,newLen)
		if targetHash in res:
			res[targetHash][0].print()
		del res
		if newLen==lastLen: break
		else: lastLen=newLen
		del newLen
	print("q2 t")
	q2.print()
	targetHash=q2.hash()
	#q2.swap((1,11))
	q2.swap((2,14))
	q2.swap((3,5))
	print("q2 s")
	q2.print()
	lastLen=-1
	for i in range(16,111,1):
		res=q2.bfs(i,[0,1,4,8,12])
		newLen=len([0 for i in res])
		print(i,newLen)
		if targetHash in res:
			res[targetHash][0].print()
		del res
		if newLen==lastLen: break
		else: lastLen=newLen
		del newLen
	exit(0)

if __name__=='__main__':
	# test
	a=board((3,3))
	b=a.copy()
	b.swap((8,7))
	b.swap((6,7))
	b.swap((6,3))
	a.print()
	b.print()
	print(a.hash(),b.hash())
	print(p9(a,b))

