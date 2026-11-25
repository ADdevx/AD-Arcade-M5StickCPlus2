#include <M5Unified.h>
#include <Preferences.h>
#include "../../src/main.cpp"
lgfx::IFont fonts::Font0{0}, fonts::Font2{2}, fonts::Font4{4}, fonts::Font8{8};
std::vector<TextRec> g_texts; M5_ M5;
std::map<std::string,int>& Preferences::store() { static std::map<std::string,int> m; return m; }
static uint32_t g_us = 1000000, g_rand = 12345;
uint32_t micros() { return g_us; } uint32_t millis() { return g_us/1000; } void delay(uint32_t ms) { g_us += ms*1000; }
uint32_t esp_random() { g_rand = g_rand*1664525u+1013904223u; return g_rand>>8; }
void Imu_::getAccel(float* x,float* y,float* z) { *x=0; *y=0; *z=1; }
static const char* OUT; static int g_shot=0; static std::vector<int> shots;
void M5Canvas::pushSprite(int,int) {
  static int n=0; n++;
  for (int s: shots) if (s==n) { char b[200]; snprintf(b,200,"%s/f%04d",OUT,n);
    FILE* f=fopen((std::string(b)+".ppm").c_str(),"wb"); fprintf(f,"P6\n240 135\n255\n");
    for (int i=0;i<240*135;i++){ uint16_t c=fb[i]; fputc(((c>>11)&31)<<3,f);fputc(((c>>5)&63)<<2,f);fputc((c&31)<<3,f);} fclose(f);
    FILE* t=fopen((std::string(b)+".txt").c_str(),"w"); for (auto &r:g_texts) fprintf(t,"%d\t%d\t%d\t%g\t%d\t%d\t%s\n",r.x,r.y,r.font,r.size,r.datum,r.col,r.s.c_str()); fclose(t); }
  g_texts.clear();
  if (n>3000) exit(0);
}
int main(int argc,char**argv){ OUT=argv[1]; for(int i=2;i<argc;i++) shots.push_back(atoi(argv[i])); { Preferences p; p.begin("tilt",false); p.putBool("ok",true); p.putInt("ax",0); p.putInt("ay",1); p.putInt("sx",1); p.putInt("sy",1); } { Preferences q; q.begin("arcade",false); if(getenv("THEME")) q.putInt("theme",atoi(getenv("THEME"))); if(getenv("SEL")) q.putInt("sel",atoi(getenv("SEL"))); } setup(); for(;;){ loop(); g_us+=16000; } }
