// Banc de test du firmware COMPLET (main.cpp + tous les jeux) avec boutons scriptes.
// script : "<frame> A|B|P" appui d'une image ; "<frame> hold A|B|P <n>" maintenu n images ; "<frame> shot nom" ; "<frame> pref ns key val" ; "<frame> rtc y m d"
#include <M5Unified.h>
#include <Preferences.h>
#include <fstream>
#include <sstream>
#include "../../src/main.cpp"
lgfx::IFont fonts::Font0{0}, fonts::Font2{2}, fonts::Font4{4}, fonts::Font8{8}, fonts::Font8x8C64{9}, fonts::AsciiFont8x16{10};
std::vector<TextRec> g_texts; M5_ M5;
std::map<std::string,int>& Preferences::store() { static std::map<std::string,int> m; return m; }
static uint32_t g_us = 1000000, g_rand = 12345;
uint32_t micros() { return g_us; } uint32_t millis() { return g_us/1000; } void delay(uint32_t ms) { }
uint32_t esp_random() { g_rand = g_rand*1664525u+1013904223u; return g_rand>>8; }
static float g_ax=0,g_ay=0,g_az=1;
void Imu_::getAccel(float* x,float* y,float* z) { *x=g_ax; *y=g_ay; *z=g_az; }
static m5::rtc_date_t g_rtc;
static m5::rtc_time_t g_rtt{10,30,0}; m5::rtc_time_t Rtc_::getTime(){return g_rtt;} void Rtc_::setTime(const m5::rtc_time_t& t){g_rtt=t; fprintf(stderr,"RTC time %d:%02d\n",t.hours,t.minutes);}
m5::rtc_date_t Rtc_::getDate() { return g_rtc; } void Rtc_::setDate(const m5::rtc_date_t& d) { g_rtc = d; fprintf(stderr, "RTC set %d-%d-%d\n", d.year, d.month, d.date); }
static const char* OUT;
void M5Canvas::pushSprite(int,int) {}
static void dump(const char* name) {
  std::string base = std::string(OUT)+"/"+name;
  FILE* f=fopen((base+".ppm").c_str(),"wb"); fprintf(f,"P6\n240 135\n255\n");
  for (int i=0;i<240*135;i++){ uint16_t c=canvas.fb[i]; fputc(((c>>11)&31)<<3,f);fputc(((c>>5)&63)<<2,f);fputc((c&31)<<3,f);} fclose(f);
  FILE* t=fopen((base+".txt").c_str(),"w"); for (auto &r:g_texts) fprintf(t,"%d\t%d\t%d\t%g\t%d\t%d\t%s\n",r.x,r.y,r.font,r.size,r.datum,r.col,r.s.c_str()); fclose(t);
}
struct Ev { int f; std::string c, a, b, d; };
int main(int argc,char**argv){
  OUT=argv[2]; std::ifstream in(argv[1]); std::string line; std::vector<Ev> ev; int last=0;
  while (std::getline(in,line)) { std::istringstream ss(line); Ev e; if(!(ss>>e.f>>e.c)) continue; ss>>e.a>>e.b>>e.d; ev.push_back(e); last=std::max(last,e.f+ (e.c=="hold"?atoi(e.d.c_str()):0)); }
  g_rtc.year=2026; g_rtc.month=11; g_rtc.date=20;
  if (getenv("RTCY")) { g_rtc.year=atoi(getenv("RTCY")); g_rtc.month=atoi(getenv("RTCM")); g_rtc.date=atoi(getenv("RTCD")); }
  if (!getenv("FIRST")) { Preferences p; p.begin("tilt",false); p.putBool("ok",true); p.putInt("ax",0); p.putInt("ay",1); p.putInt("sx",1); p.putInt("sy",1); }
  { Preferences q; q.begin("arcade",false); if(getenv("THEME")) q.putInt("theme",atoi(getenv("THEME"))); if(getenv("LANG1")) q.putInt("lang",1); if(getenv("DIFF")) q.putInt("diff",atoi(getenv("DIFF"))); if(getenv("SKIN")) q.putInt("skin",atoi(getenv("SKIN"))); if(getenv("SEL")) q.putInt("sel",atoi(getenv("SEL"))); q.putInt("slp",4); }
  setup(); if (getenv("SKINF")) g_skin = atoi(getenv("SKINF"));
  for (int f=0; f<=last+1; f++) {
    M5.BtnA.wp=M5.BtnB.wp=M5.BtnPWR.wp=false;
    for (auto &e:ev) if (e.f==f) {
      if (e.c=="A") M5.BtnA.wp=true; else if (e.c=="B") M5.BtnB.wp=true; else if (e.c=="P") M5.BtnPWR.wp=true;
      else if (e.c=="pref") { Preferences p; p.begin(e.a.c_str(),false); p.putInt(e.b.c_str(), atoi(e.d.c_str())); }
      else if (e.c=="over") session::onOver(atoi(e.a.c_str()), atoi(e.b.c_str()));
      else if (e.c=="rtc") { g_rtc.year=atoi(e.a.c_str()); g_rtc.month=atoi(e.b.c_str()); g_rtc.date=atoi(e.d.c_str()); }
      else if (e.c=="tilt") { g_ax=atof(e.a.c_str())*0.45f; g_ay=atof(e.b.c_str())*0.45f; }
    }
    // maintien
    M5.BtnA.held=M5.BtnB.held=M5.BtnPWR.held=false;
    for (auto &e:ev) if (e.c=="hold" && f>=e.f && f<e.f+atoi(e.d.c_str())) { if (e.a=="A") { M5.BtnA.held=true; if (f==e.f) M5.BtnA.wp=true; } if (e.a=="B") { M5.BtnB.held=true; if (f==e.f) M5.BtnB.wp=true; } }
    g_us += 20000; g_texts.clear(); loop();
    for (auto &e:ev) if (e.f==f && e.c=="shot") dump(e.a.c_str());
    for (auto &e:ev) if (e.f==f && e.c=="ui") {   // apercu direct d'un element du kit UI : ui <genre> <nom>
      g_texts.clear();
      if (e.a=="go") ui::gameOver("GAME OVER", 1234, 1500, false); else if (e.a=="rec") ui::gameOver("GAME OVER", 2048, 2048, true);
      else if (e.a=="pause") ui::pause(); else if (e.a=="notice") ui::notice("LEVEL CLEAR!", "+250", "A : next level", P_S);
      dump(e.b.c_str()); }
  }
  return 0;
}
