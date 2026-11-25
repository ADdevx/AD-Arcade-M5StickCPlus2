#include "inc/Preferences.h"
struct Seed { Seed() { Preferences p;
  p.begin("flap", false); p.putInt("best", 25);
  p.begin("tetris", false); p.putInt("best", 9200);
  p.begin("snake", false); p.putInt("best", 180);
  p.begin("chromedino", false); p.putInt("hi", 820);
  p.begin("lander", false); p.putInt("best", 700);
  p.begin("race", false); p.putInt("best", 100);
  p.begin("maze", false); p.putInt("lvl", 13);
  p.begin("stack", false); p.putInt("best", 30);
} } seed_;
