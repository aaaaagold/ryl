#!/bin/python3

def gen(width,strt):
	for i in range(strt,0,-1): print("B"+str(i)+" B"+str(i+1)+"\n0 0:110"+str(i*1)+",1111\n\n")

gen(0,9)
