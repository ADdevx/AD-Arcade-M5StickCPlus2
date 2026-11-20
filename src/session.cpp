// ============================================================================
//  MODES SPECIAUX : DEFI DU JOUR, 2 JOUEURS et reglage de la date
//  - Defi du jour : un jeu et une graine par jour (calcules a partir de la date de l'horloge interne),
//    3 essais, meilleur score du jour, serie de jours consecutifs, historique sur 7 jours.
//  - 2 joueurs : on se passe le M5, meme graine pour les deux (memes obstacles au depart), manches 1 ou 3.
//  Les jeux ne savent rien de tout ca : ils appellent trophy::record() a la fin de la partie, qui appelle session::onOver().
// ============================================================================
#include "common.h"
#include <Preferences.h>

// ----------------------------------------------------------------------------- utilitaires
static const uint8_t ELIG[] = {0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14};   // jeux avec un "game over" et un score (tous sauf le labyrinthe)
static const int NELIG = sizeof(ELIG);

static uint32_t hash32(uint32_t x) { x ^= x >> 16; x *= 0x7feb352du; x ^= x >> 15; x *= 0x846ca68bu; x ^= x >> 16; return x; }
static long daysFromCivil(int y, int m, int d) {                                     // jours depuis 1970-01-01
  y -= m <= 2; long era = (y >= 0 ? y : y - 399) / 400; unsigned yoe = (unsigned)(y - era * 400);
  unsigned doy = (153 * (m + (m > 2 ? -3 : 9)) + 2) / 5 + d - 1; unsigned doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
  return era * 146097 + (long)doe - 719468;
}
static int daysInMonth(int y, int m) { static const int D[12] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31}; return m == 2 && ((y % 4 == 0 && y % 100 != 0) || y % 400 == 0) ? 29 : D[(m - 1) % 12]; }
static int weekdayOf(long day) { return (int)(((day + 4) % 7 + 7) % 7); }          // 0 = dimanche
static const char* WD_EN[7] = {"Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"}, *WD_FR[7] = {"dim", "lun", "mar", "mer", "jeu", "ven", "sam"};
static const char* MO_EN[12] = {"Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"}, *MO_FR[12] = {"jan", "fev", "mar", "avr", "mai", "juin", "juil", "aout", "sep", "oct", "nov", "dec"};

static bool clockOk() { return M5.Rtc.isEnabled(); }
static bool readDate(int& y, int& m, int& d) {
  if (!clockOk()) return false;
  auto dt = M5.Rtc.getDate(); y = dt.year; m = dt.month; d = dt.date;
  return y >= 2025 && y <= 2099 && m >= 1 && m <= 12 && d >= 1 && d <= 31;
}
static void buildDefault(int& y, int& m, int& d) {                                    // date de compilation du firmware : bon point de depart
  static const char* MN[12] = {"Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"};
  char mon[4] = {__DATE__[0], __DATE__[1], __DATE__[2], 0}; m = 1; for (int i = 0; i < 12; i++) if (!strcmp(mon, MN[i])) m = i + 1;
  d = atoi(__DATE__ + 4); y = atoi(__DATE__ + 7);
}

static uint16_t SKYC = 0;
static void panel(int x, int y, int w, int h) { canvas.fillRoundRect(x, y, w, h, 6, rgb(22, 26, 54)); }
static void header(const char* t, uint16_t col) { canvas.fillScreen(rgb(14, 16, 34)); canvas.fillRect(0, 0, SCR_W, 15, rgb(26, 30, 62)); txt(t, SCR_W / 2, -1, &fonts::Font2, col, textdatum_t::top_center); }
static void footer(const char* t) { txt(t, SCR_W / 2, SCR_H - 9, &fonts::Font0, rgb(110, 118, 165), textdatum_t::top_center); }

