#pragma once
#include <map>
#include <string>
struct Preferences {
  std::string ns; static std::map<std::string,int>& store();
  bool begin(const char* n, bool) { ns=n; return true; } void end() {}
  int getInt(const char* k, int d) { auto &m=store(); auto it=m.find(ns+"/"+k); return it==m.end()?d:it->second; }
  void putInt(const char* k, int v) { store()[ns+"/"+k]=v; }
  bool remove(const char* k) { return store().erase(ns+"/"+k)>0; }
  long getLong(const char* k, long d) { return getInt(k,(int)d); } void putLong(const char* k, long v) { putInt(k,(int)v); }
  unsigned getUInt(const char* k, unsigned d) { return (unsigned)getInt(k,(int)d); } void putUInt(const char* k, unsigned v) { putInt(k,(int)v); }
  bool isKey(const char* k) { return store().count(ns+"/"+k)>0; }
  bool getBool(const char* k, bool d) { return getInt(k,d)!=0; } void putBool(const char* k, bool v) { putInt(k,v); }
};
