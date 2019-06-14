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
		self.d=90 # F
		self.xy=[0,0]
	def copy(self):
		rtv=self.__class__()
		rtv.d=self.d
		rtv.xy.clear()
		rtv.xy+=self.xy
		return rtv
	def outputs(self):
		return self.rawBoard()
	def rawBoard(self):
		rtv=[self.d]
		rtv+=self.xy
		return rtv
	def hash(self):
		arr=self.rawBoard()
		return tuple(self.rawBoard())
	def setStat(self,xy=None,d=None):
		if not isNone(xy): self.xy=xy
		if not isNone(d):  self.d=d
		return self
	def print(self,end=''):
		print("dir",self.d)
		print("xy",self.xy)
		print(end=end)
	def _rot(self,xy,rad):
		c,s=math.cos(rad),math.sin(rad)
		return [xy[0]*c-xy[1]*s,xy[0]*s+xy[1]*c]
	def _rot90(self,xy):
		return [-xy[1],xy[0]]
	def _move(self,m1m2):
		# TODO: suppose a timeslot = ?ms
		# L,R
		m1,m2=m1m2
		mscale=math.pi*0.25/700 # [-100,100] dt=0.125 * 7 ~ 90 deg # neg*1.125 # notice inertia
		D=1 # distance of 2 wheels
		# common used
		pi_180=math.pi/180
		#c,s=math.cos(self.d*math.pi*2/360),math.sin(self.d*math.pi*2/360) # F
		c,s=math.cos(self.d*pi_180),math.sin(self.d*pi_180) # F
		if c*c<1e-16: c*=0
		if s*s<1e-16: s*=0
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
		self.d=int(self.d*100)/100.0
		return self
	def moves(self,info={}):
		# return available (move steps)s
		# (0%,+-100%, ... )
		rtv=[] if not "moves" in info else [m for m in info["moves"]]
		# rtv+=[ [] , [] , ...  ]
		for j in range(3):
			for i in range(3):
				rtv.append([((i-1)*100,(j-1)*100)])
		return rtv
	def moveSeq(self,msgv,verbose=True):
		for msg in msgv:
			t,mSeq,s=msg
			self.move(mSeq)
			if verbose:
				print(mSeq)
				self.print('\n')
	def move1(self,m,fixedBlockIts=[]):
		# move 1 step
		return self._move(m)
	def move(self,move_seq,fixedBlockIts=[]):
		# 1 move steps
		for m in move_seq: self._move(m)
		return False
	def near1(self,info={}):
		# return near states: (turn,moveSeqFrom_moves,internalState)
		rtv=[]
		for mSeq in self.moves(info=info):
			n=self.copy()
			if n.move(mSeq): continue
			rtv.append((0,mSeq,n))
		return rtv


if __name__=='__main__':
	ms=[
			# deg90n
			[(100, -100), (100, -100), (100, -100), (100, -100), (100, -100), (100, -100), (100, -100)],
			# deg90p
			[(-100, 100), (-100, 100), (-100, 100), (-100, 100), (-100, 100), (-100, 100), (-100, 100)],
			# forward
			[(100, 100), (100, 100), (100, 100), (100, 100), (100, 100), (100, 100), (100, 100)],
			# backward
			#[(-100, -100), (-100, -100), (-100, -100), (-100, -100), (-100, -100), (-100, -100), (-100, -100)],
		]
	bbb=mb()
	bbb.print()
	bbb.move(ms[2])
	bbb.print()
	bbb.move(ms[2])
	bbb.print()
	bbb.move(ms[0])
	bbb.print()
	bbb.move(ms[2])
	bbb.print()
	bbb.move(ms[2])
	bbb.print()
	bbb.move(ms[0])
	bbb.print()
	bbb.move(ms[2])
	bbb.print()
	bbb.move(ms[2])
	bbb.print()
	exit()
	for _ in range(8):
		bbb.print()
		#bbb._move([math.pi*-0.25,math.pi*0.25])
		bbb._move([-100,100])
	bbb.print()
	exit()
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
	print()
