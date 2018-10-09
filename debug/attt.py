#!/bin/python3
import copy
import sys
import time
import random

from shorthand import *
from amyhead import *

class ttt:
	'''
		tik-tac-toe
	'''
	emptyNum=0
	def setNums(self,nums,turn):
		self.__board=copy.deepcopy(nums)
		self.__turn=copy.deepcopy(turn)
	def random(self):
		#turn=[-1,1][random.randint(0,1)]
		locs=[ i for i in range(9) ]
		for _ in locs:
			if random.randint(0,3)==0: break
			self.move((locs[random.randint(0,8)],self.turn()))
		return self
	def __init__(self):
		self.__board=[self.__class__.emptyNum for _ in range(9)]
		self.__turn=-1
		self.__wh=(3,3)
		pass
	def copy(self):
		rtv=ttt()
		rtv.__board = copy.deepcopy(self.__board)
		rtv.__turn=self.turn()
		rtv.__wh=self.__wh
		return rtv
	def rawBoard(self):
		return self.__board
	def turn(self):
		return copy.deepcopy(self.__turn)
	def put(self,place,player=None):
		# return True on error
		if self.__board[place]!=0: return True
		if isNone(player):
			player=self.turn()
			self.__turn=-self.__turn
		self.__board[place]=player
		return False
	def move(self,m,*argv):
		return self.put(m[1],m[0])
	def moveSeq(self,mv,verbose=False):
		for m in mv:
			self.move(m)
			if verbose:
				print(m)
				self.print('\n')
	def _bfs(self,step,turn,stateLimit):
		rtv=[]
		if step<0: return rtv
		arr=self.__board
		for i in range(len(arr)):
			if arr[i]==self.__class__.emptyNum: continue
			pass
		pass
	def near1puts(self):
		return [ i for i in range(len(self.__board)) if self.__board[i]==0 ]
	def moves(self):
		return [ (self.turn(),i) for i in self.near1puts() ]
	def near1(self):
		puts=self.near1puts()
		rtv=[] # [ (putAt,stateAfterPut) ]
		for i in puts:
			tmp=self.copy()
			turn=tmp.turn()
			if tmp.put(i): continue
			rtv.append((turn,i,tmp)) # 
		return rtv
	def hash(self):
		rtv=0
		for i in range(len(self.__board)):
			x=self.__board[i]
			rtv*=3
			rtv+=x+1
		return rtv
	def print(self):
		for y in range(self.__wh[1]):
			for x in range(self.__wh[0]):
				content=self.__board[y*self.__wh[0]+x]
				if content==-1: content='o'
				elif content==1: content='x'
				print(content,end=' ')
			print()
	def bfs(self,step=8,turn=0,stateLimit=4095):
		# TODO
		stateCnt=0
		rtv={}
		t=(self.copy(),0,(-1,-1)) # ( ; , total_puts , ((turn,last_put_loc) , lastStatHash) )
		q=queue()
		q.push(t)
		del t
		while q.size()!=0:
			t=q.pop()
			currstat=t[0]
			currstep=t[1]
			last_put=t[2][0]
			currstatNum=currstat.hash()
			if currstatNum in rtv: continue
			rtv[currstatNum]=t
			del t
			stateCnt+=1
			if stateCnt>stateLimit: break
			near1=currstat.near1()
			for near in near1:
				stat=near[2]
				actinfo=near[:2] # (who does, does what)
				if currstep<step:
					q.push((stat,currstep+1,(actinfo,currstatNum)))
		return rtv

