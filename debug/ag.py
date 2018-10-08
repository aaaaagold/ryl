#!/bin/python3
import re
import sys
from shorthand import *
from pprint import pprint

#parser_goal=re.compile('[ \t]*([0-9]+)[ \t](.+)')
token_item='([\n]|^)([ \t]*\~?[0-9]+|\~?include|\~?gonear)[ \t]([^\n]+)'
#token_item_1='[ \t]*([0-9]+)[ \t]([^\n]+)'
#token_item='[\t]*\[[ \t]*[\n](([^\n]+[\n])+)[ \t]*\][ \t]*([\n]|$)'
token_goalset='[ \t]*([A-Za-z0-9_$]+)[ \t]([A-Za-z0-9_$]+|-)[ \t]*(([\n][\n]?[^\n]+)*)([\n][\n][\n]+|[\n]?[\n]?$)'
sts=re.compile('[ \t]*')

class KWs:
	def __init__(self,kwv):
		self.data={}
		self.__cnt=0
		for kw in kwv:
			self.__cnt+=1
			tmp={"label":self.__cnt,"len":len(kw),"txt":kw}
			self[kw]=tmp
			self[self.__cnt]=tmp
	def getKwData(self,i):
		'''
			isinstance(i)==int or isinstance(i)==str
		'''
		return self.data[i] if i in self.data else None

class goal:
	parser_item=re.compile(token_item)
	#kwv=KWs(['include','gonear'])
	KW_include_label=-1
	KW_include_txt="include"
	KW_include_lentxt=len(KW_include_txt)
	KW_gonear_label=-2
	KW_gonear_txt="gonear"
	KW_gonear_lentxt=len(KW_gonear_txt)
	# node
	def __init__(self):
		self.constraints=[] # [ (int(label),item,negate?) ... ]
		self.maxLabel=-1
		self.including=False
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
			self.constraints.sort(key=lambda x:(x[2],x[:2]))
	def add(self,item,label=0,negate=False,arrangeLater=False):
		# label must be an integer
		self.constraints.append((label,item,negate))
		if self.maxLabel<label: self.maxLabel=label
		if arrangeLater==False: self.arrange()
		else: arrangeNeeded=arrangeLater
	def fromStr(self,s,cd='./'):
		'''
			character:'\r' is ommited
			this function will NOT do the arrangement
			make sure the lines of constraints:
				labels are in increasing order
				items of the same label are in lexicographical order
			
			format:
			each line: label item
			([ \t]*\~?[0-9]+|include|gonear)
			lines not match will be omitted
		'''
		old=self.constraints
		self.constraints=[]
		self.maxLabel=-1
		lines=s.split('\n')
		p=self.__class__.parser_item
		rs=p.split(s)
		#print('*'*11),pprint(rs) # debug
		for i in range(1,len(rs),p.groups+1):
			# not match , ([\n]|^) , [ \t]*\~?[0-9]+|KWs , [^\n]+
			# start from 1 =>
			# ([\n]|^) , [ \t]*[0-9]+|KWs , [^\n]+ , not match
			isKW=False
			negate=False
			label=sts.sub('',rs[i+1])
			if label[0]=='~':
				negate=True
				label=label[1:]
			content=rs[i+2]
			#print(rs[i],rs[i+1]) # debug
			if label==self.__class__.KW_include_txt:
				isKW=True
				label=self.__class__.KW_include_label
				self.including=True
				tmp=goaltree()
				tmp.fromTxt(content,_cd=cd)
				item=(content,tmp)

			if label==self.__class__.KW_gonear_txt:
				isKW=True
				label=self.__class__.KW_gonear_label
				tmp=None # TODO
				item=(content,tmp)

			if isKW==False:
				item=content
				label=int(label)

			self.add(item,label,negate=negate,arrangeLater=True)
		'''
		for line in lines:
			m=self.__class__.parser_item.match(line)
			if isNone(m): continue
			res=m.group(1,2)
			self.add(res[1],int(res[0]),arrangeLater=True)
			# TODO: need ORs
		'''
		return self
	def toStr(self,labelMinLen=0):
		length=max(len(str(self.maxLabel)),labelMinLen)
		if self.including:
			length=max(length,self.__class__.KW_include_lentxt)
		rtv=""
		tmpv=[]
		for c in self.constraints:
			useLen=length+c[2]
			label=c[0]
			content=c[1]
			if label==self.__class__.KW_include_label:
				useLen=0
				label=self.__class__.KW_include_txt
				content=c[1][0]
				#if 0!=0: tmpv.append(c[1][1].toStr(labelMinLen=length).split('\n')[1:])
			if label==self.__class__.KW_gonear_label:
				useLen=0
				label=self.__class__.KW_gonear_txt
				content=c[1][0]
			label=('~' if c[2] else '')+str(label)
			tmpv.append("%*s\t%s"%(useLen,label,content))
		rtv+='\n'.join(tmpv)
		return rtv
	def fromTxt(self,filename,_cd='./'):
		cd=_cd+filename[:filename.rindex('/')+1] if '/' in filename else _cd
		with open(_cd+filename,'rb') as f:
			self.fromStr("".join(map(chr,f.read())),cd=cd)
		return self
	def size(self):
		rtv={"byname":0,"bygoal":1}
		for c in self.constraints:
			if c[0]=="include":
				tmp=c[1][1].size()
				for k,v in tmp.items(): rtv[k]+=v
		return rtv

