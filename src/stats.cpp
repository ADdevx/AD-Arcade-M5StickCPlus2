// ============================================================================
//  STATS - temps de jeu total, parties lancees, jeu prefere, medailles, serie du defi du jour
//  Le temps est compte par main.cpp (stats::tick) tant qu'un jeu est a l'ecran.
//  A/B = page suivante ; HAUT (PWR) = page precedente ; PWR long = menu
// ============================================================================
#include "common.h"
#include <Preferences.h>

namespace stats {

static const int N = trophy::T_COUNT;
static uint32_t secs[N], plays[N], msAcc[N];
static bool loaded = false, dirty = false;
static uint32_t lastTick = 0, lastFlush = 0;

static void load() {
  if (loaded) return;
  loaded = true;
  Preferences p; if (!p.begin("stats", true)) return;
  char k[8];
  for (int i = 0; i < N; i++) { snprintf(k, sizeof k, "p%d", i); plays[i] = p.getUInt(k, 0); snprintf(k, sizeof k, "t%d", i); secs[i] = p.getUInt(k, 0); }
  p.end();
}
void flush() {
  if (!loaded || !dirty) return;
  Preferences p; if (!p.begin("stats", false)) return;
  char k[8];
  for (int i = 0; i < N; i++) { snprintf(k, sizeof k, "p%d", i); p.putUInt(k, plays[i]); snprintf(k, sizeof k, "t%d", i); p.putUInt(k, secs[i]); }
  p.end(); dirty = false; lastFlush = millis();
}
void play(int idx) { load(); if (idx < 0 || idx >= N) return; plays[idx]++; dirty = true; }
void tick(int idx) {
  uint32_t now = millis(), dt = now - lastTick; lastTick = now;
  if (idx < 0 || idx >= N || dt > 300) return;       // un grand ecart = on vient d'entrer dans le jeu
  load();
  msAcc[idx] += dt;
  while (msAcc[idx] >= 1000) { msAcc[idx] -= 1000; secs[idx]++; dirty = true; }
  if (dirty && now - lastFlush > 60000) flush();
}
int total() { load(); uint32_t t = 0; for (int i = 0; i < N; i++) t += secs[i]; return (int)t; }

static void fmtTime(char* b, size_t n, uint32_t s) {
  if (s >= 3600) snprintf(b, n, "%luh%02lum", (unsigned long)(s / 3600), (unsigned long)((s / 60) % 60));
  else if (s >= 60) snprintf(b, n, "%lum%02lus", (unsigned long)(s / 60), (unsigned long)(s % 60));
  else snprintf(b, n, "%lus", (unsigned long)s);
}

// ----------------------------------------------------------------------------- ecran
static int page = 0;
static const int PER = 5, PGS = (N + PER - 1) / PER + 1;      // page 0 = resume, puis les jeux

void begin() { load(); flush(); page = 0; }

static void renderSummary() {
  char b[40]; uint32_t tot = (uint32_t)total(), np = 0; int fav = -1; uint32_t fs = 0;
  for (int i = 0; i < N; i++) { np += plays[i]; if (secs[i] > fs) { fs = secs[i]; fav = i; } }
  canvas.fillRoundRect(4, 18, SCR_W - 8, 38, 6, rgb(22, 26, 54));
  txt(L("TOTAL PLAY TIME", "TEMPS DE JEU TOTAL"), SCR_W / 2, 21, &fonts::Font0, rgb(140, 150, 205), textdatum_t::top_center);
  fmtTime(b, sizeof b, tot); txt(b, SCR_W / 2, 31, &fonts::Font4, rgb(255, 214, 90), textdatum_t::top_center);
  int y = 60;
  snprintf(b, sizeof b, "%lu", (unsigned long)np);
  canvas.fillRoundRect(4, y, 114, 36, 6, rgb(22, 26, 54));
  txt(L("GAMES PLAYED", "PARTIES LANCEES"), 61, y + 3, &fonts::Font0, rgb(140, 150, 205), textdatum_t::top_center); txt(b, 61, y + 13, &fonts::Font2, TFT_WHITE, textdatum_t::top_center);
  canvas.fillRoundRect(122, y, 114, 36, 6, rgb(22, 26, 54));
  txt(L("FAVOURITE", "JEU PREFERE"), 179, y + 3, &fonts::Font0, rgb(140, 150, 205), textdatum_t::top_center);
  txt(fav >= 0 && fs > 0 ? gameName(fav) : "-", 179, y + 13, &fonts::Font2, TFT_WHITE, textdatum_t::top_center);
  y = 97;
  int streak = 0, bestStreak = 0; { Preferences p; if (p.begin("daily", true)) { streak = p.getInt("streak", 0); bestStreak = p.getInt("bestst", 0); p.end(); } }
  canvas.fillRoundRect(4, y, 114, 25, 6, rgb(22, 26, 54));
  txt(L("MEDALS", "MEDAILLES"), 61, y + 2, &fonts::Font0, rgb(140, 150, 205), textdatum_t::top_center);
  snprintf(b, sizeof b, "%d / %d", trophy::total(), trophy::T_COUNT * 6); txt(b, 61, y + 11, &fonts::Font2, rgb(255, 205, 60), textdatum_t::top_center);
  canvas.fillRoundRect(122, y, 114, 25, 6, rgb(22, 26, 54));
  txt(L("DAILY STREAK", "SERIE DU DEFI"), 179, y + 2, &fonts::Font0, rgb(140, 150, 205), textdatum_t::top_center);
  snprintf(b, sizeof b, L("%d  (best %d)", "%d  (record %d)"), streak, bestStreak); txt(b, 179, y + 11, &fonts::Font2, rgb(255, 150, 80), textdatum_t::top_center);
}

static void renderList(int pg) {
  uint32_t mx = 1; for (int i = 0; i < N; i++) if (secs[i] > mx) mx = secs[i];
  char b[24];
  for (int k = 0; k < PER; k++) {
    int id = pg * PER + k; if (id >= N) break;
    int y = 17 + k * 21;
    canvas.fillRoundRect(4, y, SCR_W - 8, 19, 5, rgb(22, 26, 54));
    txt(gameName(id), 10, y + 1, &fonts::Font2, TFT_WHITE, textdatum_t::top_left);
    int bw = (int)(60 * secs[id] / mx);
    canvas.fillRect(104, y + 7, 60, 5, rgb(34, 40, 78)); if (bw > 0) canvas.fillRect(104, y + 7, bw, 5, rgb(255, 190, 70));
    fmtTime(b, sizeof b, secs[id]); txt(b, SCR_W - 38, y + 1, &fonts::Font0, rgb(150, 200, 255), textdatum_t::top_right);
    snprintf(b, sizeof b, "x%lu", (unsigned long)plays[id]); txt(b, SCR_W - 8, y + 1, &fonts::Font0, rgb(160, 168, 205), textdatum_t::top_right);
  }
}

static void render() {
  canvas.fillScreen(rgb(14, 16, 34));
  canvas.fillRect(0, 0, SCR_W, 15, rgb(26, 30, 62));
  txt("STATS", SCR_W / 2, -1, &fonts::Font2, rgb(255, 210, 80), textdatum_t::top_center);
  char b[12]; snprintf(b, sizeof b, "%d/%d", page + 1, PGS); txt(b, SCR_W - 5, 4, &fonts::Font0, rgb(150, 160, 210), textdatum_t::top_right);
  if (page == 0) renderSummary(); else renderList(page - 1);
  txt(L("A/B: next page   hold PWR: menu", "A/B : page suivante   PWR long : menu"), SCR_W / 2, SCR_H - 8, &fonts::Font0, rgb(110, 118, 165), textdatum_t::top_center);
}

void loop() {
  if (M5.BtnA.wasPressed() || M5.BtnB.wasPressed()) { page = (page + 1) % PGS; sfx(1200, 15); }
  else if (M5.BtnPWR.wasPressed()) { page = (page + PGS - 1) % PGS; sfx(1000, 15); }
  render();
  present(0, 0);
  delay(10);
}

void icon(int x, int y) {
  canvas.fillRoundRect(x, y, 64, 64, 6, rgb(30, 44, 80));
  uint16_t cols[4] = {rgb(90, 200, 255), rgb(120, 230, 140), rgb(255, 200, 70), rgb(255, 120, 110)};
  static const int H[4] = {18, 30, 22, 40};
  for (int i = 0; i < 4; i++) { int h = H[i]; canvas.fillRoundRect(x + 9 + i * 13, y + 54 - h, 10, h, 2, cols[i]); canvas.fillRect(x + 9 + i * 13, y + 54 - h, 3, h, mixc(cols[i], TFT_WHITE, 90)); }
  canvas.fillRect(x + 6, y + 54, 52, 2, rgb(150, 170, 220));
}

}  // namespace stats