// ----------------------------------------------------------------------------- bandeau (dessine par present())
namespace session {
static char ov1[48] = "", ov2[48] = ""; static uint32_t ovUntil = 0, ovSince = 0; static uint16_t ovCol = 0;
static void say(const char* a, const char* b, uint16_t col, uint32_t ms) { snprintf(ov1, sizeof ov1, "%s", a); snprintf(ov2, sizeof ov2, "%s", b ? b : ""); ovCol = col; ovSince = millis(); ovUntil = ovSince + ms; }
void overlay() {
  uint32_t now = millis(); if (now >= ovUntil) return;
  int age = (int)(now - ovSince), left = (int)(ovUntil - now), h = ov2[0] ? 26 : 16, y = SCR_H - h - 3;
  if (age < 200) y += (200 - age) * (h + 4) / 200; else if (left < 200) y += (200 - left) * (h + 4) / 200;
  int w = 196, x = (SCR_W - w) / 2;
  canvas.fillRoundRect(x, y, w, h, 6, rgb(10, 8, 26)); canvas.drawRoundRect(x, y, w, h, 6, ovCol);
  txt(ov1, SCR_W / 2, y + 1, &fonts::Font0, TFT_WHITE, textdatum_t::top_center);
  if (ov2[0]) txt(ov2, SCR_W / 2, y + 13, &fonts::Font0, ovCol, textdatum_t::top_center);
}

// ----------------------------------------------------------------------------- partie "speciale" en cours
static int  activeIdx = -1;                 // jeu lance par un mode special (-1 = aucun)
static int  savedDiff = -1;
static void enterRun(int game, uint32_t seed, int diff) {
  if (savedDiff < 0) savedDiff = g_diff;
  if (diff >= 0) g_diff = diff;
  seedRand(seed); activeIdx = game;
}
static void exitRun() { if (savedDiff >= 0) { g_diff = savedDiff; savedDiff = -1; } g_rngSeeded = false; activeIdx = -1; }
int activeGame() { return activeIdx; }

// ----------------------------------------------------------------------------- reglage de la date
static bool dEd = false; static int dY = 2026, dM = 1, dD = 1, dField = 0; static uint32_t dRep = 0;
bool dateEditing() { return dEd; }
void dateBegin() { dEd = true; dField = 0; if (!readDate(dY, dM, dD)) buildDefault(dY, dM, dD); }
static void dateChange(int s) {
  if (dField == 0) { dD += s; int n = daysInMonth(dY, dM); if (dD > n) dD = 1; if (dD < 1) dD = n; }
  else if (dField == 1) { dM += s; if (dM > 12) dM = 1; if (dM < 1) dM = 12; if (dD > daysInMonth(dY, dM)) dD = daysInMonth(dY, dM); }
  else { dY += s; if (dY > 2060) dY = 2025; if (dY < 2025) dY = 2060; if (dD > daysInMonth(dY, dM)) dD = daysInMonth(dY, dM); }
  sfx(1000 + dField * 150, 10);
}
void dateLoop() {
  uint32_t now = millis();
  if (M5.BtnA.wasPressed()) { dateChange(1); dRep = now + 450; }
  else if (M5.BtnA.isPressed() && dRep && now > dRep) { dateChange(1); dRep = now + 110; }
  if (M5.BtnPWR.wasPressed()) { dateChange(-1); dRep = now + 450; }
  else if (M5.BtnPWR.isPressed() && dRep && now > dRep) { dateChange(-1); dRep = now + 110; }
  if (!M5.BtnA.isPressed() && !M5.BtnPWR.isPressed()) dRep = 0;
  if (M5.BtnB.wasPressed()) {
    if (dField < 2) { dField++; sfx(1200, 15); }
    else {
      m5::rtc_date_t dt; dt.year = dY; dt.month = dM; dt.date = dD; dt.weekDay = weekdayOf(daysFromCivil(dY, dM, dD));
      M5.Rtc.setDate(dt); dEd = false; sfx(988, 60); sfx(1318, 90, false); return;
    }
  }
  header(L("SET THE DATE", "REGLER LA DATE"), rgb(255, 210, 80));
  static const char* LB_EN[3] = {"DAY", "MONTH", "YEAR"}, *LB_FR[3] = {"JOUR", "MOIS", "ANNEE"};
  int vals[3] = {dD, dM, dY}, xs[3] = {14, 90, 160}, ws[3] = {62, 62, 66};
  for (int i = 0; i < 3; i++) {
    bool on = i == dField; int x = xs[i], w = ws[i];
    canvas.fillRoundRect(x, 30, w, 52, 8, on ? rgb(40, 48, 100) : rgb(22, 26, 54)); if (on) canvas.drawRoundRect(x, 30, w, 52, 8, rgb(255, 210, 80));
    txt((g_lang ? LB_FR : LB_EN)[i], x + w / 2, 34, &fonts::Font0, rgb(140, 150, 205), textdatum_t::top_center);
    char b[8]; snprintf(b, sizeof b, i == 2 ? "%d" : "%02d", vals[i]); txt(b, x + w / 2, 48, &fonts::Font4, on ? TFT_WHITE : rgb(190, 196, 230), textdatum_t::top_center);
    if (on) { canvas.fillTriangle(x + w / 2 - 5, 43, x + w / 2 + 5, 43, x + w / 2, 38, rgb(255, 210, 80)); }
  }
  char b[40]; long dn = daysFromCivil(dY, dM, dD);
  snprintf(b, sizeof b, "%s %d %s %d", (g_lang ? WD_FR : WD_EN)[weekdayOf(dn)], dD, (g_lang ? MO_FR : MO_EN)[dM - 1], dY);
  txt(b, SCR_W / 2, 90, &fonts::Font2, rgb(255, 214, 90), textdatum_t::top_center);
  txt(L("The clock keeps the date. Used for the daily challenge.", "L'horloge garde la date. Sert au defi du jour."), SCR_W / 2, 108, &fonts::Font0, rgb(140, 150, 205), textdatum_t::top_center);
  footer(dField < 2 ? L("A: +   PWR: -   B: next", "A : +   PWR : -   B : suivant") : L("A: +   PWR: -   B: confirm", "A : +   PWR : -   B : valider"));
  present(0, 0); delay(10);
}

// ============================================================================ DEFI DU JOUR
}  // namespace session

