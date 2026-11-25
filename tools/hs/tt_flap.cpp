#include "../../src/flap.cpp"
namespace flaptest { void begin(){ flap::begin(); } void loop(){ flap::loop(); } }
void test_hook(int k){ using namespace flap; if(k==1){ score=12; } if(k==2){ score=23; } }
