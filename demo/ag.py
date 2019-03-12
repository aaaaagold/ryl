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
			opts = {"-push":(set(),[]),"-pull":(set(),[])} # (fooNamesLookupForRepeated,fooContent)
			for opt in nodeopt.split(rs[i+5])[1::nodeopt.groups+1]:
				arr=sts.split(opt) # opt_type foo1 foo2 ...
				dest=[k for k in opts if arr[0]==k] # opt_type
				if len(dest)==0: raise TypeError("Error: "+arr[0]+" is not an option")
				arr,dst=tuple(arr[1:]),opts[dest[0]]
				if not (arr in dst[0]): # trim repeated combination
					dst[0].add(arr)
					dst[1].append([getattr(self.extendedView,f) for f in arr])
				else: print("warning: permutation:",arr,"in",dest[0],"already exists in this node")
			gsv  = re.split("[\n][ \t]*[\n]",rs[i+9]) # or
			data.append((curr, ([ Goal().fromStr(gs,cd=cd,extView=self.extendedView) for gs in gsv ],succ,set(),[''],prec,opts) ))
			# curr:( Goal()s , succ , succSet , succStrs , prec , opts)
		#data.sort()
		#print(defined),exit() # debug
		#print(sorted(list(defined))) # debug
		#pprint(data) # debug
		self.sets=dict(data)
		del data
		for k in self.sets:
			for kk in self.sets:
				if k==kk: continue
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
			a block with a name is a set of Goal. that means reach one of them is a 'match', and can to further more (try the successor)
			
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

