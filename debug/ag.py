#!/bin/python3
import os
import re
import sys
import json
from pprint import pprint

from shorthand import *
from amyhead import *

#charset_namespace="[A-Za-z0-9_$]+" # in 'shorthand'
#parser_goal=re.compile('[ \t]*([0-9]+)[ \t](.+)')
token_item='([\n]|^)([ \t]*\~?[0-9]+|[ \t]*\~?include|[ \t]*\~?gonear)[ \t]([^\n]+)'
#token_item_1='[ \t]*([0-9]+)[ \t]([^\n]+)'
#token_item='[\t]*\[[ \t]*[\n](([^\n]+[\n])+)[ \t]*\][ \t]*([\n]|$)'
token_nodeopt='(-pull|-push)([ \t]+'+charset_namespace+')*'
token_goalset = '(^|[\n])[ \t]*' # start : 1
token_goalset+= '('+charset_namespace+')[ \t]+('+charset_namespace+'|-)' # name,succ : 2
token_goalset+= '(([ \t]+'+charset_namespace+')*)' # pres : 2
token_goalset+= '(([ \t]+'+token_nodeopt+')*)' # pu** : 4
token_goalset+= '[ \t]*' # tailing
token_goalset+= '(([\n][\n]?[^\n]+)*)' # contentInSameNode : 2
token_goalset+= '([\n]+[\n](?=[\n])|[\n]?[\n]?$)' # sep : 2
# '(?=...)'Matches if ... matches next, but doesn’t consume any of the string.
sts=re.compile('[ \t]+')
nodeopt=re.compile('('+token_nodeopt+')')

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
	# is a sub-class of goaltree and should not be use directly
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
		self.extendedView=None # inherit from goaltree
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
	def fromStr(self,s,cd='./',extView=None):
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
		self.extendedView=None
		# an extendedView is an importlib.import_module() object
		# this can only be used when using 'fromTxt'
		# using 'fromStr' will remove (=None) previous extendedView from 'fromTxt'
		# file name is '_cd' and 'filename' given to 'fromTxt' concatenate '.py'
		# i.e. _cd+filename+".py"
		## it is recommended to construct a hashtable ( key is tuple(*.outputs()) or you can specify other methods ) with timeout to prevent re-calculating same condition within the same goal
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
	def getOpts(self,k):
		rtv=dict(self.sets[k][5])
		for i in rtv: rtv[i]=rtv[i][1]
		return rtv
	def getFinals(self):
		return [ k for k in self.sets if self.getSucc(k)=='-' ]
	def fromStr(self,s,cd='./',extView=None):
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
			opts = {"-push":(set(),[]),"-pull":(set(),[])} # (fooNamesLookup,fooContent)
			for opt in nodeopt.split(rs[i+5])[1::nodeopt.groups+1]:
				arr=sts.split(opt) # opt_type foo1 foo2 ...
				dest=[k for k in opts if arr[0]==k] # opt_type
				if len(dest)==0: raise TypeError("Error: "+arr[0]+" is not an option")
				arr,dst=tuple(arr[1:]),opts[dest[0]]
				if not (arr in dst[0]): # trim repeated
					dst[0].add(arr)
					dst[1].append([getattr(self.extendedView,f) for f in arr])
				else: print("warning: permutation:",arr,"in",dest[0],"already exists in this node")
			gsv  = re.split("[\n][ \t]*[\n]",rs[i+9]) # or
			data.append((curr, ([ goal().fromStr(gs,cd=cd,extView=self.extendedView) for gs in gsv ],succ,set(),[''],prec,opts) ))
			# curr:( goal()s , succ , succSet , succStrs , prec , opts)
		#data.sort()
		#print(defined),exit() # debug
		#print(sorted(list(defined))) # debug
		#pprint(data) # debug
		self.sets=dict(data)
		del data
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
		rtv=[ (v,k) for k,v in target.items() if len(self.getSuccs(k)&notBelow)==0 and valid_prec(k) ]
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

