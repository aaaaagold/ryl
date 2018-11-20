#!/bin/python3
import copy
import sys
import time
import random

from shorthand import *
from amyhead import *


class maze:
	def __init__(self):
		# const
		self._size=(0,0) # (x,y)
		self._adj=[] # 2-dim
		# changable
		self.pos=(0,0)
	def fromFile(self,fileName,strtPos=(0,0)):
		self.pos=copy.deepcopy(strtPos)
		txt=""
		with open(fileName,"r"):
			txt+=f.read()
		lines=txt.replace("\r","").split("\n")
		pass
	def copy(self):
		rtv=maze()
		rtv._size=self._size
		rtv._adj=self._adj
		rtv.pos=copy.deepcopy(self.pos)
		return rtv
	def rawBoard(self):
		return self.pos
	def random(self):
		self.pos=(random.randint(self.size[0]),random.randint(self.size[1]))
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
		if rtv==False:
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
		if rtv==False:
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
		return self.pos[1]*self._size[0]+self.pos[0]


if __name__=='__main__':
	pass
