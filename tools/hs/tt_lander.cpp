#include "../../src/lander.cpp"
namespace landertest { void begin(){ lander::begin(); } void loop(){ lander::loop(); } }
void test_hook(int k){ using namespace lander; if(k==1){ x=padC[1]; y=60; vx=0.1f; vy=0.6f; camx=x; } if(k==2){ x=padC[1]; y=100; vx=0; vy=2.0f; } if(k==3){ x=padC[1]; y=gh(x)-14; vx=0.1f; vy=0.5f; ang=0; camx=x; } }