class goaltree_byweight:
	def __init__(self,goaltree=None):
		self.goal_final={}
		self.goal_nodes={}
		self.goal_nodes_names=[]
		if not isNone(goaltree): self.setRef(goaltree)
	def copy(self):
		rtv=self.__class__()
		rtv.goal_final=self.goal_final
		rtv.goal_nodes=copy.deepcopy(self.goal_nodes)
		rtv.goal_nodes_names.extend(self.goal_nodes_names)
		return rtv
	def setRef(self,goaltree):
		tmp={}
		wdata=self._setRef_weightedRecurr(goaltree)
		for goalnode_key in goaltree.sets:
			goalnode=goaltree.sets[goalnode_key]
			goalset=goalnode[0]
			#succ=goalnode[1]
			if succ!='-':
				tmp[self.goal_nodes]=([ wdata[goalnode_key] ],goalset)
				self.goal_nodes_names.append(goalnode_key)
			else:
				# finals
				self.goal_final[goalnode_key]=((wdata[goalnode_key],),goalset)
		self.goal_nodes.update(tmp)
	def _setRef_weightedRecurr(self,goaltree,_wdata=None,_currentPath=None,_beginNode=""):
		if _beginNode=="":
			nodeList=[ k for k in goaltree.sets ]
			wdata={}
			currentPath_d={}
			currentPath_v=[]
			for k in nodeList:
				if k in wdata: continue
				self._setRef_weightedRecurr(
					goaltree=goaltree,
					_wdata=wdata,
					_currentPath=(currentPath_d,currentPath_v),
					_beginNode=k
				)
			return wdata
		else:
			succ=goaltree.getSucc(_beginNode)
			currentPath_d,currentPath_v = _currentPath
			if succ=='-':
				# terminate
				_wdata[succ]=0 # finals' weights are 0
				loc=currentPath_d[succ]
				for i in range(loc): _wdata[currentPath_v[i]]=loc-i
			elif succ in currentPath_d:
				# cycle
				loc=currentPath_d[succ]
				for i in range(loc,len(currentPath_v)): _wdata[currentPath_v[i]]=0
				for i in range(loc): _wdata[currentPath_v[i]]=loc-i
			else:
				currentPath_d[_beginNode]=len(currentPath_v)
				currentPath_v.append(_beginNode)
				res=self._setRef_weightedRecurr(
					goaltree=goaltree,
					_wdata=_wdata,
					_currentPath=_currentPath,
					_beginNode=succ
				)
				currentPath_v.pop(_beginNode)
				del currentPath_d[_beginNode]
		_setRef_weightedRecurr
		pass
	def setWeight(self,kv={}):
		# kv = {"node_name":weight}
		for k in kv:
			if k in self.goal_nodes:
				w=self.goal_nodes[k][0]
				w.clear()
				if type(kv[k])==list: w.extend(kv[k])
				else: w.append(kv[k])
	def random(self):
		self.setWeight(dict([ (k,random.random()+1) for k in self.goal_nodes ]))
	def wkeys(self,currentKey,notBelow=None,beforeKeys=set()):
		# smaller (than 'currentKey') weight will be reserve
		# [but bigger weight (in reserved keys) at first]@asol.py
		# notBelow and beforeKeys is not used # in current version
		# inter-func.
		w=self.goal_nodes[currentKey][0]
		rtv=[]
		rtv_nodes = [ (v[0],k) for k,v in self.goal_nodes if v[0]>=w ]
		maxW=max(rtv_nodes)[0] if len(rtv_nodes)!=0 else 0
		rtv.extend([ (maxW,k) for k in self.goal_final ])
		rtv.extend(rtv_nodes)
		return rtv
	def mutate(self):
		for k in self.goal_nodes:
			w=self.goal_nodes[k][0]
			for i in range(len(w)):
				w[i]+=random.random()-0.5
	def cross(self,rhs,p=0.5):
		for k in self.goal_nodes_names:
			if random.random()<p:
				w=self.goal_nodes[k][0]
				w.clear()
				w.extend(rhs.goal_nodes[k][0])
		pass