class goaltree_edgeless:
	cnt_newNode=0
	cnt_newGoal=0
	def __init__(self,goaltree=None):
		self.extendedView=None
		self.goal_final={}
		self.goal_nodes={}
		# [k]=>([weight_vector],goalset_from_goaltree,{meta})
		# the order to be used is from greatest ( far from final ) to the least ( close to final )
		self.goal_nodes_names=[]
		#self.goal_nodes_usedCnt={} # "name":int_cnt
		self.oriNodes=[]
		self.oriNodes_dict={}
		self.cache_succsStr={}
		if not isNone(goaltree):
			self.setRef(goaltree)
	def clean_cache(self):
		self.cache_succsStr={}
	def copy(self):
		rtv=self.__class__()
		rtv.goal_final=self.goal_final
		tmp={}
		for k in self.goal_nodes:
			t=self.goal_nodes[k]
			tt=([],t[1].copy(),{})
			tt[0].extend(t[0])
			for kk,vv in t[2].items(): tt[2][kk]=copy.deepcopy(vv)
			tmp[k]=tt
		rtv.goal_nodes=tmp
		rtv.goal_nodes_names.extend(self.goal_nodes_names)
		rtv.cache_succsStr=self.cache_succsStr
		rtv.extendedView=self.extendedView
		rtv.oriNodes=self.oriNodes
		rtv.oriNodes_dict=self.oriNodes_dict
		#rtv.goal_nodes_usedCnt.update(self.goal_nodes_usedCnt)
		return rtv
	def _setRef_oth(self,goaltree):
		self.extendedView=goaltree.extendedView
		self.oriNodes.clear()
		self.oriNodes.extend(self.goal_nodes_names)
		self.oriNodes.sort(key=lambda x:self.goal_nodes[x][0])
		self.oriNodes_dict=dict([ (self.oriNodes[i],i) for i in range(len(self.oriNodes)) ])
	def setRef(self,goaltree):
		self.__init__()
		self.clean_cache()
		#self.goal_nodes.clear()
		#self.goal_nodes_names.clear()
		tmp={}
		wdata=self._setRef_weightedRecurr(goaltree)
		for goalnode_key in goaltree.sets:
			goalnode=goaltree.sets[goalnode_key]
			goalset=goalnode[0] # a list
			succ=goalnode[1] # a str
			precs=goalnode[4] # a set
			if succ!='-':
				tmp[goalnode_key]=([ wdata[goalnode_key] ],goalset,{
					"precs":precs
				})
				self.goal_nodes_names.append(goalnode_key)
			else:
				# finals
				# wdata[goalnode_key]===0
				self.goal_final[goalnode_key]=([ wdata[goalnode_key] ],goalset,{
					"precs":precs
				})
		self.goal_nodes.update(tmp)
		self._setRef_oth(goaltree)
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
				# _beginNode is in finals
				_wdata[_beginNode]=0 # finals' weights are 0
				loc=len(currentPath_v)
				for i in range(loc): _wdata[currentPath_v[i]]=i-loc
			elif succ in currentPath_d:
				# cycle
				loc=currentPath_d[succ]
				for i in range(loc,len(currentPath_v)): _wdata[currentPath_v[i]]=0
				for i in range(loc): _wdata[currentPath_v[i]]=i-loc
			else:
				currentPath_d[_beginNode]=len(currentPath_v)
				currentPath_v.append(_beginNode)
				res=self._setRef_weightedRecurr(
					goaltree=goaltree,
					_wdata=_wdata,
					_currentPath=_currentPath,
					_beginNode=succ
				)
				currentPath_v.pop()
				del currentPath_d[_beginNode]
		# _setRef_weightedRecurr END
	def setWeight(self,kv={}):
		self.clean_cache()
		# kv = {"node_name":weight}
		for k in kv:
			if k in self.goal_nodes:
				w=self.goal_nodes[k][0]
				w.clear()
				if type(kv[k])==list: w.extend(kv[k])
				else: w.append(kv[k])
	def random(self):
		self.clean_cache()
		self.setWeight(dict([ (k,random.random()-1) for k in self.goal_nodes ]))
	def getGoals(self,k):
		# return a goalset
		if k in self.goal_final: return self.goal_final[k][1]
		if k in self.goal_nodes: return self.goal_nodes[k][1]
		return None
	def getSuccsStr(self,k):
		# TODO
		if k in self.cache_succsStr: return self.cache_succsStr[k]
		if k in self.goal_final: return k
		baseW=self.goal_nodes[k][0]
		arr=[ (self.goal_nodes[kk][0],kk) for kk in self.goal_nodes if k==kk or baseW<self.goal_nodes[kk][0] ]
		arr.sort()
		rtv='-'.join([ x[1] for x in arr ])
		self.cache_succsStr[k]=rtv
		return rtv
	def getFinals(self):
		return [ k for k in self.goal_final ]
	def hasNode(self,k):
		return (k in self.goal_nodes) | (k in self.goal_final)
	def getPrecs(self,k):
		tmp=self.getNode(k)[2]
		if "precs" in tmp: return tmp["precs"]
		return set()
	def size(self):
		rtv={"byname":len(self.goal_final)+len(self.goal_nodes),"bygoal":0}
		for _,d in self.goal_final.items():
			arr=d[1]
			for x in arr:
				tmp=x.size()
				for k,v in tmp.items(): rtv[k]+=v
		for _,d in self.goal_nodes.items():
			arr=d[1]
			for x in arr:
				tmp=x.size()
				for k,v in tmp.items(): rtv[k]+=v
		return rtv
	def pushs(self,currentKey):
		# TODO
		return ()
	def pulls(self,currentKey,notBelow=None,beforeKeys=set(),wkeys=None):
		# TODO
		if isNone(wkeys):
			wkeys=self.wkeys(currentKey=currentKey,notBelow=notBelow,beforeKeys=beforeKeys)
			wkeys.sort()
		return ()
	def allkeys(self):
		rtv=[ (v[0],k) for k,v in self.goal_nodes ]
		rtv.extend([(v[0],k) for k,v in self.goal_final ])
		rtv.sort(key=lambda x:x[0])
		return rtv
	def wkeys(self,currentKey,notBelow=None,beforeKeys=set()):
		# bigger (than 'currentKey') weight will be reserved
		# [and bigger weight (in reserved keys) at first]@asol.py
		# finals will be tested first. for others: nearest (to final) first
		# ( === finals have greatest weight )
		# notBelow and beforeKeys is not used # in current version
		# inter-func.
		def valid_prec(k):
			# control upper nodes to return
			# True === valid , i.e. will be return from 'wkeys'
			# it takes 'beforeKeys' to check if there's at least 1 presenting in 'precs'
			precs=self.getPrecs(k)
			return len(precs)==0 or len(precs&beforeKeys)!=0
		# inter-func. END
		minW=self.goal_nodes[currentKey][0] if currentKey in self.goal_nodes else nINF_v1
		rtv=[]
		rtv_nodes = [ (v[0],k) for k,v in self.goal_nodes.items() if minW<v[0] and valid_prec(k) ]
		rtv_nodes.sort()
		#rtv_nodes=[rtv_nodes[0]] # debug
		maxW=(max(rtv_nodes)[0]+[0]) if len(rtv_nodes)!=0 else [0]
		# let finals be tested first
		rtv.extend([ (maxW,k) for k in self.goal_final if valid_prec(k) ])
		rtv.extend(rtv_nodes)
		return rtv
	
	def getNextNodeNames(self,curr=""):
		if len(self.oriNodes)==0 or self.oriNodes[-1]==curr: return self.goal_final.keys()
		return [self.oriNodes[self.oriNodes_dict[curr]+1 if curr in self.oriNodes_dict else 0]]
	def getNode(self,name):
		return self.goal_final[name] if name in self.goal_final else self.goal_nodes[name]
	def _newNode(self):
		self.clean_cache()
		self.__class__.cnt_newNode+=1
		name="ec_%d"%(self.__class__.cnt_newNode,)
		node=([0],[],{})
		return name,node
	def newNodeByGoals(self,gs=[]):
		rtv=self._newNode()
		rtv[1][1].extend(gs)
		return rtv
	def addNodes(self,ns):
		for n in ns:
			self.goal_nodes_names.append(n[0])
			self.goal_nodes[n[0]]=n[1]
	def _newGoal(self):
		self.__class__.cnt_newGoal+=1
		name="ec_%d"%(self.__class__.cnt_newGoal,)
		g=Goal()
		g.extendedView=self.extendedView
		return name,g
	def newGoal(self):
		# empty goal
		return self._newGoal()
	def newGoal_fromConstraints(self,cs,p_contraintSelected=0.5,p_negateRatio=0.5,base=None):
		rtv=self._newGoal() if isNone(base) else base
		for c in cs:
			if random.random()<p_contraintSelected:
				rtv[1].add(item=c[1],label=c[0],negate=c[2]^(random.random()<p_negateRatio),arrangeLater=True)
		rtv[1].arrange()
		return rtv
	
	def newGoal_sparse(self,g,p_contraintSelected=0.5,p_negateRatio=0.5):
		cs=g.constraints
		return self.newGoal_fromConstraints(cs,p_contraintSelected,p_negateRatio)
	def newNode_sparse(self,node,p_contraintSelected=0.5,p_negateRatio=0.5):
		g=self.newGoal_sparse(random.choice(node[1]),p_contraintSelected,p_negateRatio)
		if len(g[1].constraints)==0: return None
		return self.newNodeByGoals([g[1]])
	
	def _newGoal_noise_noisify(self,c):
		# TODO noise in RealNumber and Range
		if c[0]<0: return c # special definitions
		rtv=list(c)
		rtv1v=re.split("[ ]+",rtv[1])
		newrtv1strs=[]
		for c in rtv1v:
			if not ":" in c: continue
			rtv1s=c.split(":")
			#print(rtv1s) # debug
			#newVal=int(rtv1s[1])+int(random.random()*15)-7
			newVal=''
			if ',' in rtv1s[1]:
				tmp=rtv1s[1].split(',')
				tmp=[ int(x)+int(random.random()*3-1) for x in tmp ]
				if tmp[0]>tmp[1]:
					tmp2=sum(tmp)
					if tmp2&1:
						tmp[0]=(tmp2+0)>>1
						tmp[1]=(tmp2+1)>>1
					else: tmp[1]=tmp[0]=tmp2
				tmp=[str(x) for x in tmp]
				newVal+=','.join(tmp)
			else:
				# suppose integer
				v=int(rtv1s[1])
				dx=int(random.random()*3)-1
				dy=int(random.random()*3)-1
				if not ( (v% 4==0 and dx<0) or (v% 4==3 and dx>0) ): v+=dx
				if not ( (v//4==0 and dy<0) or (v//4==3 and dy>0) ): v+=dy
				newVal+=str(v)
			newrtv1strs.append(rtv1s[0]+":"+str(newVal))
		rtv[1]=' '.join(newrtv1strs)
		#print(rtv[1]) # debug
		return tuple(rtv)
	def newGoal_noise(self,g,p_contraintSelected=1,p_negateRatio=0):
		cs=g.constraints
		cs=[self._newGoal_noise_noisify(c) for c in cs]
		return self.newGoal_fromConstraints(cs,p_contraintSelected,p_negateRatio)
	def newNode_noise(self,node,p_contraintSelected=1,p_negateRatio=0):
		g=self.newGoal_noise(random.choice(node[1]),p_contraintSelected,p_negateRatio)
		if len(g[1].constraints)==0: return None
		return self.newNodeByGoals([g[1]])
	
	def newGoal_merge(self,g1,g2,p_contraintSelected=0.5,p_negateRatio=0.5):
		cs=g1.constraints+g2.constraints
		return self.newGoal_fromConstraints(cs,p_contraintSelected,p_negateRatio)
	def newNode_merge(self,n1,n2,p_contraintSelected=0.5,p_negateRatio=0.5):
		g1=random.choice(n1[1])
		g2=random.choice(n2[1])
		g=self.newGoal_merge(g1,g2,p_contraintSelected,p_negateRatio)
		if len(g[1].constraints)==0: return None
		return self.newNodeByGoals([g[1]])
	
	def newGoal_noiseDiff(self,base,more,p_contraintSelected=0.5,p_negateRatio=0.5):
		csb=set(base.constraints)
		csm=set(more.constraints)
		cs=csb^csm
		cs=[self._newGoal_noise_noisify(c) for c in cs]
		rtv=self.newGoal_fromConstraints(cs,p_contraintSelected,p_negateRatio)
		return self.newGoal_fromConstraints(base.constraints,1,0,base=rtv)
	def newNode_noiseDiff(self,base,more,p_contraintSelected=1,p_negateRatio=0.5):
		gb=random.choice(base[1])
		gm=random.choice(more[1])
		g=self.newGoal_noiseDiff(gb,gm,p_contraintSelected,p_negateRatio)
		if len(g[1].constraints)==len(gb.constraints): return None
		return self.newNodeByGoals([g[1]])
	
	def newGoal_fromFinal(self,p_contraintSelected=0.5,p_negateRatio=0.5):
		cs=random.choice(self.goal_final[random.choice([ k for k in self.goal_final ])][1]).constraints
		return self.newGoal_fromConstraints(cs,p_contraintSelected,p_negateRatio)
	def newNode_fromFinal(self,p_contraintSelected=0.5,p_negateRatio=0.5):
		g=self.newGoal_fromFinal(p_contraintSelected,p_negateRatio)
		if len(g[1].constraints)==0: return None
		return self.newNodeByGoals([g[1]])
	
	def _mutate_randWeight(self,strt="",p=1):
		# random adjust weights
		useDefault=(not strt in self.oriNodes_dict)
		minW=nINF_v1 if useDefault else self.goal_nodes[strt][0]
		maxW=self.getNode(self.getNextNodeNames(strt)[0])[0]
		deltaW=None if useDefault else maxW[0]-minW[0]
		for k,v in self.goal_nodes.items():
			if minW<=v[0] and v[0]<=maxW and (not k in self.oriNodes_dict) and random.random()<p:
				w=v[0]
				if useDefault:
					#for i in range(len(w)):
					#	w[i]+=random.random()*32-16
					w[0]+=random.random()*32-16
					w[0]=min(w[0],maxW[0]-1)
				else:
					w.clear()
					w.extend([random.random()*deltaW+minW[0]])
		pass
	def _mutate_getCandi(self,strt=""):
		# get nodes whose wegiht > strt's and <= next(strt)'s
		useDefault=(not strt in self.goal_nodes)
		minW=nINF_v1 if useDefault else self.goal_nodes[strt][0]
		maxW=self.getNode(self.getNextNodeNames(strt)[0])[0]
		rtv=[ (v,k) for k,v in self.goal_nodes.items() if useDefault or (minW<v[0] and v[0]<=maxW) ]
		rtv.sort(key=lambda x:x[0][0])
		rtv=random.sample(rtv,2) if len(rtv)>1 else rtv
		rtv=[x[0] for x in rtv]
		return rtv
	def _mutate_merge(self,strt="",p_contraintSelected=0.5,p_negateRatio=0.5):
		# take some constraints from 2 goalsets of 2 nodes respectively and merge as a goalset forming a new node
		# TODO
		rtv=[]
		candi=self._mutate_getCandi(strt=strt)
		if len(candi)<2: return rtv
		nodesrc1=candi[0]
		nodesrc2=candi[1]
		node=self.newNode_merge(nodesrc1,nodesrc2,p_contraintSelected,p_negateRatio)
		rtv.append(node)
		return rtv
	def _mutate_sparse(self,strt="",p_constraintReserved=0.5,p_negateRatio=0.5):
		# take partial constraints of a goalset of a final node to form a new node
		rtv=[]
		candi=self._mutate_getCandi(strt=strt)
		if len(candi)<1: return rtv
		nodesrc=candi[0]
		node=self.newNode_sparse(nodesrc,p_constraintReserved,p_negateRatio)
		rtv.append(node)
		return rtv
	def _mutate_noise(self,strt="",p_constraintReserved=0.5,p_negateRatio=0.5):
		rtv=[]
		candi=self._mutate_getCandi(strt=strt)
		if len(candi)<1: return rtv
		nodesrc=candi[0]
		node=self.newNode_noise(nodesrc,p_constraintReserved,p_negateRatio)
		rtv.append(node)
		return rtv
	def _mutate_noiseDiff(self,strt="",p_constraintReserved=0.5,p_negateRatio=0.5):
		rtv=[]
		if not strt in self.goal_nodes: return rtv
		nextIt=self.oriNodes_dict[strt]+1
		base=self.goal_nodes[ self.oriNodes[nextIt-1] ]
		more=self.goal_nodes[ self.oriNodes[nextIt] if nextIt<len(self.oriNodes) else  random.choice([k for k in self.goal_final]) ]
		node=self.newNode_noiseDiff(base,more,p_constraintReserved,p_negateRatio)
		rtv.append(node)
		return rtv
	def _mutate_partialFinal(self,strt="",p_constraintReserved=0.5,p_negateRatio=0.5):
		rtv=[]
		node=self.newNode_fromFinal(p_constraintReserved,p_negateRatio)
		rtv.append(node)
		return rtv
	def mutate(self,strts=[""],
		maxAddedNodes=20,
		p_nodeNoise=0.5,
		p_nodeNoiseDiff=0.5,
		p_nodePartialFinal=1,
		p_nodeSparse=0.5, # TODO
		#p_nodeMerge=0.5, # TODO
		p_nodeRandWeight=0.5,
		__dummy=0):
		strt=strts[0]
		if strt in self.goal_final: return self
		#TODO: constraint mutation
		#TODO structure is wrong
		self.clean_cache()
		newNodes=[]
		if random.random()<p_nodeNoise:
			newNodes+=self._mutate_noise(strt=strt,p_negateRatio=0.05)
		if random.random()<p_nodeNoiseDiff:
			newNodes+=self._mutate_noiseDiff(strt=strt,p_negateRatio=0.05)
		if random.random()<p_nodePartialFinal:
			newNodes+=self._mutate_partialFinal(strt=strt,p_negateRatio=0.05)
		if random.random()<p_nodeSparse:
			newNodes+=self._mutate_sparse(strt=strt,p_negateRatio=0.05)
		#if random.random()<p_nodeMerge:
		#	newNodes+=self._mutate_merge(strt=strt,p_negateRatio=0)
		newNodes=[ node for node in newNodes if not isNone(node) ]
		for node in newNodes: node[1][2]["precs"]=set([strt])
		# rand weight
		baseW=self.goal_nodes[strt][0] if strt in self.oriNodes_dict else nINF_v1
		#nextW=self.getNode(self.getNextNodeNames(strt))[0]
		addedSuccs=[k for k in self.goal_nodes if baseW<=self.goal_nodes[k][0] and not k in self.oriNodes_dict]
		cnt=len(addedSuccs)-maxAddedNodes
		if cnt>0:
			delSet=set(random.sample(addedSuccs,cnt))
			self.goal_nodes_names=[k for k in self.goal_nodes_names if not k in delSet]
			for k in delSet: del self.goal_nodes[k]
		self.addNodes(newNodes)
		if random.random()<p_nodeRandWeight:
			self._mutate_randWeight(strt=strt)
		return self
	def cross(self,rhs,p_wRef=0.5):
		#TODO: constraint crossover
		self.clean_cache()
		for k in self.goal_nodes_names:
			if (k in rhs.goal_nodes) and random.random()<p_wRef:
				w=self.goal_nodes[k][0]
				w.clear()
				w.extend(rhs.goal_nodes[k][0])
		return self
		pass
	def similar(self,rhs):
		lnn=[n for n in self.goal_nodes_names]
		rnn=[n for n in  rhs.goal_nodes_names]
		if len(lnn)!=len(rnn): return False
		lnn.sort(key=lambda x:self.goal_nodes[x][0])
		rnn.sort(key=lambda x: rhs.goal_nodes[x][0])
		f=lambda x:str(x)
		for i in range(len(lnn)):
			if lnn[i]==rnn[i]: continue # same name
			lns=[cs for cs in self.goal_nodes[lnn[i]][1]]
			rns=[cs for cs in  rhs.goal_nodes[rnn[i]][1]]
			lns.sort(key=f)
			rns.sort(key=f)
			if lns!=rns: return False
		return True

