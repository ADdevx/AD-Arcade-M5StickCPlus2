#include "../../src/tilt.cpp"
#include <cstdio>
void set_acc(float,float,float);
namespace tilttest { void begin(){} void loop(){} }
void test_frame(int f){
  if(f==0){
    Preferences p; p.begin("tilt",false); p.putBool("ok",true); p.putInt("ax",0); p.putInt("ay",1); p.putInt("sx",-1); p.putInt("sy",-1); p.putInt("sz",1);
    tilt::load();
    set_acc(0,0,1); tilt::zero(); printf("start flat: posture=%d\n",tilt::posture());
    set_acc(0,0,1); printf("adapt same pose: %d\n",(int)tilt::adapt());
    set_acc(0,1,0); bool r=tilt::adapt(); printf("switch to upright: adapted=%d posture=%d\n",(int)r,tilt::posture());
    for(int i=0;i<10;i++) tilt::update();
    printf("upright rest: x=%.2f y=%.2f\n",tilt::x(),tilt::y());
    set_acc(-0.3f,0.95f,0); for(int i=0;i<20;i++) tilt::update(); printf("upright roll cw(right side down): x=%.2f (want +)\n",tilt::x());
    set_acc(0,0.95f,0.3f); for(int i=0;i<20;i++) tilt::update(); printf("upright top pushed away: y=%.2f (want +)\n",tilt::y());
    set_acc(0,0.95f,-0.3f); for(int i=0;i<20;i++) tilt::update(); printf("upright top toward me: y=%.2f (want -)\n",tilt::y());
    set_acc(0,0,1); tilt::adapt(); printf("back to flat: posture=%d\n",tilt::posture());
    set_acc(0,-0.3f,1); for(int i=0;i<20;i++) tilt::update(); printf("flat top down: y=%.2f (want +)\n",tilt::y());
    set_acc(-0.3f,0,1); for(int i=0;i<20;i++) tilt::update(); printf("flat right side down: x=%.2f (want +)\n",tilt::x());
  }
}
