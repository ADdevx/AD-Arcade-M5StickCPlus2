#include "../../src/tetris.cpp"
namespace tetristest {
void begin(){ tetris::begin(); }
void loop(){ tetris::loop(); }
void fill(){ using namespace tetris; for(int y=16;y<20;y++) for(int x=0;x<9;x++) grid[y][x]=1+((x+y)%7); cur.t=0; cur.r=1; cur.x=7; cur.y=8; }
}
void test_hook(int n){ if(n==1) tetristest::fill(); }
