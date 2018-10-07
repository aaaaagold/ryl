#!/bin/python3
import copy
import sys
import time
import random


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

