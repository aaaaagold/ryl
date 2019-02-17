#!/bin/python3
import copy
import sys
import time
import random

from shorthand import *
from amyhead import *
#from ah import *
import ab

class board(ab.board):
	outputOrder=[
		15,
		14,11,10,
		13,9,7,6,5,
		12,8,4,3,2,1,0
	]
	'''
		pieceNum.. -> outputOrder[pieceNum]..
		00 01 02 03
		04 05 06 07
		08 09 10 11
		12 13 14 15
		->
		15 14 13 12
		11 08 07 06
		10 05 03 02
		09 04 01 00
	'''
	def __init__(self,wh):
		super(self.__class__,self).__init__(wh)
	def _output(self,argv=()):
		t=()
		tmp=[ t for _ in range(len(self.__board)) ]
		for loc in range(len(self.__board)):
			transedOrd=self.__class__.outputOrder[self.__board[loc]] # change order
			tmp[transedOrd]=(int(loc%self.__wh[0]),int(loc//self.__wh[0]))
			#tmp[ self.__board[loc] ] = (loc,)
			#tmp[ self.__board[loc] ] = (int(loc//self.__wh[0]),int(loc%self.__wh[0]))
		rtv=[ x for v in tmp for x in v ]
		#tmp=[] # debug
		#tmp+=rtv # debug
		#tmp+=rtv # debug
		#print(len(tmp)) # debug
		return rtv
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

