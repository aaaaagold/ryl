#!/bin/python3
# 4x4x2d

outputCnt=32

def corner(ov,width):
	self=corner
	if not hasattr(self,"last"): self.last={}
	tov=tuple(ov)
	if tov in self.last: return self.last[tov]
	else:
		del self.last
		self.last={}
	
	rtv=True
	target=[ i for i in range(16) ]
	msk=[ 0 for _ in range(16) ]
	for y in range(4):
		for x in range(4):
			if min(x,y)<width:
				msk[y*4+x]|=1
	rtv=(sum([ target[i]!=ov[i+outputCnt] for i in range(16) if msk[i]!=0 ])==0)+0
	self.last[tov]=rtv
	return rtv
def corner1(ov): return corner(ov,1)
def corner2(ov): return corner(ov,2)
def corner3(ov): return corner(ov,3)

def near(ov,n):
	#(idx,correct)=(ov.index(n),(n%4,n//4))
	(idx,correct)=((ov[n]%4,ov[n]//4),(n%4,n//4))
	(dx,dy)=(correct[0]-idx[0],correct[1]-idx[1])
	return abs(dx)+abs(dy)
def near0(ov): return near(ov,0)
def near1(ov): return near(ov,1)
def near2(ov): return near(ov,2)
def near3(ov): return near(ov,3)
def near4(ov): return near(ov,4)
def near5(ov): return near(ov,5)
def near6(ov): return near(ov,6)
def near7(ov): return near(ov,7)
def near8(ov): return near(ov,8)
def near9(ov): return near(ov,9)
def near10(ov): return near(ov,10)
def near11(ov): return near(ov,11)
def near12(ov): return near(ov,12)
def near13(ov): return near(ov,13)
def near14(ov): return near(ov,14)
def near15(ov): return near(ov,15)

