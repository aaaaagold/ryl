#!/bin/python3
import os
import re
import sys
import json
from pprint import pprint

from shorthand import *
from amyhead import *

#parser_goal=re.compile('[ \t]*([0-9]+)[ \t](.+)')
token_item='([\n]|^)([ \t]*\~?[0-9]+|\~?include|\~?gonear)[ \t]([^\n]+)'
#token_item_1='[ \t]*([0-9]+)[ \t]([^\n]+)'
#token_item='[\t]*\[[ \t]*[\n](([^\n]+[\n])+)[ \t]*\][ \t]*([\n]|$)'
token_goalset='[ \t]*([A-Za-z0-9_$]+)[ \t]+([A-Za-z0-9_$]+|-)(([ \t]+[A-Za-z0-9_$]+)*)[ \t]*(([\n][\n]?[^\n]+)*)([\n][\n][\n]+|[\n]?[\n]?$)'
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
		# TODO:
		with open(_cd+filename+".learn",'rb') as f:
			pass
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
		self.filename=None
		self.learned={"nextgoal":{}}
		self.isSuccsOf={}
		# learn file is self.filename+".learn", self.filename will be set after self.fromTxt()
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
	def keys(self,notBelow=None,beforeKeys=set()):
		def valid_prec(k):
			precs=self.getPrecs(k)
			return len(precs)==0 or len(precs&beforeKeys)!=0
		if isNone(notBelow):
			rtv=[k for k in self.sets if valid_prec(k)]
			rtv.sort()
			return rtv
		else:
			#rtv=[k for k in self.sets if not self.getSucc(k) in notBelow]
			rtv=[k for k in self.sets if len(self.getSuccs(k)&notBelow)==0 and valid_prec(k)]
			rtv.sort()
			return rtv
	def getGoals(self,k):
		return self.sets[k][0] if k in self.sets else None
	def getSucc(self,k):
		return self.sets[k][1]
	def _getSuccs(self,k):
		rtvSet=set()
		rtvStr=k
		tmpsucc=self.getSucc(k)
		while not ( tmpsucc=='-' or tmpsucc=='+' or (tmpsucc in rtvSet) ):
			# rtv
			rtvSet.add(tmpsucc)
			rtvStr+='-'
			rtvStr+=tmpsucc
			# reversed succs
			#if not tmpsucc in self.isSuccsOf: self.isSuccsOf[tmpsucc]=set() # is set before
			self.isSuccsOf[tmpsucc].add(k)
			# next
			tmpsucc=self.getSucc(tmpsucc)
		return rtvSet,rtvStr
	def getSuccs(self,k):
		return self.sets[k][2]
	def getSuccsStr(self,k):
		return self.sets[k][3][0]
	def getPrecs(self,k):
		return self.sets[k][4]
	def getFinals(self):
		return [ k for k in self.sets if self.getSucc(k)=='-' ]
	def fromStr(self,s,cd='./'):
		'''
			\r\n , \n\r , \n -> \n
			format: see self.fromTxt
		'''
		# unset filename
		self.filename=None
		#old=self.sets
		p=self.__class__.parser_set
		s=re.sub("(\n\r|\n|\r\n)[ \t]+(\n\r|\n|\r\n)","\n\n",s)
		defined=set()
		data=[]
		rs=p.split(s) # cut via "\n\n\n"
		#print(rs[0:p.groups+1]),exit()
		for i in range(1,len(rs),p.groups+1):
			# not match , currName , succName , precNames , precName_Last , goals , others
			# start from 1 =>
			# currName , succName , precNames , precName , goals , others
			curr=rs[i  ]
			if curr in defined:
				raise TypeError("Error: '"+curr+"' is defined twice")
			defined.add(curr)
			succ = rs[i+1]
			prec = set(re.split("[ \t]+",rs[i+2])[1:]) # or
			gsv  = re.split("[\n][ \t]*[\n]",rs[i+4]) # and
			data.append((curr, ([ goal().fromStr(gs,cd=cd) for gs in gsv ],succ,set(),[''],prec) ))
			# curr:( goal()s , succ , succSet , succStrs , prec )
		#data.sort()
		#pprint(data) # debug
		self.sets=dict(data)
		del data
		self.isSuccsOf=dict([(k,set()) for k in self.sets])
		for k,v in self.sets.items():
			succSet,succStr=self._getSuccs(k)
			v[2].update(succSet)
			v[3][0]+=succStr
		'''
		isSuccsOf=dict([(k,set()) for k in allKeys])
		for k in allKeys:
			succs=self.getSuccs(k)
			for kk in succs:
				isSuccsOf[kk].add(k)
		'''
		allKeys=set([k for k in self.sets])
		for k in allKeys:
			self.learned["nextgoal"][k]=dict([ (kk,-len(self.getSuccs(kk))) for kk in allKeys-self.isSuccsOf[k] if kk!=k ])
		self.learned["nextgoal"][""]=dict([ (k,-len(self.getSuccs(k))) for k in allKeys if len(self.getPrecs(k))==0 ])
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
		filename=_cd+filename
		with open(filename,'rb') as f:
			self.fromStr("".join(map(chr,f.read())),cd=cd)
		self.filename=filename
		return self
	def size(self):
		rtv={"byname":len(self.sets),"bygoal":0}
		for _,d in self.sets.items():
			arr=d[0]
			for x in arr:
				tmp=x.size()
				for k,v in tmp.items(): rtv[k]+=v
		return rtv
	'''
		learn file
		a learn file records ordered goals of the successful paths
			probably
	'''
	def loadNextGoalFile(self,filename=None):
		# return True on error
		#  else False
		if isNone(filename): filename=self.filename
		if isNone(filename) or os.path.isfile(filename)==False: return True
		with open(filename) as f:
			self.learned["nextgoal"]=json.loads(f.read())["nextgoal"]
		return False
	def saveNextGoalFile(self,filename=None):
		# filename
		learnfile=""
		if isNone(filename):
			if isNone(self.filename):
				t0=str(time.time())
				t0+='0'*(t0.find('.')+8-len(t0))
				self.filename=t0.replace('.','-')
			learnfile+=self.filename+".learn"
		else: learnfile+=filename
		if os.path.isdir(learnfile): return True
		with open(learnfile,"w") as f:
			f.write(json.dumps(self.learned))
		return False
	def saveNextGoal(self,successSubgoalList):
		'''
			format of successSubgoalList is genSol()['nodes']
			i.e. a list of successful paths
		'''
		# data
		nextgoal=self.learned["nextgoal"]
		for arr in successSubgoalList:
			p=[""]+arr
			for i in range(1,len(p)):
				#print(p[i-1]) # debug
				if not p[i-1] in nextgoal: nextgoal[ p[i-1] ]={}
				curr=nextgoal[ p[i-1] ]
				if not p[i] in curr: curr[ p[i] ]=0
				curr[ p[i] ]+=1
		return False
	def wkeys(self,currentKey,notBelow=None,beforeKeys=set()):
		'''
		* weighted keys *
		# ref-rtv
		if isNone(notBelow):
			rtv=[k for k in self.sets]
			rtv.sort()
			return rtv
		else:
			#rtv=[k for k in self.sets if not self.getSucc(k) in notBelow]
			rtv=[k for k in self.sets if len(self.getSuccs(k)&notBelow)==0]
			rtv.sort()
			return rtv
		'''
		# inter-func.
		def valid_prec(k):
			precs=self.getPrecs(k)
			return len(precs)==0 or len(precs&beforeKeys)!=0
		if isNone(notBelow): notBelow=set()
		if type(notBelow)!=set: notBelow=set(notBelow)
		# data
		#validKeys=[k for k in self.sets if len(self.getSuccs(k)&notBelow)==0]
		nextgoal=self.learned["nextgoal"]
		target=nextgoal[currentKey] if currentKey in nextgoal else {}
		rtv=[ (v,k) for k,v in target.items() if len(self.getSuccs(k)&notBelow)==0 and valid_prec(k) ]
		#rtv+=[ (0,k) for k in self.sets if (not k in target) and len(self.getSuccs(k)&notBelow)==0]
		#rtv.sort(reverse=True) # leave it to caller
		return rtv
		

###########
