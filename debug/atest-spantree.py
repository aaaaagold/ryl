#!/bin/python3
import sys
import copy
import time

from ag import *
#from ab2g import *
from aspantree import *
from asol import *

tree=spantree()
tree.fromStr('''
6
0 1 11
1 2 22
2 3 33
3 4 44
4 5 55
''')
stat=spantreeState(tree)
print([ x[2].chosen for x in stat.near1()])
tmp=bfs(stat)
print(tmp)
print([ (tmp[i][0].totalWeight(),tmp[i][0].chosen) for i in tmp])

