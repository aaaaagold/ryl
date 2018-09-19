#!/bin/python3
import re
from shorthand import *

parser=re.compile('[ \t]*([0-9]+)[ \t](.+)')

class goal:
	# chain-like structure
	def __init__(self):
		self.constraints=[]
		self.arrangeNeeded=False
	def arrange(self):
		if self.arrangeNeeded!=False:
			self.arrangeNeeded=False
			self.constraints.sort()
	def add(self,item,label=0,arrangeLater=False):
		# label must be an integer
		self.constraints.append((label,item))
		if arrangeLater==False: self.arrange()
		else: arrangeNeeded=arrangeLater
	def __eq__(self,rhs):
		self.arrange()
		if isinstance(rhs,self.__class__):
			return self.constraints==rhs.constraints
		else:
			raise TypeError("unsupport: %s == %s"%(self.__class__,type(rhs)))
	def fromTxt(self,filename):
		# TODO
		'''
			will NOT do the arrangement
			make sure the lines of constraints:
				labels are in increasing order
				items of the same label are in lexicographical order
		'''
		with open(filename,'rb') as f:
			#print("".join(map(chr,f.read())))
			'''
				format:
				each line: label item
				[ \t]*([0-9]+)[ \t](.+)
				lines not match will be omitted
			'''
			lines="".join(map(chr,f.read())).split("\n")
			for line in lines:
				m=parser.match(line)
				if isNone(m): continue
				res=m.group(1,2)
				self.add(res[1],int(res[0]),arrangeLater=True)
			self.arrange()
		return self

