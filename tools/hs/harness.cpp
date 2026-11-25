#include <M5Unified.h>
#include <Preferences.h>
#include "/home/claude/m5arcade/src/common.h"
#include <WebServer.h>
#include <fstream>
#include <sstream>
lgfx::IFont fonts::Font0{0}, fonts::Font2{2}, fonts::Font4{4}, fonts::Font8{8};
std::vector<TextRec> g_texts; M5_ M5; M5Canvas canvas(nullptr);
std::map<std::string,int>& Preferences::store() { static std::map<std::string,int> m; return m; }
static uint32_t g_us = 1000000, g_rand = 12345; static float g_ax=0,g_ay=0,g_az=1;
uint32_t micros() { return g_us; } uint32_t millis() { return g_us/1000; } void delay(uint32_t) {}
uint32_t esp_random() { g_rand = g_rand*1664525u+1013904223u; return g_rand>>8; }
void Imu_::getAccel(float* x,float* y,float* z) { *x=g_ax; *y=g_ay; *z=g_az; }
void sfx(int,int,bool) {}
int g_theme=getenv("THEME")?atoi(getenv("THEME")):0; int themeCount(){return 7;} const char* themeName(int i){ static const char* n[7]={"Auto","Ocean","Sunset","Forest","Sakura","Gold","Mono"}; return n[i%7]; }
int g_lang=getenv("LANG1")?1:0; int g_bright=2; bool g_sound=true; bool g_music=true; int g_sleepIdx=1; bool g_quit=false; void applyBrightness(){} void saveSettings(){}
static const char* OUT;
namespace GAME { void begin(); void loop(); }
__attribute__((weak)) void test_hook(int) {}
__attribute__((weak)) void test_frame(int) {}
void set_acc(float x,float y,float z){ g_ax=x; g_ay=y; g_az=z; }
void set_tilt(float a,float b){ g_ax=a*0.45f; g_ay=b*0.45f; }
void set_seed(uint32_t s){ g_rand=s; }
void M5Canvas::pushSprite(int,int) {}
void present(int x,int y){ canvas.pushSprite(x,y); }
static void dump(const char* name) {
  std::string base = std::string(OUT)+"/"+name;
  FILE* f=fopen((base+".ppm").c_str(),"wb"); fprintf(f,"P6\n240 135\n255\n");
  for (int i=0;i<240*135;i++){ uint16_t c=canvas.fb[i]; uint8_t r=((c>>11)&31)<<3, g=((c>>5)&63)<<2, b=(c&31)<<3; fputc(r,f);fputc(g,f);fputc(b,f);} fclose(f);
  FILE* t=fopen((base+".txt").c_str(),"w"); for (auto &r:g_texts) fprintf(t,"%d\t%d\t%d\t%g\t%d\t%d\t%s\n",r.x,r.y,r.font,r.size,r.datum,r.col,r.s.c_str()); fclose(t);
}
int main(int argc, char** argv) {
  OUT=argv[2]; std::ifstream in(argv[1]); std::string line; struct Ev{int f; std::string c; float a,b; std::string s;}; std::vector<Ev> ev; int last=0;
  while (std::getline(in,line)) { std::istringstream ss(line); Ev e; if(!(ss>>e.f>>e.c)) continue; e.a=e.b=0; if(e.c=="add"){ std::getline(ss,e.s); } else ss>>e.a>>e.b; if(e.c=="shot"){ std::istringstream s2(line); std::string x,y; s2>>x>>y>>e.s; } ev.push_back(e); last=std::max(last,e.f); }
  Preferences p; p.begin("tilt",false); p.putBool("ok",true); p.putInt("ax",0); p.putInt("ay",1); p.putInt("sx",1); p.putInt("sy",1);
  GAME::begin();
  for (int f=0; f<=last+1; f++) {
    M5.BtnA.wp=M5.BtnB.wp=M5.BtnPWR.wp=false;
    for (auto &e:ev) if (e.f==f) {
      if (e.c=="A") M5.BtnA.wp=true; else if (e.c=="B") M5.BtnB.wp=true; else if (e.c=="P") M5.BtnPWR.wp=true;
      else if (e.c=="add") { size_t k=e.s.find('|'); WebStub::args()["t"]=e.s.substr(1,k-1); WebStub::args()["d"]=e.s.substr(k+1); WebStub::h()["/add"](); fprintf(stderr,"ADD -> %s\n",WebStub::last().c_str()); }
      else if (e.c=="del") { WebStub::args()["i"]=std::to_string((int)e.a); WebStub::h()["/del"](); }
      else if (e.c=="list") { WebStub::h()["/list"](); fprintf(stderr,"LIST -> %s\n",WebStub::last().c_str()); }
      else if (e.c=="hook") test_hook((int)e.a);
      else if (e.c=="tilt") { g_ax=e.a*0.45f; g_ay=e.b*0.45f; }
    }
    test_frame(f);
    g_us += 20000; g_texts.clear(); GAME::loop();
    for (auto &e:ev) if (e.f==f && e.c=="shot") dump(e.s.c_str());
  }
  return 0;
}
