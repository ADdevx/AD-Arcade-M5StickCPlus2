#pragma once
#ifndef PROGMEM
#define PROGMEM
#endif
#pragma once
#include <string>
#include <functional>
#include <map>
#include <vector>
#include <cstdio>
#include <cstdarg>
#include <cstdlib>
struct IPAddress {};
enum { WIFI_AP = 2, WIFI_OFF = 0 };
struct WiFiClass { void mode(int){} bool softAP(const char*, const char*){return true;} IPAddress softAPIP(){return {};} void softAPdisconnect(bool){} };
static WiFiClass WiFi;
struct String {
  std::string s; String(){} String(const char* c):s(c){} String(const std::string& c):s(c){}
  const char* c_str() const { return s.c_str(); } int toInt() const { return atoi(s.c_str()); }
  String& operator+=(const char* c){ s+=c; return *this; } String& operator+=(int v){ s+=std::to_string(v); return *this; }
  friend String operator+(String a, const char* b){ a.s+=b; return a; } friend String operator+(const char* a, const String& b){ return String(std::string(a)+b.s); }
};