class goaltree:
	'''
		definitions:
			successor:
				the next goal to match after matching a goal
		closer the root(tree), closer the final goal
	'''
	parser_set=re.compile(token_goalset)
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
	def keys(self,notBelow=None):
		if isNone(notBelow):
			rtv=[k for k in self.sets]
			rtv.sort()
			return rtv
		else:
			#rtv=[k for k in self.sets if not self.getSucc(k) in notBelow]
			rtv=[k for k in self.sets if len(self.getSuccs(k)&notBelow)==0]
			rtv.sort()
			return rtv
	def getGoals(self,k):
		return self.sets[k][0] if k in self.sets else None
	def getSucc(self,k):
		return self.sets[k][1]
	def _getSuccs(self,k):
		# TODO
		rtvSet=set()
		rtvStr=k
		tmpsucc=self.getSucc(k)
		while not ( tmpsucc=='-' or tmpsucc=='+' or (tmpsucc in rtvSet) ):
			rtvSet.add(tmpsucc)
			rtvStr+='-'
			rtvStr+=tmpsucc
			tmpsucc=self.getSucc(tmpsucc)
		return rtvSet,rtvStr
	def getSuccs(self,k):
		return self.sets[k][2]
	def getSuccsStr(self,k):
		return self.sets[k][3][0]
	def getFinals(self):
		return [ k for k in self.sets if self.getSucc(k)=='-' ]
	def fromStr(self,s,cd='./'):
		'''
			\r\n , \n\r , \n -> \n
			format: see self.fromTxt
		'''
		old=self.sets
		p=self.__class__.parser_set
		s=re.sub("(\n\r|\n|\r\n)[ \t]+(\n\r|\n|\r\n)","\n\n",s)
		defined=set()
		data=[]
		rs=p.split(s) # cut via "\n\n\n"
		for i in range(1,len(rs),p.groups+1):
			# not match , currName , succName , goals , others
			# start from 1 =>
			# currName , succName , goals , others
			curr=rs[i  ]
			if curr in defined:
				raise TypeError("Error: '"+curr+"' is defined twice")
			defined.add(curr)
			succ = rs[i+1]
			gsv  = re.split("[\n][ \t]*[\n]",rs[i+2])
			data.append((curr, ([ goal().fromStr(gs,cd=cd) for gs in gsv ],succ,set(),['']) ))
		#data.sort()
		#pprint(data) # debug
		self.sets=dict(data)
		del data
		for k,v in self.sets.items():
			succSet,succStr=self._getSuccs(k)
			v[2].update(succSet)
			v[3][0]+=succStr
		return self
	def toStr(self,labelMinLen=0):
		kv=self.keys()
		rtv=""
		tmpv=[]
		for k in kv:
			tmps=""
			tmps+=k
			tmps+='\t'
			tmps+=self.getSucc(k)
			tmpgsv=[ g.toStr(labelMinLen=labelMinLen) for g in self.getGoals(k) ]
			tmpv.append('\n'.join([tmps,"\n\n".join(tmpgsv)]))
		rtv+="\n\n\n".join(tmpv)
		return rtv
	def fromTxt(self,filename,_cd='./'):
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
		cd=_cd+filename[:filename.rindex('/')+1] if '/' in filename else _cd
		with open(_cd+filename,'rb') as f:
			self.fromStr("".join(map(chr,f.read())),cd=cd)
		return self
	def size(self):
		rtv={"byname":len(self.sets),"bygoal":0}
		for _,d in self.sets.items():
			arr=d[0]
			for x in arr:
				tmp=x.size()
				for k,v in tmp.items(): rtv[k]+=v
		return rtv

