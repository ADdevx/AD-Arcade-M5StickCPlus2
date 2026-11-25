#pragma once
#include "WiFi.h"
enum { HTTP_GET = 1, HTTP_POST = 3 };
struct WebStub { static std::map<std::string, std::function<void()>>& h() { static std::map<std::string, std::function<void()>> m; return m; }
  static std::map<std::string, std::string>& args() { static std::map<std::string, std::string> m; return m; }
  static std::string& last() { static std::string s; return s; } };
struct WebServer {
  WebServer(int){} void on(const char* p, int, std::function<void()> f){ WebStub::h()[p]=f; } void onNotFound(std::function<void()>){}
  void begin(){} void stop(){} void handleClient(){}
  String arg(const char* k){ return String(WebStub::args()[k]); }
  void send(int, const char*, const String& b){ WebStub::last()=b.s; } void send_P(int, const char*, const char*){}
  void sendHeader(const char*, const char*, bool){}
};
