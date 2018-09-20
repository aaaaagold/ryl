#!/bin/python3
import re
import sys
from shorthand import *

#parser_goal=re.compile('[ \t]*([0-9]+)[ \t](.+)')
token_item='[ \t]*([0-9]+)[ \t]([^\n]+)'
token_goalset='([A-Za-z0-9_$]+)[ \t]([A-Za-z0-9_$]+|-)(([\n][\n]?[^\n]+)*)([\n][\n][\n]|[\n]?[\n]?$)'
token_goaltree='[\n]*(('+token_goalset+')*)'
#token_goaltree='[\n]*([A-Za-z0-9_$]+[ \t]([A-Za-z0-9_$]+|-)([\n][^\n])*)($|[\n][\n]+)'
parser_goaltree=re.compile(token_goaltree)

class goal:
	parser_item=re.compile(token_item)
	# node
	def __init__(self):
		self.constraints=[]
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
		lines=s.split('\n')
		for line in lines:
			m=self.__class__.parser_item.match(line)
			if isNone(m): continue
			res=m.group(1,2)
			self.add(res[1],int(res[0]),arrangeLater=True)
		return self
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
		self.sets={'-':0}
		pass
	def __repr__(self):
		rtv='{goaltree:\n'
		tmp=[ (k,v) for k,v in self.sets.items() ]
		tmp.sort()
		for x in tmp:
			rtv+="\t"+x[0]+":"+str(x[1])+",\n"
		rtv+='}'
		return rtv
	def addgoal(self,goal,name,successorName):
		# TODO
		pass
	def fromStr(self,s):
		'''
			character:'\r' is ommited
			format: see self.fromTxt
		'''
		s=s.replace('\r','')
		print(bytes(token_goaltree,"UTF-8"))
		m=self.__class__.parser_tree.match(s)
		if isNone(m): return
		#print('*',m.groups()) # debug
		data=[('-',0)]
		defined=set()
		blocks=m.group(1).split("\n\n\n")
		for block in blocks:
			#print('**',block) # debug
			m=self.__class__.parser_set.match(block)
			#print('***',m.groups()) # debug
			curr=m.group(1)
			succ=m.group(2)
			if curr in defined:
				raise TypeError("'"+curr+"' is defined twice")
			defined.add(curr)
			gsv=m.group(3).split("\n\n")
			data.append((curr,[succ]+[ goal().fromStr(gs) for gs in gsv ]))
			#data.sort()
		self.sets=dict(data)
		return self
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

