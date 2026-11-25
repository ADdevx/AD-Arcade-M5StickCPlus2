#pragma once
#include "WiFi.h"
#include <fstream>
#include <sstream>
#include <sys/stat.h>
#include <unistd.h>
struct File {
  std::fstream f; bool ok=false; operator bool() const { return ok; }
  String readStringUntil(char d){ std::string s; std::getline(f,s,d); return String(s); }
  size_t readBytes(char* b, size_t n){ f.read(b,n); return f.gcount(); }
  int printf(const char* fmt, ...){ char buf[8192]; va_list a; va_start(a,fmt); int n=vsnprintf(buf,sizeof buf,fmt,a); va_end(a); f.write(buf,n); return n; }
  void close(){ f.close(); }
};
struct LittleFSClass {
  std::string path(const char* p){ return std::string("/tmp/lfs_test")+p; }
  bool begin(bool, const char*, int, const char*){ mkdir("/tmp/lfs_test",0777); return true; }
  bool exists(const char* p){ return access(path(p).c_str(),F_OK)==0; }
  File open(const char* p, const char* m){ File x; x.f.open(path(p), m[0]=='r'? std::ios::in : std::ios::out|std::ios::trunc); x.ok=x.f.is_open(); return x; }
  bool remove(const char* p){ return ::remove(path(p).c_str())==0; }
};
static LittleFSClass LittleFS;
