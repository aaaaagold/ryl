#!/bin/python3

class goal:
	# chain-like sturcture
	def __init__(self):
		self.constraints=[]
		self.arrangeNeeded=False
	def arrange(self):
		if self.arrangeNeeded!=False:
			self.arrangeNeeded=False
			self.constraints.sort()
	def add(self,ele,label=0,arrangeLater=False):
		self.constraints.append((label,ele))
		if arrangeLater==False: self.arrange()
		else: arrangeNeeded=arrangeLater
	def __eq__(self,rhs):
		self.arrange()
		if isinstance(rhs,self.__class__):
			return self.constraints==rhs.constraints
		else:
			raise TypeError("unsupport: %s == %s"%(self.__class__,type(rhs)))

