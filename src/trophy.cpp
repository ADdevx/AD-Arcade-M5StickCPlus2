// ============================================================================
//  TROPHEES - medailles bronze / argent / or pour chaque jeu
//  - trophy::record() est appele en fin de partie : si une nouvelle medaille est gagnee, un bandeau s'affiche
//  - ecran "TROPHEES" dans le menu : meilleur score + medailles de chaque jeu
//  Seuils : modifier le tableau DEFS (bronze, argent, or) pour regler la difficulte.
// ============================================================================
#include "common.h"

namespace trophy {

struct Def { const char* en; const char* fr; const char* ns; const char* key; int b, s, g; };
static const Def DEFS[T_COUNT] = {
  {"Chrome Dino",  "Chrome Dino",   "chromedino", "hi",   300,  700, 1500},
  {"Flap Bird",    "Flap Bird",     "flap",       "best",  10,   20,   30},
  {"Meteors",      "Meteores",      "space",      "best", 100,  300,  600},   // score / 10 (secondes de survie x 5)
  {"Maze",         "Labyrinthe",    "maze",       "lvl",    4,    8,   12},   // niveau atteint
  {"Breakout",     "Casse-briques", "breakout",   "best", 300,  800, 1800},
  {"Invaders",     "Invaders",      "invaders",   "best", 500, 1500, 3500},
  {"Slalom",       "Slalom",        "ski",        "best", 300,  800, 1600},
  {"Stack",        "Stack",         "stack",      "best",  10,   25,   50},   // etages
  {"Racing",       "Course",        "race",       "best", 400, 1000, 2000},
  {"Flight",       "Avion",         "sky",        "best", 400, 1200, 2500},
  {"River",        "Riviere",       "river",      "best", 300,  800, 1600},
  {"Fish",         "Poisson",       "fish",       "best", 150,  500, 1200},
  {"Tetris",       "Tetris",        "tetris",     "best", 1000, 3000, 8000},
  {"Snake",        "Snake",         "snake",      "best", 150,  400,  800},
  {"Lunar Lander", "Alunissage",    "lander",     "best", 600, 1800, 4000},
};

static int medalOf(int id, int v) { const Def& d = DEFS[id]; return v >= d.g ? 3 : (v >= d.s ? 2 : (v >= d.b ? 1 : 0)); }
static int stored(int id) { Preferences p; if (!p.begin(DEFS[id].ns, true)) return 0; int v = p.getInt(DEFS[id].key, 0); p.end(); return v; }

// ----------------------------------------------------------------------------- dessin d'une medaille
static void drawMedal(int cx, int cy, int r, int lv) {                 // lv 0 = pas gagnee, 1 bronze, 2 argent, 3 or
  if (lv <= 0) { canvas.drawCircle(cx, cy, r, rgb(74, 78, 116)); canvas.drawCircle(cx, cy, r - 1, rgb(40, 44, 76)); return; }
  static const uint16_t BASE[3][3] = {{205, 127, 50}, {200, 206, 220}, {255, 205, 60}};
  const uint16_t* c = BASE[lv - 1];
  uint16_t base = rgb(c[0], c[1], c[2]), dark = rgb(c[0] * 5 / 12, c[1] * 5 / 12, c[2] * 5 / 12), light = rgb(c[0] + (255 - c[0]) / 2, c[1] + (255 - c[1]) / 2, c[2] + (255 - c[2]) / 2);
  if (r >= 7) { canvas.fillTriangle(cx - 5, cy - r - 4, cx, cy - r + 2, cx - 1, cy - r - 4, rgb(220, 60, 60)); canvas.fillTriangle(cx + 5, cy - r - 4, cx, cy - r + 2, cx + 1, cy - r - 4, rgb(60, 110, 230)); }
  canvas.fillCircle(cx, cy, r, dark); canvas.fillCircle(cx, cy, r - 1, base);
  canvas.drawCircle(cx, cy, r - 3 > 1 ? r - 3 : 1, light);
  canvas.fillRect(cx - 1, cy - 1, 3, 3, light);
  canvas.drawPixel(cx - r / 2, cy - r / 2, TFT_WHITE);
}

// ----------------------------------------------------------------------------- bandeau "nouvelle medaille"
static uint32_t until = 0, since = 0, lastT = 0; static int bMedal = 0, lastId = -1, lastM = 0; static bool bNew = false;

void record(int id, uint32_t value) {
  if (id < 0 || id >= T_COUNT) return;
  int m = medalOf(id, (int)value), pm = medalOf(id, stored(id));
  if (m <= 0) return;
  bool isNew = m > pm; uint32_t now = millis();
  if (!isNew && id == lastId && m == lastM && now - lastT < 30000) return;      // pas de repetition pendant la meme partie
  lastId = id; lastM = m; lastT = now;
  bMedal = m; bNew = isNew; since = now; until = now + 3600;
  if (isNew) { sfx(784, 70); sfx(988, 70, false); sfx(1319, 120, false); if (m == 3) sfx(1760, 260, false); }
}

void banner() {
  uint32_t now = millis();
  if (now >= until) return;
  int age = (int)(now - since), y = age < 260 ? -24 + age * 28 / 260 : 4;
  if ((int)(until - now) < 260) y = 4 - (260 - (int)(until - now)) * 28 / 260;
  static const char* NEN[3] = {"BRONZE MEDAL", "SILVER MEDAL", "GOLD MEDAL"}; static const char* NFR[3] = {"MEDAILLE BRONZE", "MEDAILLE ARGENT", "MEDAILLE OR"};
  const char* name = (g_lang ? NFR : NEN)[bMedal - 1];
  int w = 176, x = (SCR_W - w) / 2;
  canvas.fillRoundRect(x, y, w, 24, 8, rgb(10, 8, 26)); canvas.drawRoundRect(x, y, w, 24, 8, bMedal == 3 ? rgb(255, 205, 60) : (bMedal == 2 ? rgb(200, 206, 220) : rgb(205, 127, 50)));
  drawMedal(x + 16, y + 13, 8, bMedal);
  txt(name, x + 30, y + 1, &fonts::Font2, TFT_WHITE, textdatum_t::top_left);
  if (bNew && (now / 250) % 2 == 0) txt("NEW!", x + w - 6, y + 1, &fonts::Font2, rgb(255, 120, 120), textdatum_t::top_right);
}

// ----------------------------------------------------------------------------- ecran "TROPHEES"
static int page = 0;
static const int PER = 5, PAGES = (T_COUNT + PER - 1) / PER;

void begin() { page = 0; }

static void render() {
  canvas.fillScreen(rgb(14, 16, 34));
  canvas.fillRect(0, 0, SCR_W, 15, rgb(26, 30, 62));
  int total = 0; for (int i = 0; i < T_COUNT; i++) total += medalOf(i, stored(i));
  txt(L("TROPHIES", "TROPHEES"), SCR_W / 2, -1, &fonts::Font2, rgb(255, 210, 80), textdatum_t::top_center);
  char b[24]; snprintf(b, sizeof b, "%d/%d", total, T_COUNT * 3); txt(b, 5, 4, &fonts::Font0, rgb(150, 160, 210), textdatum_t::top_left);
  snprintf(b, sizeof b, "%d/%d", page + 1, PAGES); txt(b, SCR_W - 5, 4, &fonts::Font0, rgb(150, 160, 210), textdatum_t::top_right);
  for (int k = 0; k < PER; k++) {
    int id = page * PER + k; if (id >= T_COUNT) break;
    int y = 17 + k * 21, v = stored(id), m = medalOf(id, v);
    canvas.fillRoundRect(4, y, SCR_W - 8, 19, 5, rgb(22, 26, 54));
    txt((g_lang ? DEFS[id].fr : DEFS[id].en), 10, y + 1, &fonts::Font2, TFT_WHITE, textdatum_t::top_left);
    if (v > 0) { snprintf(b, sizeof b, "%d", v); txt(b, 118, y + 6, &fonts::Font0, rgb(150, 200, 255), textdatum_t::top_left); }
    for (int lv = 1; lv <= 3; lv++) drawMedal(SCR_W - 52 + (lv - 1) * 18, y + 10, 6, m >= lv ? lv : 0);
  }
  txt(L("A/B: next page   hold PWR: menu", "A/B : page suivante   PWR long : menu"), SCR_W / 2, SCR_H - 8, &fonts::Font0, rgb(110, 118, 165), textdatum_t::top_center);
}

void loop() {
  if (M5.BtnA.wasPressed() || M5.BtnB.wasPressed()) { page = (page + 1) % PAGES; sfx(1200, 15); }
  else if (M5.BtnPWR.wasPressed()) { page = (page + PAGES - 1) % PAGES; sfx(1000, 15); }
  render();
  present(0, 0);
  delay(10);
}

void icon(int x, int y) {
  canvas.fillRoundRect(x, y, 64, 64, 6, rgb(40, 34, 90));
  uint16_t gold = rgb(255, 205, 60), dk = rgb(170, 110, 20), lt = rgb(255, 240, 160);
  canvas.fillRect(x + 26, y + 40, 12, 8, dk); canvas.fillRoundRect(x + 18, y + 48, 28, 6, 2, gold);               // pied
  canvas.drawCircle(x + 14, y + 22, 7, gold); canvas.drawCircle(x + 50, y + 22, 7, gold);                         // anses
  canvas.fillRoundRect(x + 18, y + 8, 28, 8, 3, gold); canvas.fillRect(x + 18, y + 12, 28, 16, gold); canvas.fillCircle(x + 32, y + 28, 14, gold);
  canvas.fillRect(x + 18, y + 12, 6, 20, lt); canvas.fillTriangle(x + 32, y + 14, x + 35, y + 21, x + 28, y + 21, dk);
  canvas.fillCircle(x + 32, y + 22, 4, rgb(255, 250, 220));
}

}  // namespace trophy
