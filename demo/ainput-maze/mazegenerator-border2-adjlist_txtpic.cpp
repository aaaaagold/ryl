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
	// outputting
	const string txtpic="--txtpic";
	bool bool_txtpic=false; for(int x=argc;x--;)if(txtpic==argv[x]){bool_txtpic=true;break;}
	if(bool_txtpic){
		const string box="--box";
		bool bool_box=false; for(int x=argc;x--;)if(box==argv[x]){bool_box=true;break;}
		const string bold="--bold";
		bool bool_bold=false; for(int x=argc;x--;)if(bold==argv[x]){bool_bold=true;break;}
		if(bool_box){
			std::vector<std::vector<const char *> > wall(adj.size()+1);
			wall[0].push_back("└");
			wall.back().push_back("┌");
			for(unsigned y=adj.size();--y;){
				wall[y].push_back( (adj[y][0]&4)==0?"│":"├" );
			}
			for(unsigned x=1,xs=adj.back().size();x<xs;++x){
				wall.back().push_back( (adj.back()[x]&1)==0?"─":"┬" );
			}
			wall.back().push_back("┐");
			for(unsigned x=1,xs=adj[0].size();x<xs;++x){
				wall[0].push_back( (adj[0][x]&1)==0?"─":"┴" );
			}
			wall[0].push_back("┘");
			const char *const wall_kinds[]={
				"┼","├","┴","└",
				"┤","│","┘"," ",
				"┬","┌","─"," ",
				"┐"," "," "," ",
			""};
			for(unsigned y=adj.size();--y;){
				for(unsigned x=1,xs=adj[y].size();x<xs;++x){
					unsigned ch=0;
					int curr=adj[y][x],diag=adj[y-1][x-1];
					ch<<=1; ch|=(curr&1)==0; // -x
					ch<<=1; ch|=(curr&4)==0; // -y
					ch<<=1; ch|=(diag&2)==0; // +x
					ch<<=1; ch|=(diag&8)==0; // +y
					wall[y].push_back(wall_kinds[ch]);
				}
			}
			for(unsigned y=adj.size();--y;){
				wall[y].push_back( (adj[y].back()&4)==0?"│":"┤" );
			}
			for(unsigned y=wall.size();y--;){
				for(unsigned x=0,xs=wall[y].size();x<xs;++x)
					cout << wall[y][x] ;
				cout<<endl;
			}
		}else{
			// drawing line
			const char *const line_bold[]={
				"╬","╠","╣","║",
				"╩","╚","╝","╨",
				"╦","╔","╗","╥",
				"═","╞","╡","█",
			""};
			const char *const line[]={
				"┼","├","┤","│",
				"┴","└","┘","╧",
				"┬","┌","┐","╤",
				"─","╟","╢","╬",
			""};
			const char * const *const lines[]={line,line_bold};
			for(int y=ys;y--;){
				for(int x=0;x<xs;x++) cout<<lines[bool_bold][ adj[y][x] ];
				cout<<endl;
			}
		}
		exit(0);
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
