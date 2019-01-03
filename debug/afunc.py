#!/bin/python3
import copy
import sys
import time
import random
import re

from shorthand import *
from amyhead import *


class func_tx:
	# y = f(t,x)
	# given range of y, find x so that f(t,x) in that range
	# t is given and may be edited, so there's chances to re-find x.
	####  form of f:  ####
	# THIS class is suppose to be: p1(t) crossproduct p2(x), where p1 and p2 are polynomial
	def __init__(self,coef_X=[],coef_T=[],copyArg=True):
		# exponent starts from 0
		if copyArg:
			self.coefs={"x":copy.deepcopy(coef_X),"t":copy.deepcopy(coef_T)}
		else:
			self.coefs={"x":coef_X,"t":coef_T}
	def copy(self):
		rtv=self.__class__(self.coefs["x"],self.coefs["t"])
		return rtv
	def cal(self,T,X):
		rtv=0
		expX=1
		for x in self.coefs["x"]:
			expT=1
			expXx=expX*x
			for t in self.coefs["t"]:
				rtv+=expXx*expT*t
				expT*=T
			expX*=X
		return rtv

class func:
	# class issue
	def __init__(self,x_init=[0],coef_X=[],coef_T=[],copyArg=True):
		self._core=func_tx(coef_X,coef_T,copyArg=copyArg)
		self.x = copy.deepcopy(x_init) if copyArg else x_init
		self.t=0
	def copy(self):
		rtv=self.__class__()
		rtv._core=self._core
		rtv.x = copy.deepcopy(self.x)
		rtv.t=self.t
		return rtv
	# state / output
	def rawBoard(self):
		return self.x
	def output(self):
		return [ self._core.cal(self.t,x) for x in self.x ]
	def outputs(self):
		rtv=[]
		rtv+=self.output()
		rtv+=self.rawBoard()
		return rtv
	def random(self,info=None):
		scale = info["scale"] if type(info)==dict and "scale" in info else 1024
		self.x = [ x+(random.random()*2-1)*scale for x in self.x ]
	def print(self,end=''):
		print("x:",self.x,"t:",self.t,end=end)
	# ext-force
	def _inc_t(self):
		self.t+=1
	def nextStage(self):
		self._inc_t()
	# expand
	def _moves_exp(self,deltaV,_midx,_xIt=0,_deltaVchV=[],_rtv=[]):
		func_exp1=self._moves_exp
		if _xIt==len(_midx):
			_rtv.append([[ _midx[i]+_deltaVchV[i]-self.x[i] for i in range(_xIt) ],])
			return
		if _xIt==0:
			_deltaVchV=[]
			_rtv=[]
		for d in deltaV:
			_deltaVchV.append(d)
			func_exp1(deltaV,_midx=_midx,_xIt=_xIt+1,_deltaVchV=_deltaVchV,_rtv=_rtv)
			_deltaVchV.pop()
		return _rtv
	def moves(self,info=None):
		# return move sequences
		width=info["width"] if type(info)==dict and "width" in info else 11
		precision=info["precision"] if type(info)==dict and "precision" in info else 0.1
		#
		if width<=0 or precision<=0: return []
		midx=self.x if (width&1)!=0 else [ x-precision/2.0 for x in self.x ]
		strt=((-width)>>1)+1
		ende=(width>>1)+1
		return self._moves_exp(deltaV=[ precision*i for i in range(strt,ende) ],_midx=midx)
	def moveSeq(self,msgv,verbose=True):
		# move according to sequences
		for msg in msgv:
			t,mSeq,s=msg
			self.move(mSeq)
			if verbose:
				print(mSeq)
				self.print('\n')
	def move1(self,m,info=None):
		# 1-step basic move
		rtv=False
		self.x = [ self.x[i]+m[i] for i in range(len(m)) ]
		return rtv
	def move(self,move_seq,info=None):
		# move according to 1 sequence
		if (len(move_seq)<<1)<len(self.rawBoard()):
			for i in range(len(move_seq)):
				m=move_seq[i]
				if self.move1(m):
					self.moveR(move_seq[:i])
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
		moveSeqR=[ [ -m for m in move_seq[i] ] for i in range(len(move_seq)-1,-1,-1) ]
		return self.move(moveSeqR)
	def near1(self,info={"width":11,"precision":0.1}):
		rtv=[]
		for mSeq in self.moves(info=info):
			if self.move(mSeq): continue
			rtv.append((0,mSeq,self.copy()))
			self.moveR(mSeq)
		return rtv
	def hash(self):
		return tuple(self.x+[self.t])
		pass

