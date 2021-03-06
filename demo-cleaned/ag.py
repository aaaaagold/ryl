﻿#!/bin/python3
import os
import re
import sys
import json
from pprint import pprint

from shorthand import *
from amyhead import *

#charset_namespace="[A-Za-z0-9_$]+" # in 'shorthand'
#parser_goal=re.compile('[ \t]*([0-9]+)[ \t](.+)')
token_item=r'([\n]|^)([ \t]*\~?[0-9]+|[ \t]*\~?include|[ \t]*\~?gonear)[ \t]+([^ \t][^\n]*)'
#token_item_1='[ \t]*([0-9]+)[ \t]([^\n]+)'
#token_item='[\t]*\[[ \t]*[\n](([^\n]+[\n])+)[ \t]*\][ \t]*([\n]|$)'
token_nodeopt=r'(-pull|-push)([ \t]+'+charset_namespace+r')*'
token_goalset = r'(^|[\n])[ \t]*' # start : 1
token_goalset+= r'('+charset_namespace+r')[ \t]+('+charset_namespace+r'|-)' # name,succ : 2
token_goalset+= r'(([ \t]+'+charset_namespace+r')*)' # pres : 2
token_goalset+= r'(([ \t]+'+token_nodeopt+r')*)' # pu** : 4
token_goalset+= r'[ \t]*' # tailing
token_goalset+= r'(([\n][\n]?[^\n]+)*)' # contentInSameNode : 2
token_goalset+= r'([\n]+[\n](?=[\n])|[\n]?[\n]?$)' # sep : 2
# '(?=...)'Matches if ... matches next, but doesn’t consume any of the string.
sts=re.compile(r'[ \t]+')
nodeopt=re.compile(r'('+token_nodeopt+r')')

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

class Goal:
	# a part of goalset
	# is a sub-class of Goaltree and should not be use directly
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
		self.extendedView=None # inherit from Goaltree
	def __eq__(self,rhs):
		self.arrange()
		if isinstance(rhs,self.__class__):
			return self.constraints==rhs.constraints
		else:
			raise TypeError("unsupport: %s == %s"%(self.__class__,type(rhs)))
	def __repr__(self):
		return "[Goal:"+str(self.constraints)+"]"
	def isSpecial(self):
		# having constraints labels != 0
		for c in self.constraints:
			if c[0]!=0:
				return 1
		return 0
	def flatten(self):
		add=[]
		delItSet=set()
		rg=range(len(self.constraints))
		for i in rg:
			c=self.constraints[i]
			if c[0]==self.__class__.KW_include_label:
				src=c[1][1]
				if len(src.sets)<=1 and len(src.pushs(""))==0 and len(src.pulls(""))==0:
					cFinalGs=src[src.getFinals()[0]][0]
					if len(cFinalGs)<=1 and cFinalGs[0].isSpecial()==0:
						add+=cFinalGs[0].constraints
						delItSet.add(i)
		if len(add)!=0:
			newCs=[ self.constraints[i] for i in rg if not i in delItSet ]
			self.constraints=newCs
			for c in add:
				self.add(c[1],c[0],c[2],arrangeLater=True)
			self.arrange()
		return self
	def arrange(self):
		if self.arrangeNeeded!=False:
			self.arrangeNeeded=False
			self.constraints.sort(key=lambda x:(x[2],x[:2]))
			tmpv=[]
			tmp=0
			for c in self.constraints:
				if tmp==c: continue
				tmpv.append(c)
				tmp=c
			self.constraints=tmpv
			if len([ c[0] for c in tmpv if c[0]==-1])==0:
				self.including=False
		return self
	def add(self,item,label=0,negate=False,arrangeLater=False):
		# label must be an integer
		self.constraints.append((label,item,negate))
		if self.maxLabel<label: self.maxLabel=label
		if arrangeLater==False: self.arrange()
		else: self.arrangeNeeded=arrangeLater
	def fromStr(self,s,cd='./',extView=None):
		s=s.replace('\r','')
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
		# preserve
		old=self.constraints
		# clean
		self.constraints=[]
		self.maxLabel=-1
		self.extendedView=extView
		# start
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
				tmp=Goaltree()
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
			useLen=length+c[2] # len of neg no usage
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
	def fromTxt(self,filename,_cd='./',extView=None):
		cd=_cd+filename[:filename.rindex('/')+1] if '/' in filename else _cd
		with open(_cd+filename,'rb') as f:
			self.fromStr("".join(map(chr,f.read())),cd=cd,extView=extView)
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

