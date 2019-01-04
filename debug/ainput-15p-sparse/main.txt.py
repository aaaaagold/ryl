#!/bin/python3
# 4x4

def corner(bd,width):
	rtv=True
	target=[ i for i in range(16) ]
	msk=[ 0 for _ in range(16) ]
	for y in range(4):
		for x in range(4):
			if min(x,y)<width:
				msk[y*4+x]|=1
	return (sum([ target[i]!=bd[i] for i in range(16) if msk[i]!=0 ])==0)+0
def corner1(bd): return corner(bd,1)
def corner2(bd): return corner(bd,2)
def corner3(bd): return corner(bd,3)

def near(bd,n):
	(idx,correct)=(bd.index(n),(n%4,n//4))
	(dx,dy)=(correct[0]-idx%4,correct[1]-idx//4)
	return abs(dx)+abs(dy)
def near0(bd): return near(bd,0)
def near1(bd): return near(bd,1)
def near2(bd): return near(bd,2)
def near3(bd): return near(bd,3)
def near4(bd): return near(bd,4)
def near5(bd): return near(bd,5)
def near6(bd): return near(bd,6)
def near7(bd): return near(bd,7)
def near8(bd): return near(bd,8)
def near9(bd): return near(bd,9)
def near10(bd): return near(bd,10)
def near11(bd): return near(bd,11)
def near12(bd): return near(bd,12)
def near13(bd): return near(bd,13)
def near14(bd): return near(bd,14)
def near15(bd): return near(bd,15)