namespace daily {
using namespace session;
static const int MAXTRIES = 3;
enum { HOME, PLAY, NOCLOCK };
static int phase = HOME; static long today = 0; static int gameOfDay = 0, tries = 0, tbest = 0, streak = 0, bestSt = 0; static uint32_t seed = 0;
static int hist[7]; static long histDay[7];
static bool over = false, armed = true; static uint32_t finishAt = 0; static int anim = 0;
static int lastScore = 0;

static int pickGame(long d) {
  int g = hash32((uint32_t)d) % NELIG, pg = hash32((uint32_t)(d - 1)) % NELIG; if (g == pg) g = (g + 1) % NELIG; return ELIG[g];
}
static void loadDay() {
  int y, m, d; if (!readDate(y, m, d)) { today = 0; return; }
  today = daysFromCivil(y, m, d); gameOfDay = pickGame(today); seed = hash32((uint32_t)today * 7919u + 13u);
  Preferences p; if (!p.begin("daily", true)) { tries = tbest = 0; return; }
  if (p.getLong("td", 0) == today) { tries = p.getInt("tries", 0); tbest = p.getInt("tbest", 0); } else { tries = 0; tbest = 0; }
  streak = p.getInt("streak", 0); bestSt = p.getInt("bestst", 0);
  long lp = p.getLong("lastp", 0); if (lp != today && lp != today - 1) streak = 0;     // serie rompue
  char k[8]; for (int i = 0; i < 7; i++) { snprintf(k, sizeof k, "hd%d", i); histDay[i] = p.getLong(k, 0); snprintf(k, sizeof k, "hs%d", i); hist[i] = p.getInt(k, 0); }
  p.end();
}
static void saveResult(int score) {
  Preferences p; if (!p.begin("daily", false)) return;
  long lp = p.getLong("lastp", 0); int st = p.getInt("streak", 0);
  if (lp != today) { st = (lp == today - 1) ? st + 1 : 1; p.putLong("lastp", today); p.putInt("streak", st); if (st > p.getInt("bestst", 0)) p.putInt("bestst", st); }
  streak = st; bestSt = p.getInt("bestst", 0);
  tries++; if (score > tbest) tbest = score;
  p.putLong("td", today); p.putInt("tries", tries); p.putInt("tbest", tbest);
  int i = (int)(today % 7); char k[8]; snprintf(k, sizeof k, "hd%d", i); p.putLong(k, today); snprintf(k, sizeof k, "hs%d", i); p.putInt(k, tbest);
  histDay[i] = today; hist[i] = tbest;
  p.end();
}

void begin() {
  phase = HOME; anim = 0; exitRun();
  if (!clockOk()) { phase = NOCLOCK; return; }
  int y, m, d; if (!readDate(y, m, d)) { dateBegin(); return; }
  loadDay();
}
void onOver(int id, int score) {
  if (phase != PLAY || id != gameOfDay || over) return;
  over = true; lastScore = score; saveResult(score);
  char a[48], b[48];
  snprintf(a, sizeof a, L("SCORE %d   BEST OF THE DAY %d", "SCORE %d   MEILLEUR DU JOUR %d"), score, tbest);
  if (tries >= MAXTRIES) { finishAt = millis() + 3600; snprintf(b, sizeof b, "%s", L("Daily challenge done!", "Defi du jour termine !")); }
  else snprintf(b, sizeof b, L("%d try left - press A to retry", "%d essai restant - A pour rejouer"), MAXTRIES - tries);
  say(a, b, tries >= MAXTRIES ? rgb(255, 205, 60) : rgb(120, 210, 255), tries >= MAXTRIES ? 3400 : 4500);
  armed = true;
}
static void startRun() {
  enterRun(gameOfDay, seed, 1);                       // difficulte normale pour tout le monde
  gameBegin(gameOfDay); over = false; armed = true; phase = PLAY;
  char a[48]; snprintf(a, sizeof a, L("DAILY CHALLENGE   try %d/%d", "DEFI DU JOUR   essai %d/%d"), tries + 1, MAXTRIES);
  say(a, L("Same start for everyone today", "Meme depart pour tout le monde"), rgb(255, 160, 80), 3000);
}

static void renderHome() {
  int y, m, d; readDate(y, m, d);
  char b[48]; header(L("DAILY CHALLENGE", "DEFI DU JOUR"), rgb(255, 160, 80));
  snprintf(b, sizeof b, "%s %d %s", (g_lang ? WD_FR : WD_EN)[weekdayOf(today)], d, (g_lang ? MO_FR : MO_EN)[m - 1]); txt(b, SCR_W - 5, 3, &fonts::Font0, rgb(150, 160, 210), textdatum_t::top_right);
  panel(4, 18, 100, 98);
  canvas.fillRoundRect(22, 22, 64, 64, 6, rgb(10, 12, 28)); gameIcon(gameOfDay, 22, 22);
  txt(gameName(gameOfDay), 54, 90, &fonts::Font2, TFT_WHITE, textdatum_t::top_center);
  txt(L("TODAY'S GAME", "JEU DU JOUR"), 54, 107 - 2, &fonts::Font0, rgb(140, 150, 205), textdatum_t::top_center);
  panel(108, 18, 128, 98);
  txt(L("TRIES", "ESSAIS"), 114, 22, &fonts::Font0, rgb(140, 150, 205), textdatum_t::top_left);
  for (int i = 0; i < MAXTRIES; i++) { int cx = 156 + i * 14; if (i < tries) canvas.fillCircle(cx, 26, 4, rgb(255, 160, 80)); else { canvas.fillCircle(cx, 26, 4, rgb(40, 46, 90)); canvas.drawCircle(cx, 26, 4, rgb(255, 160, 80)); } }
  txt(L("BEST TODAY", "MEILLEUR"), 114, 36, &fonts::Font0, rgb(140, 150, 205), textdatum_t::top_left);
  snprintf(b, sizeof b, tries ? "%d" : "-", tbest); txt(b, 114, 45, &fonts::Font4, rgb(255, 214, 90), textdatum_t::top_left);
  // flamme + serie
  int fx = 206, fy = 56; uint16_t fl = streak > 0 ? rgb(255, 130, 40) : rgb(70, 76, 110);
  canvas.fillCircle(fx, fy + 4, 5, fl); canvas.fillTriangle(fx - 5, fy + 3, fx + 5, fy + 3, fx, fy - 8, fl); canvas.fillCircle(fx, fy + 5, 2, streak > 0 ? rgb(255, 230, 120) : rgb(90, 96, 130));
  snprintf(b, sizeof b, "%d", streak); txt(b, fx + 9, fy - 2, &fonts::Font2, streak > 0 ? rgb(255, 170, 80) : rgb(110, 116, 150), textdatum_t::top_left);
  // 7 derniers jours
  int mx = 1; for (int i = 0; i < 7; i++) { long dd = today - 6 + i; int ix = (int)(((dd % 7) + 7) % 7); if (histDay[ix] == dd && hist[ix] > mx) mx = hist[ix]; }
  for (int i = 0; i < 7; i++) {
    long dd = today - 6 + i; int ix = (int)(((dd % 7) + 7) % 7); int v = histDay[ix] == dd ? hist[ix] : -1; int bx = 116 + i * 17;
    canvas.fillRect(bx, 98, 13, 2, rgb(60, 68, 120));
    if (v >= 0) { int h = 3 + (int)(26L * v / mx); canvas.fillRect(bx, 98 - h, 13, h, i == 6 ? rgb(255, 170, 70) : rgb(110, 150, 230)); }
    txt((g_lang ? WD_FR : WD_EN)[weekdayOf(dd)], bx + 6, 102, &fonts::Font0, i == 6 ? rgb(255, 214, 90) : rgb(120, 128, 180), textdatum_t::top_center, 1.0f);
  }
  if (tries >= MAXTRIES) footer(L("Done for today - come back tomorrow!   B: date", "Termine pour aujourd'hui - a demain !   B : date"));
  else footer(L("A: play   B: change date   hold PWR: menu", "A : jouer   B : date   PWR long : menu"));
}

void loop() {
  if (dateEditing()) { dateLoop(); if (!dateEditing()) { begin(); } return; }
  anim++;
  if (phase == NOCLOCK) {
    header(L("DAILY CHALLENGE", "DEFI DU JOUR"), rgb(255, 160, 80));
    txt(L("No clock on this device", "Pas d'horloge sur cet appareil"), SCR_W / 2, 50, &fonts::Font2, TFT_WHITE, textdatum_t::top_center);
    txt(L("The daily challenge needs the", "Le defi du jour a besoin de"), SCR_W / 2, 74, &fonts::Font0, rgb(140, 150, 205), textdatum_t::top_center);
    txt(L("built-in clock to know the date.", "l'horloge interne pour la date."), SCR_W / 2, 86, &fonts::Font0, rgb(140, 150, 205), textdatum_t::top_center);
    footer(L("hold PWR: menu", "PWR long : menu")); present(0, 0); delay(10); return;
  }
  if (phase == HOME) {
    if (M5.BtnB.wasPressed()) { dateBegin(); sfx(1200, 15); return; }
    if (M5.BtnA.wasPressed() && tries < MAXTRIES) { startRun(); return; }
    renderHome(); present(0, 0); delay(10); return;
  }
  // PLAY
  if (armed && M5.BtnA.wasPressed()) { seedRand(seed); armed = false; if (!finishAt) over = false; }   // nouvelle partie : on repart de la graine du jour
  gameLoop(gameOfDay);
  if (over && finishAt && millis() >= finishAt) { finishAt = 0; exitRun(); bgm::stop(); phase = HOME; }
}
void icon(int x, int y) {
  canvas.fillRoundRect(x, y, 64, 64, 6, rgb(70, 36, 30));
  canvas.fillRoundRect(x + 10, y + 12, 44, 42, 5, rgb(250, 244, 230)); canvas.fillRoundRect(x + 10, y + 12, 44, 12, 5, rgb(230, 70, 60)); canvas.fillRect(x + 10, y + 19, 44, 5, rgb(230, 70, 60));
  canvas.fillRect(x + 18, y + 6, 4, 11, rgb(250, 244, 230)); canvas.fillRect(x + 42, y + 6, 4, 11, rgb(250, 244, 230));
  uint16_t fl = rgb(255, 140, 40); canvas.fillCircle(x + 32, y + 42, 7, fl); canvas.fillTriangle(x + 25, y + 40, x + 39, y + 40, x + 32, y + 26, fl); canvas.fillCircle(x + 32, y + 43, 3, rgb(255, 232, 120));
}
}  // namespace daily

