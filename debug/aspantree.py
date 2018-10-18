#!/bin/python3
import copy
import sys
import time
import random

from shorthand import *
from amyhead import *
from ag import *

class spantree:
	def __init__(self):
		self.edges=[]
		self.edges_r=[]
		self.weights=[]
		self.nodes=0
	def fromTxt(self,fname):
		tmp=""
		with open(fname) as f:
			tmp+=f.read()
		return self.fromStr(tmp)
	def copy(self):
		rtv=spantree()
		rtv.edges=copy.deepcopy(self.edges)
		rtv.weights=copy.deepcopy(self.weights)
		rtv.nodes=self.nodes
		return rtv
	def fromStr(self,s):
		# TODO
		'''
			An integer N in first line, the graph has N vertices, 0 to N-1
			following lines indicate edges, 3 vars for a line:
				node1(int) node2(int) weight(int)
			undirected simplegraph
			the parse will NOT check if the node number in [ 0 , N-1 ]
		'''
		lines=s.replace("\r","").split("\n")
		self.nodes=int(lines[0])
		parser=re.compile("[ \t]+")
		tmp=[]
		for i in range(1,len(lines)):
			line=lines[i]
			tokens=[ int(x) for x in parser.split(line) ]
			tmp.append(tokens)
		tmp.sort()
		for x in tmp:
			e = (x[0],x[1]) if x[0]<x[1] else (x[1],x[0])
			self.edges.append(e)
			self.edges_r.append(e[::-1])
			self.weights.append(x[2])
		self.edges_r.sort()
	def getWeight(self,n1,n2):
		edge = (n1,n2) if n1<n2 else (n2,n1)
		rtv=bs(self.edges,edge)
		return None if self.edges[rtv]!=edge else self.weights[rtv]
	def nodesize(self):
		return self.nodes

class spantreeState:
	def __init__(self,referTree,chosenEdges=None,visitNodes=None):
		# chosenEdges is a list of int, x-th edge in referTree.edges
		self.referTree=referTree
		if isNone(chosenEdges): self.chosen=set()
		else: self.chosen=copy.deepcopy(set(chosenEdges))
		if isNone(visitNodes):
			tmp=[ 0 for _ in range(self.referTree.nodesize()) ]
			for x in self.chosen:
				e1,e2 = self.referTree.edges[x]
				tmp[e1]=1
				tmp[e2]=1
			self._nodes=tmp
		else: self._nodes=copy.deepcopy(visitNodes)
	def copy(self):
		rtv=spantreeState(self.referTree,self.chosen)
		return rtv
	def _test_near1(self):
		# return all 1-more-edge states
		rtv=[]
		for i in len(self.referTree.edges):
			if i in self.chosen: continue
			tmp=spantreeState(self.referTree,self.chosen,self._nodes)
			tmp.chosen.add(i)
			for n in self.referTree.edges[i]: tmp._nodes[n]=1
			rtv.append(tmp)
		return rtv
	def near1(self):
		rtv=[]
		if len(self.chosen)==0:
			for i in len(self.referTree.edges):
				tmp=spantreeState(self.referTree,self.chosen,self._nodes)
				tmp.chosen.add(i)
				for n in self.referTree.edges[i]: tmp._nodes[n]=1
				rtv.append(tmp)
		else:
			newedges=set()
			preparebs=[ 0 for _ in range(self.referTree.nodesize()) ]
			preparebs_r=[ 0 for _ in range(self.referTree.nodesize()) ]
			for n in self._nodes:
				preparebs[n]=1
				preparebs[n+1]=1
				preparebs_r[n]=1
				preparebs_r[n+1]=1
			for i in range(len(preparebs)):
				if preparebs[i]!=0:
					preparebs[i]=bs(self.referTree.edges,(i,))
				if preparebs_r[i]!=0:
					preparebs_r[i]=bs(self.referTree.edges_r,(i,))
			for n in self._nodes:
				for i in range(preparebs[n],preparebs[n+1]):
					if not self.referTree.edges[i] in self.chosen:
						newedges.add(self.referTree.edges[i])
				for i in range(preparebs_r[n],preparebs_r[n+1]):
					tmp=self.referTree.edges_r[i][::-1]
					if not tmp in self.chosen:
						newedges.add(tmp)
			newedgesIndex = [ bs(self.referTree.edges,x) for x in newedges ]
			for i in newedgesIndex:
				tmp=spantreeState(self.referTree,self.chosen,self._nodes)
				tmp.chosen.add(i)
				for n in self.referTree.edges[i]: tmp._nodes[n]=1
				rtv.append(tmp)
		return rtv
	

