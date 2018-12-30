#!/bin/python3
import copy
import sys
import time
import random
import re

from shorthand import *
from amyhead import *


class func:
	# y = f(t,x)
	# given range of y, find x so that f(t,x) in that range
	# t is given and may be edited, so there's chances to re-find x.
	####  form of f:  ####
	# THIS class is suppose to be: p1(t) crossproduct p2(x), where p1 and p2 are polynomial
	def __init__(self,coef_X=[],coef_T=[]):
		# exponent starts from 0
		self.coefs={"x":copy.deepcopy(coef_X),"t":copy.deepcopy(coef_T)}
	def cal(self,T,X):
		rtv=0
		expX=1
		for x in self.coefs["x"]:
			expT=1
			expXx=expX*x
			for t in self.coefs["t"]:
				rtv+=expXx*expT*t
				expT*=T
			expX*=X
		return rtv	

