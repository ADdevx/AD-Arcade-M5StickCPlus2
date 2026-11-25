#include "../../src/snake.cpp"
namespace snaketest { void begin(){ snake::begin(); } void loop(){ snake::loop(); } }
void test_hook(int k){ using namespace snake; 
 if(k==1){ level=3; addRock(); addRock(); addRock(); addRock(); gx=10; gy=3; gT=200; }
 if(k==2){ bulge=0; }
 if(k==3){ n=24; int i=0; for(int x=12;x>=0;x--){sx[i]=x;sy[i]=6;i++;} for(int y=5;y>=0&&i<n;y--){sx[i]=0;sy[i]=y;i++;} for(int j=0;j<n;j++){px_[j]=sx[j];py_[j]=sy[j];} dir=0; ax=14; ay=6; bulge=99; tickAcc=0;}
}
