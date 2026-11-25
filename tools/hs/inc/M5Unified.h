#pragma once
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <string>
#include <vector>
#include <algorithm>
#define TFT_WHITE 0xFFFF
#define TFT_BLACK 0x0000
namespace lgfx { struct IFont { int id; }; }
namespace fonts { extern lgfx::IFont Font0, Font2, Font4, Font8, Font8x8C64, AsciiFont8x16; }
enum class textdatum_t { top_left, top_center, top_right };
uint32_t micros(); uint32_t millis(); void delay(uint32_t); uint32_t esp_random();
inline void pinMode(int, int) {} inline void digitalWrite(int, int) {}
#define OUTPUT 1
#define HIGH 1
struct TextRec { std::string s; int x, y; int font; float size; int datum; uint16_t col; };
extern std::vector<TextRec> g_texts;
namespace m5 { struct rtc_time_t { int8_t hours=0, minutes=0, seconds=0; }; struct rtc_date_t { int16_t year=2000; int8_t month=1, date=1, weekDay=0; }; }
struct Rtc_ { bool isEnabled(){return true;} m5::rtc_date_t getDate(); void setDate(const m5::rtc_date_t& d); m5::rtc_time_t getTime(); void setTime(const m5::rtc_time_t& t); };
namespace m5 { enum class board_t { board_unknown, board_M5StickCPlus2, board_M5StickC, board_M5StickCPlus }; }
struct M5Display_ { void setRotation(int) {} void setBrightness(int) {} void invertDisplay(bool) {} void fillScreen(uint16_t) {} int width() { return 240; } int height() { return 135; } };
struct Touch_ { int getCount() { return 0; } };
struct M5Canvas {
  void drawArc(int,int,int,int,float,float,uint16_t){} void setClipRect(int,int,int,int){} void clearClipRect(){}
  M5Canvas(void*) {}
  uint16_t fb[240*135]; int font=0; float size=1; int datum=0; uint16_t col=0xFFFF;
  void setColorDepth(int) {} void createSprite(int, int) {} void* getBuffer() { return fb; }
  void pushSprite(int, int);
  template<class D> void pushRotateZoom(D*, float, float, float, float, float) {}
  inline void px(int x, int y, uint16_t c) { if (x>=0 && y>=0 && x<240 && y<135) fb[y*240+x]=c; }
  void drawPixel(int x, int y, uint16_t c) { px(x,y,c); }
  void fillScreen(uint16_t c) { for (auto &p : fb) p=c; g_texts.clear(); }
  void fillRect(int x,int y,int w,int h,uint16_t c) { for (int j=0;j<h;j++) for (int i=0;i<w;i++) px(x+i,y+j,c); }
  void drawFastHLine(int x,int y,int w,uint16_t c) { fillRect(x,y,w,1,c); }
  void drawFastVLine(int x,int y,int h,uint16_t c) { fillRect(x,y,1,h,c); }
  void drawRect(int x,int y,int w,int h,uint16_t c) { drawFastHLine(x,y,w,c); drawFastHLine(x,y+h-1,w,c); drawFastVLine(x,y,h,c); drawFastVLine(x+w-1,y,h,c); }
  void drawLine(int x0,int y0,int x1,int y1,uint16_t c) { int dx=abs(x1-x0), sx=x0<x1?1:-1, dy=-abs(y1-y0), sy=y0<y1?1:-1, e=dx+dy; for(;;){ px(x0,y0,c); if(x0==x1&&y0==y1)break; int e2=2*e; if(e2>=dy){e+=dy;x0+=sx;} if(e2<=dx){e+=dx;y0+=sy;} } }
  void fillEllipse(int cx,int cy,int rx,int ry,uint16_t c) { for (int j=-ry;j<=ry;j++) for (int i=-rx;i<=rx;i++) if ((float)i*i/(rx*rx+0.01f)+(float)j*j/(ry*ry+0.01f)<=1.0f) px(cx+i,cy+j,c); }
  void drawEllipse(int cx,int cy,int rx,int ry,uint16_t c) { for (int j=-ry-1;j<=ry+1;j++) for (int i=-rx-1;i<=rx+1;i++) { float v=(float)i*i/(rx*rx+0.01f)+(float)j*j/(ry*ry+0.01f); if (v<=1.15f && v>=0.7f) px(cx+i,cy+j,c);} }
  void fillCircle(int cx,int cy,int r,uint16_t c) { for (int j=-r;j<=r;j++) for (int i=-r;i<=r;i++) if (i*i+j*j<=r*r+r*0.5f) px(cx+i,cy+j,c); }
  void drawCircle(int cx,int cy,int r,uint16_t c) { for (int j=-r;j<=r;j++) for (int i=-r;i<=r;i++) { int d=i*i+j*j; if (d<=r*r+r && d>=(r-1)*(r-1)) px(cx+i,cy+j,c);} }
  void qrcode(const char*, int x, int y, int w, int v = 1) { fillRect(x, y, w, w, 0xFFFF); for (int j = 0; j < 29; j++) for (int k = 0; k < 29; k++) if (((j * 7 + k * 13 + j * k) % 5) < 2) fillRect(x + 12 + k * 3, y + 12 + j * 3, 3, 3, 0); }
  void drawTriangle(int x0,int y0,int x1,int y1,int x2,int y2,uint16_t c) { drawLine(x0,y0,x1,y1,c); drawLine(x1,y1,x2,y2,c); drawLine(x2,y2,x0,y0,c); }
  void fillTriangle(int x0,int y0,int x1,int y1,int x2,int y2,uint16_t c) { int minx=std::min({x0,x1,x2}),maxx=std::max({x0,x1,x2}),miny=std::min({y0,y1,y2}),maxy=std::max({y0,y1,y2});
    for (int y=miny;y<=maxy;y++) for (int x=minx;x<=maxx;x++){ auto e=[&](int ax,int ay,int bx,int by){return (x-ax)*(by-ay)-(y-ay)*(bx-ax);}; int a=e(x0,y0,x1,y1),b=e(x1,y1,x2,y2),d=e(x2,y2,x0,y0); if((a>=0&&b>=0&&d>=0)||(a<=0&&b<=0&&d<=0)) px(x,y,c);} }
  void fillRoundRect(int x,int y,int w,int h,int r,uint16_t c) { for (int j=0;j<h;j++) for (int i=0;i<w;i++){ int dx=std::max(std::max(r-i,0),i-(w-1-r)), dy=std::max(std::max(r-j,0),j-(h-1-r)); if(dx*dx+dy*dy<=r*r) px(x+i,y+j,c);} }
  void drawRoundRect(int x,int y,int w,int h,int r,uint16_t c) { for (int j=0;j<h;j++) for (int i=0;i<w;i++){ int dx=std::max(std::max(r-i,0),i-(w-1-r)), dy=std::max(std::max(r-j,0),j-(h-1-r)); int d=dx*dx+dy*dy; if(d<=r*r && (d>(r-1)*(r-1) || i==0||j==0||i==w-1||j==h-1)) px(x+i,y+j,c);} }
  void setFont(const lgfx::IFont* f) { font=f->id; } void setTextSize(float s) { size=s; } void setTextDatum(textdatum_t d) { datum=(int)d; } void setTextColor(uint16_t c) { col=c; }
  void drawString(const char* s, int x, int y) { g_texts.push_back({s,x,y,font,size,datum,col}); }
};
struct Btn { bool wp=false, wr=false, held=false; bool wasPressed(){return wp;} bool wasReleased(){return wr;} bool isPressed(){return held;} bool pressedFor(uint32_t){return false;} bool wasClicked(){return false;} bool wasHold(){return false;} void setRawState(uint32_t,bool){} };
struct Spk { void tone(float,int,int=-1,bool=true) {} void stop(int=0) {} void setVolume(int) {} void setChannelVolume(int,int) {} };
struct Imu_ { bool isEnabled(){return true;} void getAccel(float* x,float* y,float* z); };
struct M5Cfg {};
namespace m5 { struct Power_Class { enum { is_discharging=0, is_charging=1, charge_unknown=2 }; }; }
struct Pwr_ { int getBatteryLevel(){return 63;} int isCharging(){return 1;} };
struct M5_ { Rtc_ Rtc; Pwr_ Power; M5Display_ Display; Touch_ Touch; m5::board_t getBoard(){return m5::board_t::board_M5StickCPlus2;} Spk Speaker; Imu_ Imu; Btn BtnA, BtnB, BtnPWR; M5Cfg config(){return {};} void begin(M5Cfg){} void update(){} };
extern M5_ M5;
