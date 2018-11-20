#include <cstdlib>
#include <iostream>
#include <string>
#include <vector>
#include <set>
#include <algorithm>

using namespace std;

class L
{
public:
	vector<int> x;
	L(){x.resize(4);};
	L(int a1,int a2,int a3,int a4){ x.resize(4); reset(a1,a2,a3,a4); }
	void reset(int a1,int a2,int a3,int a4)
	{
		x[0]=a1;
		x[1]=a2;
		x[2]=a3;
		x[3]=a4;
	}
	bool operator<(const L &rhs)const
	{
		return x<rhs.x;
	}
};

int main(const int argc,const char *argv[])
{
	string s;
	vector<L> lines;
	for(int x=5;x--;) getline(cin,s);
	int xm=0,xM=0,ym=0,yM=0;
	for(int x1,x2,y1,y2;cin>>x1>>x2>>y1>>y2;){
		lines.push_back(L(x1,x2,y1,y2));
		xm=min(min(x1,x2),xm);
		xM=max(max(x1,x2),xM);
		ym=min(min(y1,y2),ym);
		yM=max(max(y1,y2),yM);
	}
	sort(lines.begin(),lines.end());
	if(0!=0)
	for(const auto& line:lines){
		for(const auto& val:line.x) cout<<val<<" ";
		cout<<endl;
	}
	int xs=xM-xm,ys=yM-ym;
	vector<vector<int> > adj(yM-ym,vector<int>(xM-xm,0));
	// bitmask: blocked @ DURL
	if(0==0){
		for(int y=ys,x=xs-1;y--;){
			adj[y][x]|=2;
			adj[y][0]|=1;
		}
		for(int y=ys-1,x=xs;x--;){
			adj[0][x]|=4;
			adj[y][x]|=8;
		}
	}
	for(const auto& line:lines){
		if(line.x[0]==line.x[1] && line.x[0]!=xM && line.x[0]!=xm){
			const auto &y=min(line.x[2],line.x[3])-ym;
			const auto &x=line.x[0]-xm;
			adj[y][x-1]|=2;
			adj[y][x  ]|=1;
		}else if(line.x[2]==line.x[3] && line.x[2]!=yM && line.x[2]!=ym){
			const auto &x=min(line.x[0],line.x[1])-xm;
			const auto &y=line.x[2]-ym;
			adj[y-1][x]|=8;
			adj[y  ][x]|=4;
		}else if(!(line.x[0]==line.x[1]||line.x[2]==line.x[3])){
			cout<<"weird\n";
			exit(1);
		}
	}
	vector<vector<set<pair<int,int> > > > adjlist(adj.size(),vector<set<pair<int,int> > >(adj[0].size()));
	for(int y=ys;y--;){
		for(int x=xs;x--;){
			if((adj[y][x]&1)==0) adjlist[y][x].insert(pair<int,int>(x-1,y));
			if((adj[y][x]&2)==0) adjlist[y][x].insert(pair<int,int>(x+1,y));
			if((adj[y][x]&4)==0) adjlist[y][x].insert(pair<int,int>(x,y-1));
			if((adj[y][x]&8)==0) adjlist[y][x].insert(pair<int,int>(x,y+1));
		}
	}
	const string txtpic="--txtpic";
	if(argc>1 && txtpic==argv[1]){
	for(int y=ys;y--;){
		for(int x=0;x<xs;x++){
			const char *ptr=0;
			switch(adj[y][x])
			{
			case  0: ptr="┼"; break;
			case  1: ptr="├"; break;
			case  2: ptr="┤"; break;
			case  3: ptr="│"; break;
			case  4: ptr="┴"; break;
			case  5: ptr="└"; break;
			case  6: ptr="┘"; break;
			case  7: ptr="╧"; break;
			case  8: ptr="┬"; break;
			case  9: ptr="┌"; break;
			case 10: ptr="┐"; break;
			case 11: ptr="╤"; break;
			case 12: ptr="─"; break;
			case 13: ptr="╟"; break;
			case 14: ptr="╢"; break;
			case 15: ptr="╬"; break;
			}
			cout<<ptr;
		}
		cout<<endl;
	}
	exit(0);
	}

	cout<<xs<<" "<<ys<<endl;
	for(int y=ys;y--;){
		for(int x=xs;x--;){
			const auto &p1=y*xs+x;
			for(const auto &p:adjlist[y][x]){
				const auto &p2=p.second*xs+p.first;
				if(p1<p2) cout<<p1<<" "<<p2<<endl;
			}
		}
	}
}
