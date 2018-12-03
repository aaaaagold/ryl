#!/bin/python3

w,h=15,15

print("%d %d"%(w,h))
for y in range(h):
	for x in range(w):
		n=y*w+x
		if y+1!=h: print("%d %d"%(n,n+w))
		if x+1!=w: print("%d %d"%(n,n+1))
