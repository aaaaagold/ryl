#!/bin/python3
import copy
import sys
import time
import random

from shorthand import *

class queue:
	def __init__(self):
		self.__contI=[]
		self.__contO=[]
	def __dump(self):
		while len(self.__contI)!=0:
			self.__contO.append(self.__contI.pop())
	def front(self):
		return self.__contI[0] if len(self.__contO)==0 else self.__contO[-1]
	def back(self):
		return self.__contO[0] if len(self.__contI)==0 else self.__contI[-1]
	def push(self,obj):
		self.__contI.append(obj)
	def pop(self):
		if len(self.__contO)==0: self.__dump()
		return self.__contO.pop()
	def size(self):
		return len(self.__contI)+len(self.__contO)
	def toArr(self):
		return self.__contO+self.__contI

def bs(aList,val,se=None):
	'''
		return value: index(i) that either
			aList[i]==val
			(i==0 or aList[i-1]<val) and val<aList[i]
	'''
	if isNone(se): se=(0,len(aList))
	if se[1]-se[0]<3:
		for i in range(se[0],se[1]):
			if aList[i]==val:
				return i
		for i in range(se[0],se[1]):
			if val<aList[i]:
				return i
		return se[1]
	m=int(sum(se))>>1
	return bs(aList,val,(se[0],m)) if val<aList[m] else bs(aList,val,(m,se[1]))
	

class avl:
	class node:
		def __init__(self,obj):
			self.obj=obj
			self.v=0
	def __init__(self):
		# TODO
		pass