###########

def matchGoal_v1(b,g):
	barr=b.rawBoard()
	for x in g.constraints:
		if str(barr[x[0]])!=str(x[1]):
			return False
	return True

def matchGoal_v2(b,g):
	barr=b.rawBoard()
	print(g),exit()
	for x in g.constraints:
		p=re.compile("([0-9]+):([0-9]+)")
		item=p.split(str(x[1]))
		matched=False
		for i in range(1,len(item),p.groups+1):
			loc = int(item[i  ])
			pn  = item[i+1]
			if str(barr[loc])==str(pn):
				matched=True
				break
		if matched==False:
			return False
	return True

def matchGoal_v3(b,g):
	barr=b.rawBoard()
	for x in g.constraints:
		isKW=False
		matched=False # if a cosntraint is matched
		if x[0]==g.__class__.KW_include_label:
			isKW=True
			for name in x[1][1].getFinals():
				goals=x[1][1].getGoals(name)
				if matchGoaltree_find_inSet(b,goals):
					matched=True
					break
		if isKW==False:
			p=re.compile("([0-9]+):([0-9]+)")
			item=p.split(str(x[1])) # may have several constraints, just one of them
			for i in range(1,len(item),p.groups+1):
				loc = int(item[i  ])
				pn  = item[i+1]
				if str(barr[loc])==str(pn):
					matched=True
					break
		if matched==False:
			return False
	return True

matchGoal=matchGoal_v3

def matchGoaltree_find_inSet(b,goals):
	for g in goals:
		if matchGoal(b,g):
			return True
	return False

def matchGoaltree_find(b,gt,notBelow=None):
	barr=b.rawBoard()
	rtv=[]
	for k in gt.keys(notBelow=notBelow):
		if matchGoaltree_find_inSet(b,gt.getGoals(k)):
			rtv.append(k)
	return rtv

def matchGoaltree_trim_v1(mv,gt):
	#mv=set(mv)
	mv=[ x for x in mv ]
	mv.sort()
	mv=[ mv[i] for i in range(len(mv)) if i==0 or mv[i-1]!=mv[i] ]
	rtv=[]
	tmpv=[]
	for k in mv:
		tmps=""
		tmpk=k
		while 0==0:
			tmps+=tmpk
			succ=gt.getSucc(tmpk)
			if succ=='-': break
			tmpk=succ
		tmpv.append((k,tmps))
	# TODO: need suffix array to speedup
	rg=range(len(tmpv))
	delSet=set()
	for i1 in rg:
		for i2 in rg:
			if i1==i2: continue
			if tmpv[i1][1] in tmpv[i2][1]:
				delSet.add(tmpv[i2][0])
	rtv+=[ k for k in mv if not k in delSet]
	return rtv

def matchGoaltree_trim_v2(mv,gt):
	#mv=set(mv)
	mv=[ x for x in mv ]
	mv.sort()
	mv=[ mv[i] for i in range(len(mv)) if i==0 or mv[i-1]!=mv[i] ]
	sv=[ (gt.getSuccs(k)|set([k]),k) for k in mv]
	#rtv=[]
	delSet=set()
	rg=range(len(sv))
	for i1 in rg:
		for i2 in rg:
			if i1==i2: continue
			s1,s2 = sv[i1][0],sv[i2][0]
			ss=s1&s2
			if len(ss)==len(s1): delSet.add(sv[i2][1])
			#if len(ss)==len(s2): delSet.add(sv[i1][1])
			del s1,s2,ss
	rtv=[ k for k in mv if not k in delSet ]
	return rtv

def matchGoaltree_trim_v3(mv,gt):
	#mv=list(set(mv))
	mv=[ x for x in mv ]
	mv.sort()
	mv=[ mv[i] for i in range(len(mv)) if i==0 or mv[i-1]!=mv[i] ]
	sv=[ (gt.getSuccsStr(k),k) for k in mv]
	# TODO: need suffix array to speedup
	rg=range(len(mv))
	delSet=set()
	for i1 in rg:
		for i2 in rg:
			if i1==i2: continue
			s1,s2 = sv[i1],sv[i2]
			if s1[0] in s2[0]:
				delSet.add(s2[1])
			del s1,s2
	rtv=[ k for k in mv if not k in delSet]
	return rtv

matchGoaltree_trim=matchGoaltree_trim_v3

def matchGoaltree(b,gt,notBelow=None):
	return matchGoaltree_trim(matchGoaltree_find(b,gt,notBelow),gt)


