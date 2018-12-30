#!/bin/python3
import copy
import sys
import time
import random
import re

from shorthand import *
from amyhead import *


class maze:
	# a "question" like a 2-d Cartesian maze
	# need a maze adjacency list with first line is two numbers: "width height"
	parser=re.compile("([0-9]+)[ \t]+([0-9]+)")
	def __init__(self):
		# const
		self._fileName=""
		self._size=(0,0) # (x,y)
		self._adj=[] # [ set() , ... ]
		# changable
		self.pos=(0,0)
	def _toAdjIdx(self,pos):
		return pos[1]*self._size[0]+pos[0]
	def fromFile(self,fileName,strtPos=(0,0)):
		self._fileName=fileName
		self.pos=copy.deepcopy(strtPos)
		txt=""
		with open(fileName,"r") as f:
			txt+=f.read()
		lines=txt.replace("\r","").split("\n")
		parser=self.__class__.parser
		self._size=tuple([ int(x) for x in parser.match(lines[0]).groups() ])
		self._adj=[ set() for _ in range(self._size[0]*self._size[1]) ]
		for i in range(1,len(lines)):
			m=parser.match(lines[i])
			if isNone(m): continue
			pts=[int(x) for x in m.groups()]
			self._adj[pts[0]].add(pts[1])
			self._adj[pts[1]].add(pts[0])
		return self
	def copy(self):
		rtv=maze()
		rtv._fileName=self._fileName
		rtv._size=self._size
		rtv._adj=self._adj
		rtv.pos=copy.deepcopy(self.pos)
		return rtv
	def setAs(self,rhs,noCopy=False):
		tmp=rhs.copy() if noCopy==False else rhs
		self._fileName=tmp._fileName
		self._size=tmp._size
		self._adj=tmp._adj
		self.pos=tmp.pos
		return self
	def setBoard(self,bd):
		# sets something that can be changed in this "question"
		self.pos=copy.deepcopy(bd)
	def rawBoard(self):
		# returns something that can be changed in this "question"
		return self.pos
	def output(self,argv=()):
		return ()
	def outputs(self,argv=()):
		rtv=[]
		rtv+=self.output(argv)
		rtv+=self.rawBoard()
		return rtv
	def random(self):
		self.pos=(random.randint(0,self._size[0]-1),random.randint(0,self._size[1]-1))
		return self
	def moves(self,info=None):
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
	def move1(self,m):
		rtv=False
		newPos=[ x for x in self.pos ]
		
		# 0z:R+L- 1z:D+U-
		idx=(m&2)==0
		newPos[idx]+=((0==(m&1))<<1)-1
		rtv=(newPos[idx]<0)|(newPos[idx]>=self._size[idx]) # err
		#print(self.pos)
		if rtv==False and self._toAdjIdx(newPos) in self._adj[self._toAdjIdx(self.pos)]:
			# no err, move
			self.pos=tuple(newPos)
			return False
		else: return True
		
		# alternative_code:
		# 0z:RL 1z:DU
		if (m&2)==0:
			# 0:R+ 1:L-
			if (m&1)==0: newPos[0]+=1
			else: newPos[0]-=1
			rtv=(newPos[0]<0)|(newPos[0]>=self._size[0]) # err
		else:
			# 0:D+ 1:U-
			if (m&1)==0: newPos[1]+=1
			else: newPos[1]-=1
			rtv=(newPos[1]<0)|(newPos[1]>=self._size[1]) # err
		if rtv==False and self._toAdjIdx(newPos) in self._adj[self._toAdjIdx(self.pos)]:
			# no err, move
			self.pos=tuple(newPos)
			return False
		else: return True
	def move(self,move_seq):
		if (len(move_seq)<<1)<len(self.rawBoard()):
			for i in range(len(move_seq)):
				m=move_seq[i]
				if self.move1(m):
					for j in range(i-1,-1,-1):
						self.move1(move_seq[j]^1)
					return True
			return False
		oriStat=self.copy()
		for m in move_seq:
			if self.move1(m):
				# invalid move, recover
				self.setAs(oriStat,noCopy=True)
				return True
		# all moves are valid
		return False
	def moveR(self,move_seq):
		# reversed move of the move sequence
		moveSeqR=[ move_seq[i]^1 for i in range(-len(move_seq),0) ]
		return self.move(moveSeqR)
	def near1(self,info=None):
		rtv=[]
		for mSeq in self.moves(info=info):
			if self.move(mSeq): continue
			rtv.append((0,mSeq,self.copy()))
			self.moveR(mSeq)
		return rtv
	def hash(self):
		return self._toAdjIdx(self.pos)
	def print(self):
		print("maze",self._fileName)
		print("size",self._size)
		print("pos",self.pos)


if __name__=='__main__':
	pass
