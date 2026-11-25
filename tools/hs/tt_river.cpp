#include "../../src/river.cpp"
#include <cstdio>
void set_tilt(float,float); void set_seed(uint32_t);
static int minLives=3, hits=0, f0=0; static int rowsChecked=0, violations=0;
namespace rivertest { void begin(){ river::begin(); } void loop(){ river::loop(); } }
void test_hook(int k){ if(k==9) set_seed(getenv("SEED")?atoi(getenv("SEED")):1); }
void test_frame(int f){
  using namespace river;
  if (f==2) { state=PLAY; reset(); }              // lance une partie
  if (state!=PLAY) return;
  // bot : suit le centre du couloir de la rangee la plus proche en avant du kayak
  float tgt=bx; float bestY=-1e9;
  for(int i=0;i<nRows;i++) if(rows[i].y<=BY+14 && rows[i].y>bestY){ bestY=rows[i].y; tgt=rows[i].cx; }
  float t=clampf((tgt-bx)*0.12f-bv*0.35f,-1,1); set_tilt(getenv("NOBOT")?0:t,0);
  // invariant : aucun obstacle ne chevauche le couloir de sa rangee quand il vient de naitre
  for(auto&o:objs) if(o.on && o.y>=SPAWN_Y && o.y<SPAWN_Y+1.5f*spd+0.1f && o.type!=2){
    for(int i=0;i<nRows;i++) if(fabsf(rows[i].y-o.y)<spd*2+1){ float cx=rows[i].cx; rowsChecked++;
      float dist = o.type==0 ? fabsf(o.x-cx)-o.a : fabsf(o.x-cx)-o.a*fabsf(cosf(o.b));
      if(dist < HW+3.0f){ violations++; }
      break; }
  }
  if(lives<minLives){ minLives=lives; hits++; }
  if(f%5000==0 && f) fprintf(stderr,"f=%d score=%lu lives=%d spd=%.2f\n",f,(unsigned long)score,lives,spd);
}
struct Fin{ ~Fin(){ fprintf(stderr,"RESULT lives_min=%d hits=%d checked=%d violations=%d\n",minLives,hits,rowsChecked,violations);} } fin_;