// ============================================================================ 2 JOUEURS
namespace duo {
using namespace session;
enum { PICK, READY, PLAY, PASS, RESULT };
static int phase = PICK, pick = 0, game = 0, rounds = 1, round = 0, pl = 0, sc[2], wins[2], cur = 0; static uint32_t seed = 0, overAt = 0; static bool over = false, armed = false, final_ = false;
static int anim = 0, mode = 1, soloBest = 0; static bool newBest = false;      // mode : 0 = 1 joueur, 1 = 2 joueurs (1 manche), 2 = 2 joueurs (au meilleur de 3)
static const uint16_t PC[2] = {rgb(90, 170, 255), rgb(255, 140, 80)};

void begin() { phase = PICK; exitRun(); anim = 0; }
void onOver(int id, int score) {
  if (phase != PLAY || id != game || over) return;
  over = true; cur = score; overAt = millis() + 1700;
}
static void newSeed() { seed = hash32(millis() * 2654435761u + (uint32_t)esp_random()); }
static void startTurn() {
  enterRun(game, seed, -1); gameBegin(game); over = false; armed = true; phase = PLAY;
  char a[40]; snprintf(a, sizeof a, L("PLAYER %d", "JOUEUR %d"), pl + 1); if (mode == 0) say(L("SOLO", "SOLO"), L("Beat your best score!", "Bats ton meilleur score !"), PC[0], 2600); else say(a, L("Same start for both players", "Meme depart pour les deux joueurs"), PC[pl], 2600);
}
static void startMatch() { round = 0; pl = 0; wins[0] = wins[1] = 0; newSeed(); phase = READY; exitRun(); }

static void badge(int x, int y, int p, bool big) {
  canvas.fillRoundRect(x, y, big ? 74 : 56, big ? 20 : 15, 6, PC[p]);
  char b[8]; snprintf(b, sizeof b, "P%d", p + 1); txt(b, x + (big ? 37 : 28), y + (big ? 2 : 0), big ? &fonts::Font2 : &fonts::Font2, rgb(10, 12, 30), textdatum_t::top_center);
}
static void crown(int cx, int cy, uint16_t c) {
  canvas.fillRect(cx - 8, cy, 16, 5, c); canvas.fillTriangle(cx - 8, cy, cx - 8, cy - 7, cx - 3, cy, c); canvas.fillTriangle(cx - 3, cy, cx, cy - 9, cx + 3, cy, c); canvas.fillTriangle(cx + 3, cy, cx + 8, cy - 7, cx + 8, cy, c);
}

void loop() {
  anim++;
  char b[48];
  if (phase == PICK) {
    if (M5.BtnB.wasPressed()) { pick = (pick + 1) % NELIG; sfx(1200, 15); }
    if (M5.BtnPWR.wasPressed()) { pick = (pick + NELIG - 1) % NELIG; sfx(1000, 15); }
    if (M5.BtnA.wasPressed()) { game = ELIG[pick]; rounds = mode == 2 ? 3 : 1; soloBest = 0; startMatch(); sfx(880, 40); sfx(1320, 60, false); return; }
    header(L("1-2 PLAYERS", "1-2 JOUEURS"), rgb(120, 210, 255));
    int sl = (int)(sinf(anim * 0.08f) * 2);
    for (int k = -1; k <= 1; k++) {
      int idx = (pick + k + NELIG) % NELIG; int x = SCR_W / 2 - 32 + k * 84;
      if (k == 0) { canvas.fillRoundRect(x - 4, 20 + sl, 72, 72, 8, rgb(40, 48, 100)); canvas.drawRoundRect(x - 4, 20 + sl, 72, 72, 8, rgb(120, 210, 255)); gameIcon(ELIG[idx], x, 24 + sl); }
      else { canvas.fillRoundRect(x, 28, 64, 64, 6, rgb(22, 26, 54)); gameIcon(ELIG[idx], x, 28); for (int yy = 28; yy < 92; yy++) for (int xx = x + ((yy & 1) ? 0 : 1); xx < x + 64; xx += 2) canvas.drawPixel(xx, yy, rgb(14, 16, 34)); }
    }
    txt(gameName(ELIG[pick]), SCR_W / 2, 98, &fonts::Font2, TFT_WHITE, textdatum_t::top_center);
    snprintf(b, sizeof b, "%d/%d", pick + 1, NELIG); txt(b, SCR_W - 5, 3, &fonts::Font0, rgb(150, 160, 210), textdatum_t::top_right);
    footer(L("B/PWR: choose   A: select", "B/PWR : choisir   A : valider")); present(0, 0); delay(10); return;
  }
  if (phase == READY) {
    if (round == 0 && pl == 0 && M5.BtnB.wasPressed()) { mode = (mode + 1) % 3; rounds = mode == 2 ? 3 : 1; sfx(1200, 15); }
    if (M5.BtnA.wasPressed()) { startTurn(); return; }
    header(L("1-2 PLAYERS", "1-2 JOUEURS"), rgb(120, 210, 255));
    txt(gameName(game), SCR_W / 2, 20, &fonts::Font2, TFT_WHITE, textdatum_t::top_center);
    if (rounds > 1) { snprintf(b, sizeof b, L("ROUND %d / %d", "MANCHE %d / %d"), round + 1, rounds); txt(b, SCR_W / 2, 38, &fonts::Font0, rgb(140, 150, 205), textdatum_t::top_center); }
    badge(SCR_W / 2 - 37, 52, pl, true);
    txt(L("get ready!", "prepare-toi !"), SCR_W / 2, 78, &fonts::Font4, TFT_WHITE, textdatum_t::top_center);
    if (rounds > 1 && (round > 0 || pl > 0)) { snprintf(b, sizeof b, "P1  %d - %d  P2", wins[0], wins[1]); txt(b, SCR_W / 2, 106, &fonts::Font0, rgb(255, 214, 90), textdatum_t::top_center); }
    else if (round == 0 && pl == 0) { snprintf(b, sizeof b, L("Mode: %s  (B: change)", "Mode : %s  (B : changer)"), mode == 0 ? L("1 player", "1 joueur") : (mode == 1 ? L("2 players", "2 joueurs") : L("2 players, best of 3", "2 joueurs, meilleur de 3"))); txt(b, SCR_W / 2, 106, &fonts::Font0, rgb(255, 214, 90), textdatum_t::top_center); }
    footer(L("A: start", "A : demarrer")); present(0, 0); delay(10); return;
  }
  if (phase == PLAY) {
    if (armed && M5.BtnA.wasPressed()) { seedRand(seed); armed = false; }
    gameLoop(game);
    if (over && millis() >= overAt) {
      sc[pl] = cur; bgm::stop(); exitRun();
      if (mode == 0) { newBest = cur > soloBest; if (newBest) soloBest = cur; final_ = true; phase = RESULT; sfx(988, 80); sfx(1318, 80, false); if (newBest) sfx(1760, 160, false); }
      else if (pl == 0) { phase = PASS; sfx(660, 80); sfx(880, 80, false); }
      else {
        final_ = false;
        if (sc[0] > sc[1]) wins[0]++; else if (sc[1] > sc[0]) wins[1]++;
        if (rounds == 1 || round >= rounds - 1 || wins[0] >= 2 || wins[1] >= 2) final_ = true;
        phase = RESULT; sfx(988, 80); sfx(1318, 80, false); sfx(1760, 160, false);
      }
    }
    return;
  }
  if (phase == PASS) {
    if (M5.BtnA.wasPressed()) { pl = 1; startTurn(); return; }
    header(L("1-2 PLAYERS", "1-2 JOUEURS"), rgb(120, 210, 255));
    badge(SCR_W / 2 - 37, 22, 0, true);
    snprintf(b, sizeof b, "%d", sc[0]); txt(b, SCR_W / 2, 46, &fonts::Font4, TFT_WHITE, textdatum_t::top_center);
    int ax = SCR_W / 2 + (int)(sinf(anim * 0.15f) * 8);
    canvas.fillTriangle(ax + 16, 86, ax + 16, 102, ax + 30, 94, PC[1]); canvas.fillRect(ax - 24, 90, 40, 8, PC[1]);
    txt(L("Pass the M5 to", "Passe le M5 au"), SCR_W / 2 - 6, 77 - 12, &fonts::Font0, rgb(180, 188, 225), textdatum_t::top_center);
    badge(SCR_W / 2 - 28, 108 - 6, 1, false);
    footer(L("A: player 2 ready", "A : joueur 2 pret")); present(0, 0); delay(10); return;
  }
  // RESULT
  if (mode == 0) {
    if (M5.BtnA.wasPressed()) { newSeed(); pl = 0; startTurn(); return; }
    if (M5.BtnB.wasPressed()) { phase = PICK; sfx(1200, 20); return; }
    header(L("RESULT", "RESULTAT"), rgb(255, 214, 90));
    canvas.fillRoundRect(40, 22, 160, 64, 8, rgb(44, 52, 104)); canvas.drawRoundRect(40, 22, 160, 64, 8, PC[0]);
    txt(gameName(game), SCR_W / 2, 26, &fonts::Font2, TFT_WHITE, textdatum_t::top_center);
    snprintf(b, sizeof b, "%d", sc[0]); txt(b, SCR_W / 2, 46, &fonts::Font4, TFT_WHITE, textdatum_t::top_center);
    if (newBest) { if ((anim / 12) % 2 == 0) txt(L("NEW BEST!", "NOUVEAU RECORD !"), SCR_W / 2, 90, &fonts::Font2, rgb(255, 214, 90), textdatum_t::top_center); }
    else { snprintf(b, sizeof b, L("Best this session: %d", "Meilleur de la session : %d"), soloBest); txt(b, SCR_W / 2, 92, &fonts::Font0, rgb(150, 160, 210), textdatum_t::top_center); }
    footer(L("A: retry   B: other game", "A : rejouer   B : autre jeu")); present(0, 0); delay(10); return;
  }
  if (M5.BtnA.wasPressed()) {
    if (!final_) { round++; pl = 0; newSeed(); phase = READY; sfx(1200, 20); }
    else { startMatch(); sfx(880, 30); }
    return;
  }
  if (M5.BtnB.wasPressed() && final_) { phase = PICK; sfx(1200, 20); return; }
  header(final_ ? L("RESULT", "RESULTAT") : L("ROUND RESULT", "RESULTAT DE LA MANCHE"), rgb(255, 214, 90));
  int win = sc[0] > sc[1] ? 0 : (sc[1] > sc[0] ? 1 : -1);
  for (int p = 0; p < 2; p++) {
    int x = 6 + p * 118; bool w = win == p;
    canvas.fillRoundRect(x, 18, 110, 68, 8, w ? rgb(44, 52, 104) : rgb(22, 26, 54)); if (w) canvas.drawRoundRect(x, 18, 110, 68, 8, PC[p]);
    badge(x + 18, 21, p, true);
    snprintf(b, sizeof b, "%d", sc[p]); txt(b, x + 55, 42, &fonts::Font4, w ? TFT_WHITE : rgb(160, 168, 205), textdatum_t::top_center);
    if (w) crown(x + 55, 78 + (int)(sinf(anim * 0.2f) * 2), rgb(255, 205, 60));
  }
  if (win < 0) snprintf(b, sizeof b, "%s", L("DRAW!", "EGALITE !"));
  else if (final_) snprintf(b, sizeof b, L("PLAYER %d WINS!", "JOUEUR %d GAGNE !"), win + 1);
  else snprintf(b, sizeof b, L("PLAYER %d WINS THE ROUND", "JOUEUR %d GAGNE LA MANCHE"), win + 1);
  txt(b, SCR_W / 2, 90, &fonts::Font2, win < 0 ? TFT_WHITE : PC[win], textdatum_t::top_center);
  if (rounds > 1) { snprintf(b, sizeof b, "P1  %d - %d  P2", wins[0], wins[1]); txt(b, SCR_W / 2, 109, &fonts::Font0, rgb(255, 214, 90), textdatum_t::top_center); }
  footer(final_ ? L("A: rematch   B: other game", "A : revanche   B : autre jeu") : L("A: next round", "A : manche suivante"));
  present(0, 0); delay(10);
}
void icon(int x, int y) {
  canvas.fillRoundRect(x, y, 64, 64, 6, rgb(28, 40, 88));
  for (int p = 0; p < 2; p++) {
    int cx = x + 18 + p * 28, cy = y + 24; uint16_t c = PC[p];
    canvas.fillCircle(cx, cy, 8, c); canvas.fillRoundRect(cx - 11, cy + 10, 22, 22, 8, c);
    canvas.fillCircle(cx - 3, cy - 1, 2, rgb(10, 12, 30)); canvas.fillCircle(cx + 3, cy - 1, 2, rgb(10, 12, 30));
  }
  canvas.fillRoundRect(x + 20, y + 48, 24, 10, 3, rgb(255, 214, 90)); txt("VS", x + 32, y + 49, &fonts::Font0, rgb(60, 30, 10), textdatum_t::top_center, 1.0f);
}
}  // namespace duo

// ----------------------------------------------------------------------------- aiguillage des fins de partie
namespace session {
void onOver(int gameId, int score) { daily::onOver(gameId, score); duo::onOver(gameId, score); }
void end() { exitRun(); dEd = false; ovUntil = 0; }
}
