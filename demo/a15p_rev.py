#!/bin/python3
import copy
import sys
import time
import random

from shorthand import *
from amyhead import *
#from ah import *
import a15p_base

class board(a15p_base.board):
	def __init__(self,wh):
		super(self.__class__,self).__init__(wh)
	def _output(self,argv=()):
		t=()
		tmp=[ t for _ in range(len(self.__board)) ]
		for i in range(len(self.__board)):
			tmp[ self.__board[i] ] = (i,)
			#tmp[ self.__board[i] ] = (int(i//self.__wh[0]),int(i%self.__wh[0]))
		return [ x for v in tmp for x in v ]
	def copy(self):
		rtv=self.__class__(self.__wh)
		rtv.__board=self.copyBoard()
		rtv.__emptyNum=copy.deepcopy(self.__emptyNum)
		rtv.__emptyAt=copy.deepcopy(self.__emptyAt)
		return rtv
	def output(self,argv=()):
		rtv=[]
		rtv+=self._output(argv)
		return rtv
	def outputs(self,argv=()):
		rtv=[]
		rtv+=self._output(argv)
		rtv+=self.rawBoard()
		return rtv

def p9(goal,strt):
	self=p9
	ab.p9(goal,strt)

