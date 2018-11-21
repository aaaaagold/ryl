#!/bin/python3
import copy
import sys
import time
import random
import re

from shorthand import *
from amyhead import *


class maze:
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
		rtv._size=self._size
		rtv._adj=self._adj
		rtv.pos=copy.deepcopy(self.pos)
		return rtv
	def rawBoard(self):
		return self.pos
	def random(self):
		self.pos=(random.randint(0,self._size[0]-1),random.randint(0,self._size[1]-1))
		return self
	def moves(self):
		return [ i for i in range(4) ]
	def moveSeq(self,mv,verbose=True):
		for msg in mv:
			t,m,s=msg
			self.move(m)
			if verbose:
				print(m)
				self.print('\n')
	def move(self,m):
		rtv=False
		newPos=[ x for x in self.pos ]
		
		# 0z:R+L- 1z:D+U-
		idx=(m&2)==0
		if (m&1)==0: newPos[idx]+=1
		else: newPos[idx]-=1
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
	def near1(self):
		rtv=[]
		for m in self.moves():
			if self.move(m): continue
			rtv.append((0,m,self.copy()))
			self.move(m^1)
		return rtv
	def hash(self):
		return self._toAdjIdx(self.pos)
	def print(self):
		print("maze",self._fileName)
		print("size",self._size)
		print("pos",self.pos)


if __name__=='__main__':
	pass
