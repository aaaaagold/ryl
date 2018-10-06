#!/bin/python3
import copy
import sys
import time
import random

from shorthand import *

class ttt:
	'''
		tik-tac-toe
	'''
	emptyNum=0
	def __init__(self):
		self.__board=[self.__class__.emptyNum for _ in range(9)]
		self.__turn=-1
		pass
	def copy(self):
		rtv=ttt()
		rtv.__board = copy.copy(self.__board)
		rtv.__turn=self.turn()
		return rtv
	def rawBoard(self):
		return self.__board
	def turn(self):
		return copy.copy(self.turn)
	def put(self,place,player=None):
		# return True on error
		if self.__board[place]!=0: return True
		if isNone(player):
			player=self.turn()
			self.__turn=-self.__turn
		self.__board[place]=player
		return False
	def _bfs(self,step,turn,stateLimit):
		rtv=[]
		if step<0: return rtv
		arr=self.__board
		for i in range(len(arr)):
			if arr[i]==self.__class__.emptyNum: continue
			pass
		pass
	def near1puts(self):
		return [ i for i in range(len(arr)) if self.__board[i]==0 ]
	def near1(self):
		puts=self.near1puts()
		rtv=[] # [ (putAt,stateAfterPut) ]
		for i in puts:
			tmp=self.copy()
			tmp.put(i)
			rtv.append((i,tmp))
		return rtv
	def hash(self):
		rtv=0
		for i in range(len(self.__board)):
			x=self.__board[i]
			rtv*=3
			rtv+=x+1
		return rtv
	def bfs(self,step=8,turn=0,stateLimit=4095):
		# TODO
		rtv={}
		t=(self.copy(),0,(-1,-1)) # ( ; , total_puts , (last_put , hash) )
		q=queue()
		q.push(t)
		del t
		while q.size()!=0:
			t=q.pop()
			pass
		pass

