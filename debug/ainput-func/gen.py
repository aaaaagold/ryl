#!/bin/python3

def gen(width,strt):
	for i in range(1,strt): print("B"+str(i)+" B"+str(i-1)+"\n0 0:-1"+str(i*11)+",1111\n\n")

gen(0,9)