class Goaltree:
	# lots of goalset
	'''
		definitions:
			successor:
				the next goalset to match after matching a goalset
		closer the root(tree), closer the final goalset
	'''
	parser_set=re.compile(token_goalset)
	def __init__(self):
		self.sets={}
		self.filename=None
		self.extendedView=None
		# an extendedView is an importlib.import_module() object
		# this can only be used when using 'fromTxt'
		# using 'fromStr' will remove (=None) previous extendedView from 'fromTxt'
		# file name is '_cd' and 'filename' given to 'fromTxt' concatenate '.py'
		# i.e. _cd+filename+".py"
		## it is recommended to construct a hashtable ( key is tuple(*.outputs()) or you can specify other methods ) with timeout to prevent re-calculating same condition within the same goal to achive
		self.learned={"nextgoal":{}}
		self.isSuccsOf={}
		# learn file is self.filename+".learn", self.filename will be set after self.fromTxt()
		pass
	def __repr__(self):
		rtv='{Goaltree:\n'
		tmp=[ (k,v) for k,v in self.sets.items() ]
		tmp.sort()
		for x in tmp:
			rtv+="\t"+x[0]+":"+str(x[1])+",\n"
		rtv+='\t-:0\n}'
		return rtv
	def __getitem__(self,k):
		return self.sets[k] if k in self.sets else None
	def newNode(self,goals=[],name="",successorName='-'):
		node=(goals,successorName,set(),[''])
		return name,node
	def addNode(self,goalset=[],name="",successorName='-'):
		# TODO
		if name=="" or (name in self.sets): return 1
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
		# return a goalset
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
	def getOpts(self,k):
		rtv=dict(self.sets[k][5])
		for i in rtv: rtv[i]=rtv[i][1]
		return rtv
	def getFinals(self):
		return [ k for k in self.sets if self.getSucc(k)=='-' ]
	def fromStr(self,s,cd='./',extView=None):
		s=s.replace('\r','')
		'''
			\r\n , \n\r , \n -> \n
			format: see self.fromTxt
		'''
		# unset filename
		self.filename=None
		self.extendedView=extView
		#old=self.sets
		p=self.__class__.parser_set
		s=re.sub("(\n\r|\n|\r\n)[ \t]*(\n\r|\n|\r\n)","\n\n",s)
		defined=set()
		data=[]
		rs=p.split(s) # cut via "\n\n\n"
		#print(p.groups+1),print(rs[1:1+p.groups+1]),print(rs[1+(p.groups+1)*1:1+(p.groups+1)*2]),exit()
		#print(rs[0]),exit() # debug
		for i in range(1,len(rs),p.groups+1):
			# rs[0] is "not match", omitted
			# start from 1 =>
			# (^|[\n]) , currName , succName , precNames , precName_last , pu** , pu**_last , (-pull|-push) , pu**_func_last , goals , others
			#    +0    ,    +1    ,    +2    ,    +3     ,      +4       ,  +5  ,    +6     ,      +7       ,       +8       ,  +9   ,  + >=10
			#print(i,p.groups+1,rs[i-1]),print(rs[i:i+p.groups+1]) # debug
			#if i>p.groups: exit() # debug
			curr=rs[i+1]
			if curr in defined:
				raise TypeError("Error: '"+curr+"' is defined twice")
			defined.add(curr)
			#print(i,curr,defined) # debug
			succ = rs[i+2]
			prec = set(sts.split(rs[i+3])[1:]) # or
			opts = {"-push":(set(),[],[]),"-pull":(set(),[],[])} # (fooNamesLookupForRepeated,fooContent)
			for opt in nodeopt.split(rs[i+5])[1::nodeopt.groups+1]:
				arr=sts.split(opt) # opt_type foo1 foo2 ...
				dest=[k for k in opts if arr[0]==k] # opt_type
				if len(dest)==0: raise TypeError("Error: "+arr[0]+" is not an option")
				arr,dst=tuple(arr[1:]),opts[dest[0]]
				if not (arr in dst[0]): # trim repeated combination
					dst[0].add(arr)
					dst[1].append([getattr(self.extendedView,f) for f in arr])
				else: print("warning: permutation:",arr,"in",dest[0],"already exists in this node")
				dst[2].append(arr)
			gsv  = re.split("[\n][ \t]*[\n]",rs[i+9]) # or
			data.append((curr, ([ Goal().fromStr(gs,cd=cd,extView=self.extendedView).flatten() for gs in gsv ],succ,set(),[''],prec,opts) ))
			# curr:( Goal()s , succ , succSet , succStrs , prec , opts)
		#data.sort()
		#print(defined),exit() # debug
		#print(sorted(list(defined))) # debug
		#pprint(data) # debug
		self.sets=dict(data)
		del data
		'''
		def getTarget(c):
			tmp=c[1].split(":")[1] if ":" in c[1] else c[1]
			return c[0],tmp,c[2]
		for k in self.sets:
			node=self.sets[k]
			if node[1]=='-': continue
			gs_node=node[0]
			if len(gs_node)!=1: continue
			gs_node=gs_node[0]
			gs_node.arrange()
			sn=set(gs_node.constraints)
			succ=self.sets[node[1]]
			gs_succ=succ[0]
			for g in gs_succ:
				if abs(len(g.constraints)-len(sn))>1: continue
				ss=set(g.constraints)
				delta=ss^sn
				if len(delta)>2: continue
				rem_sn,rem_ss=delta&sn,delta&ss
				if len(rem_sn)!=1 or len(rem_ss)!=1: continue # no idea how to do
				rem_sn,rem_ss=rem_sn.pop(),rem_ss.pop()
				if not (":" in rem_sn[1] or ":" in rem_ss[1]): continue # not value
				rem1_sn=re.split(r'[ \t]+',rem_sn[1])
				rem1_ss=re.split(r'[ \t]+',rem_ss[1])
				if len(rem1_sn)!=len(rem1_ss)!=1: continue
				rem1_sn.sort(),rem1_ss.sort()
				diff=[]
				for i in range(len(rem1_sn)):
					if rem1_sn[i]!=rem1_ss[i]:
						diff.append((rem1_sn[i],rem1_ss[i]))
				if len(diff)!=1 or diff[0]==diff[1]: continue
				target=[ x[:x.index(":")] for x in diff ]
				if target[0]!=target[1]: continue
				vals=[ x[len(target[0])+1:] for x in diff ]
				if not ',' in vals[0]: vals[0]=vals[0]+','+vals[0]
				if not ',' in vals[1]: vals[1]=vals[1]+','+vals[1]
			newNodes=[]
			if vals[0]
			print("?",gs_node),exit()
		'''
		self.isSuccsOf=dict([(k,set()) for k in self.sets])
		for k,v in self.sets.items():
			succSet,succStr=self._getSuccs(k)
			v[2].update(succSet)
			v[3][0]+=succStr
		# basic keys
		allKeys=set([k for k in self.sets])
		for k in allKeys:
			# all lower nodes
			self.learned["nextgoal"][k]=dict([ (kk,(0.0-len(self.getSuccs(kk)))/len(allKeys)) for kk in allKeys-self.isSuccsOf[k] if kk!=k ])
		self.learned["nextgoal"][""]=dict([ (k,(0.0-len(self.getSuccs(k)))/len(allKeys)) for k in allKeys if len(self.getPrecs(k))==0 ])
		return self
	def toStr(self,labelMinLen=0):
		kv=[ k for k in self.sets ]
		kv.sort()
		rtv=""
		tmpv=[]
		for k in kv:
			tmps=""
			tmps+=k+'\t'+self.getSucc(k)
			if len(self.getPrecs(k))!=0:
				tmps+='\t'.join([""]+sorted([ kk for kk in self.getPrecs(k) ]))
			opts=self.sets[k][5]
			optstrs=[]
			for opt in sorted([_ for _ in opts]):
				if len(opts[opt][2])!=0:
					optstrs.append('\t'.join([x for v in opts[opt][2]for x in[opt]+list(v)]))
			tmps+='\t'.join([""]+optstrs)
			tmpgsv=[ g.toStr(labelMinLen=labelMinLen) for g in self.getGoals(k) ]
			tmpv.append('\n'.join([tmps,"\n\n".join(tmpgsv)]))
		rtv+="\n\n\n".join(tmpv)
		return rtv
	def fromTxt(self,filename,_cd='./'):
		'''
			concept:
			a block with a name is a set of Goal. that means reach one of them is a 'match', and can to further more (try the successor)
		'''
		'''
			format prototype:

			( none or more empty lines )
			...
			( none or more empty lines )
			name successorName(if None, use '-')
			# lines which cannot be parsed as <class: Goal>
			label item
			# lines which cannot be parsed as <class: Goal>
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
		try:
			path=filename+".py"
			if os.path.isfile(path):
				spec = importlib.util.spec_from_file_location(filename,path)
				self.extendedView = importlib.util.module_from_spec(spec)
				spec.loader.exec_module(self.extendedView)
				#print(inspect.getsource(self.extendedView)) # debug
		except:
			print("WARNING: file exists but it cannot be import:",path)
		with open(filename,'rb') as f:
			self.fromStr("".join(map(chr,f.read())),cd=cd,extView=self.extendedView)
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
			# control upper nodes to return
			# True === valid , i.e. will be return from 'wkeys'
			# it takes 'beforeKeys' to check if there's at least 1 presenting in 'precs'
			precs=self.getPrecs(k)
			return len(precs)==0 or len(precs&beforeKeys)!=0
		if isNone(notBelow): notBelow=set()
		if type(notBelow)!=set: notBelow=set(notBelow)
		# data
		#validKeys=[k for k in self.sets if len(self.getSuccs(k)&notBelow)==0]
		nextgoal=self.learned["nextgoal"]
		target=nextgoal[currentKey] if currentKey in nextgoal else {}
		rtv=[ (v,k) for k,v in target.items() if k in self.sets and len(self.getSuccs(k)&notBelow)==0 and valid_prec(k) ]
		#rtv+=[ (0,k) for k in self.sets if (not k in target) and len(self.getSuccs(k)&notBelow)==0]
		#rtv.sort(reverse=True) # leave it to caller
		return rtv
	def pulls(self,currentKey,notBelow=None,beforeKeys=set(),wkeys=None):
		# return how other nodes can pull
		# if 'wkeys' is not None: notBelow && beforeKeys will be omitted
		#   note: if wkeys is not sublist from self.wkeys, it might cause errors
		if isNone(wkeys):
			wkeys=self.wkeys(currentKey=currentKey,notBelow=notBelow,beforeKeys=beforeKeys)
			wkeys.sort()
		return [ hv for vk in wkeys for hv in self.getOpts(vk[1])["-pull"] ]
	def pushs(self,currentKey):
		# return how can the node push
		rtv=[] if not currentKey in self.sets else self.getOpts(currentKey)["-push"]
		return rtv
		

###########
