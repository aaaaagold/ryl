#!/bin/python3
import copy
import sys
import time
import random
import math

from shorthand import *
from amyhead import *

class mb:
	def __init__(self):
		self.xy=[0,0]
		self.d=90 # F
	def copy(self):
		rtv=self.__class__()
		rtv.xy=self.xy
		rtt.d=self.d
		return rtv
	def ouyputs(self):
		pass
	def setStat(self,xy=None,d=None):
		if not isNone(xy): self.xy=xy
		if not isNone(d):  self.d=d
		return self
	def print(self):
		print("xy",self.xy)
		print("dir",self.d)
	def _rot(self,xy,rad):
		c,s=math.cos(rad),math.sin(rad)
		return [xy[0]*c-xy[1]*s,xy[0]*s+xy[1]*c]
	def _rot90(self,xy):
		return [-xy[1],xy[0]]
	def _move(self,m1m2):
		# L,R
		m1,m2=m1m2
		mscale=1
		D=1 # distance of 2 wheels
		# common used
		pi_180=math.pi/180
		#c,s=math.cos(self.d*math.pi*2/360),math.sin(self.d*math.pi*2/360) # F
		c,s=math.cos(self.d*pi_180),math.sin(self.d*pi_180) # F
		rc,rs=self._rot90([c,s]) # L
		d=D/2.0
		dxy=[rc*d,rs*d]
		if m1*m2==0:
			rad=0
			if m1!=0:
				rad+=-m1*mscale/D
				cxy=[self.xy[i]-dxy[i] for i in range(2)]
				dxy=self._rot(dxy,rad)
				self.xy=[cxy[i]+dxy[i] for i in range(2)]
			elif m2!=0:
				rad+=m2*mscale/D
				cxy=[self.xy[i]+dxy[i] for i in range(2)]
				dxy=self._rot(dxy,rad)
				self.xy=[cxy[i]-dxy[i] for i in range(2)]
			else: return
			#self.d+=rad/(math.pi*2)*360
			self.d+=rad/pi_180
			self.d%=360
		elif m1==m2:
			scale=m1*mscale
			self.xy[0]+=c*scale
			self.xy[1]+=s*scale
		else:
			n=(m1-m2)*1.0
			m1/=n
			m2/=n
			cxy=[ -m2*(self.xy[i]+dxy[i])+m1*(self.xy[i]-dxy[i]) for i in range(2) ]
			dxy=[ self.xy[i]-cxy[i] for i in range(2) ]
			rad=0
			if m1==-m2: rad+=m2*n*mscale/d
			else:
				rad+=(m1+m2)*n/2*mscale/sum([i**2 for i in dxy])**0.5
				dxy=self._rot(dxy,rad)
				self.xy=[ cxy[i]+dxy[i] for i in range(2) ]
			self.d+=rad/(math.pi*2)*360
			self.d%=360
		return self
	def moves(self,info={}):
		# return available (move steps)s
		# (+- 0%,20%,40%,60%,80%,100%, ... )
		pass
	def moveSeq(self,msgv,verbose=True):
		# move several move steps
		pass
	def move1(self,m,fixedBlockIts=[]):
		# move 1 step
		pass
	def move(self,move_seq,fixedBlockIts=[]):
		# 1 move steps
		pass
	def near1(self,info={}):
		# return near states: (turn,moveSeqFrom_moves,internalState)
		pass


if __name__=='__main__':
	bbb=mb()
	for _ in range(8):
		bbb.print()
		bbb._move([math.pi*3.5,math.pi*4])
	bbb.print()
	print()
	for _ in range(4):
		bbb.print()
		bbb._move([math.pi*-0.5,math.pi*0.5])
	bbb.print()
	print()
	for _ in range(2):
		bbb.print()
		bbb._move([1,1])
		bbb.print()
		bbb._move([math.pi*1.5,math.pi*2])
	bbb.print()
