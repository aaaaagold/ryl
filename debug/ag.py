#!/bin/python3
import re
import sys
from shorthand import *
from pprint import pprint

#parser_goal=re.compile('[ \t]*([0-9]+)[ \t](.+)')
token_item='[ \t]*([0-9]+)[ \t]([^\n]+)'
token_goalset='[\n]*([A-Za-z0-9_$]+)[ \t]([A-Za-z0-9_$]+|-)(([\n][\n]?[^\n]+)*)([\n][\n][\n]|[\n]?[\n]?$)'
token_goaltree='(('+token_goalset+')*)'
#token_goaltree='[\n]*([A-Za-z0-9_$]+[ \t]([A-Za-z0-9_$]+|-)([\n][^\n])*)($|[\n][\n]+)'
parser_goaltree=re.compile(token_goaltree)

class goal:
	parser_item=re.compile(token_item)
	# node
	def __init__(self):
		self.constraints=[]
		self.maxLabel=-1
		self.arrangeNeeded=False
	def __eq__(self,rhs):
		self.arrange()
		if isinstance(rhs,self.__class__):
			return self.constraints==rhs.constraints
		else:
			raise TypeError("unsupport: %s == %s"%(self.__class__,type(rhs)))
	def __repr__(self):
		return "[goal:"+str(self.constraints)+"]"
	def arrange(self):
		if self.arrangeNeeded!=False:
			self.arrangeNeeded=False
			self.constraints.sort()
	def add(self,item,label=0,arrangeLater=False):
		# label must be an integer
		self.constraints.append((label,item))
		if self.maxLabel<label: self.maxLabel=label
		if arrangeLater==False: self.arrange()
		else: arrangeNeeded=arrangeLater
	def fromStr(self,s):
		'''
			character:'\r' is ommited
			this function will NOT do the arrangement
			make sure the lines of constraints:
				labels are in increasing order
				items of the same label are in lexicographical order
			
			format:
			each line: label item
			[ \t]*([0-9]+)[ \t]([^\n]+)
			lines not match will be omitted
		'''
		self.maxLabel=-1
		lines=s.split('\n')
		for line in lines:
			m=self.__class__.parser_item.match(line)
			if isNone(m): continue
			res=m.group(1,2)
			self.add(res[1],int(res[0]),arrangeLater=True)
		return self
	def toStr(self):
		length=len(str(self.maxLabel))
		rtv=""
		tmpv=[]
		for c in self.constraints:
			tmpv.append("%*d\t%s"%(length,c[0],c[1]))
		rtv+='\n'.join(tmpv)
		return rtv
	def fromTxt(self,filename):
		with open(filename,'rb') as f:
			self.fromStr("".join(map(chr,f.read())))
		return self

class goaltree:
	'''
		definitions:
			successor:
				the next goal to match after matching a goal
	'''
	parser_set=re.compile(token_goalset)
	parser_tree=re.compile(token_goaltree)
	def __init__(self):
		self.sets={}
		pass
	def __repr__(self):
		rtv='{goaltree:\n'
		tmp=[ (k,v) for k,v in self.sets.items() ]
		tmp.sort()
		for x in tmp:
			rtv+="\t"+x[0]+":"+str(x[1])+",\n"
		rtv+='\t-:0\n}'
		return rtv
	def __getitem__(self,k):
		return self.sets[k] if k in self.sets else None
	def addgoal(self,goal,name,successorName):
		# TODO
		pass
	def keys(self):
		rtv=[k for k in self.sets]
		rtv.sort()
		return rtv
	def getGoals(self,k):
		return self.sets[k][0] if k in self.sets else None
	def getSucc(self,k):
		return self.sets[k][1]
	def getFinals(self):
		return [ k for k in self.sets if self.getSucc(k)=='-' ]
	def fromStr(self,s):
		'''
			character:'\r' is ommited
			format: see self.fromTxt
		'''
		s=s.replace('\r','')
		#print(bytes(token_goaltree,"UTF-8")) # debug
		m=self.__class__.parser_tree.match(s)
		if isNone(m): return
		#print('*',m.groups()) # debug
		data=[]
		defined=set()
		blocks=re.sub("[ \t]+[\n]","\n",m.group(1)).split("\n\n\n")
		#pprint(blocks) # debug
		for block in blocks:
			#print('**',block) # debug
			m=self.__class__.parser_set.match(block)
			if isNone(m): continue
			#print('***',m.groups()) # debug
			curr=m.group(1)
			succ=m.group(2)
			if curr in defined:
				raise TypeError("Error: '"+curr+"' is defined twice")
			defined.add(curr)
			#print("add",curr) # debug
			gsv=m.group(3).split("\n\n")
			data.append((curr,([ goal().fromStr(gs) for gs in gsv ],succ)))
			#data.sort()
		#pprint(data) # debug
		self.sets=dict(data)
		return self
	def toStr(self):
		kv=self.keys()
		rtv=""
		tmpv=[]
		for k in kv:
			tmps=""
			tmps+=k
			tmps+='\t'
			tmps+=self.getSucc(k)
			tmpgsv=[ g.toStr() for g in self.getGoals(k) ]
			tmpv.append('\n'.join([tmps,"\n\n".join(tmpgsv)]))
		rtv+="\n\n\n".join(tmpv)
		return rtv
	def fromTxt(self,filename):
		'''
			concept:
			a block with a name is a set of goal. that means reach one of them is a 'match', and can to further more (try the successor)
			
			format prototype:

			( none or more empty lines )
			...
			( none or more empty lines )
			name successorName(if None, use '-')
			# lines which cannot be parsed as <class: goal>
			label item
			# lines which cannot be parsed as <class: goal>
			label item
			...
			label item
			label item
			( an empty line )
			label item
			label item
			...
			label item
			label item
			( two or more empty lines )
			...
			( two or more empty lines )
			name successorName(if None, use '-')
			label item
			...

			in regex:
			
		'''
		with open(filename,'rb') as f:
			self.fromStr("".join(map(chr,f.read())))
		return self

