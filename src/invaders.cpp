// ============================================================================
//  INVADERS - M5 a l'horizontale : pencher = deplacer le canon ; M5 (A) = tirer
//  B (cote) = recalibrer (ecran titre) ; HAUT (PWR) = pause
// ============================================================================
#include "common.h"

namespace invaders {

static const uint32_t STEP_US = 20000;
static const int ACOLS = 8, AROWS = 4, APX = 22, APY = 15, AW = 16, AH = 14;
static const int SHIP_Y = 117, HUD_H = 14, GROUND_Y = 131;
enum State { TITLE, READY, PLAY, PAUSED, WAVEUP, OVER };
static State state = TITLE;
static Preferences pr;
static uint32_t last = 0, acc = 0;

// 3 sortes d'envahisseurs, 2 images chacun (8 x 7 points, dessines en x2)
static const uint8_t SPR[3][2][7] = {
  {{0x18, 0x3C, 0x7E, 0xDB, 0xFF, 0x24, 0x42}, {0x18, 0x3C, 0x7E, 0xDB, 0xFF, 0x5A, 0xA5}},
  {{0x24, 0xBD, 0xFF, 0xDB, 0x7E, 0x24, 0x42}, {0x24, 0x3C, 0xFF, 0xDB, 0x7E, 0x42, 0x81}},
  {{0x3C, 0x7E, 0xFF, 0xE7, 0xFF, 0x3C, 0x66}, {0x3C, 0x7E, 0xFF, 0xE7, 0xFF, 0x66, 0xC3}},
};
static const uint8_t ROWTYPE[AROWS] = {0, 1, 1, 2};
static const int ROWPTS[AROWS] = {30, 20, 20, 10};
static const uint16_t TYPECOL[3] = {rgb(255, 100, 210), rgb(90, 225, 255), rgb(130, 255, 120)};

static uint8_t alive[AROWS][ACOLS]; static int nAlive = 0;
static float gx, gy; static int dir = 1, moveT = 0, frame = 0, noteI = 0;
static float padX = 120, padV = 0;
static int lives = 3, wave = 1, invul = 0, readyT = 0, endT = 0, animT = 0;
static uint32_t score = 0, best = 0;
static bool pb = false; static float pbx, pby;
struct Bomb { float x, y; bool on; }; static Bomb bombs[3]; static int bombT = 60;
struct Boom { float x, y; int t; uint16_t col; }; static Boom booms[8];
static bool ufoOn = false; static float ufoX; static int ufoDir = 1, ufoT = 900, ufoPts = 50;
static uint8_t shield[3][5][12];
static const int SH_X[3] = {36, 108, 180}, SH_Y = 99;
static const char* SHAPE[5] = {"011111111110", "111111111111", "111111111111", "111100001111", "111000000111"};

static void boom(float x, float y, uint16_t col) { for (auto &b : booms) if (b.t <= 0) { b = {x, y, 12, col}; return; } }
static void resetShields() { for (int s = 0; s < 3; s++) for (int r = 0; r < 5; r++) for (int c = 0; c < 12; c++) shield[s][r][c] = SHAPE[r][c] == '1'; }

static void startWave() {
  gx = 20; gy = 20 + (wave > 5 ? 4 : wave - 1) * 6; dir = 1; moveT = 0; frame = 0;
  memset(alive, 1, sizeof alive); nAlive = AROWS * ACOLS;
  for (auto &b : bombs) b.on = false;
  pb = false; for (auto &b : booms) b.t = 0;
  bombT = 60; resetShields();
}
static void reset() {
  lives = 3; wave = 1; score = 0; padX = SCR_W / 2; padV = 0; invul = 0; animT = 0; endT = 0;
  ufoOn = false; ufoT = rnd(700, 1200);
  startWave();
}
void begin() {
  pr.begin("invaders", false); best = pr.getInt("best", 0);
  tilt::load();
  reset(); state = TITLE; last = 0; acc = 0;
}

static void gameOver() {
  state = OVER; endT = 0;
  if (score > best) { best = score; pr.putInt("best", best); }
  sfx(300, 120); sfx(120, 320, false);
}
static void playerHit() {
  boom(padX, SHIP_Y + 3, rgb(255, 200, 80)); boom(padX - 6, SHIP_Y, rgb(255, 120, 60)); boom(padX + 6, SHIP_Y, rgb(255, 120, 60));
  for (auto &b : bombs) b.on = false;
  sfx(220, 120); sfx(110, 220, false);
  if (--lives <= 0) { gameOver(); return; }
  invul = 100;
}

// un projectile au point (px,py) touche-t-il un bouclier ? (et le ronge)
static bool shieldHit(float px, float py) {
  for (int s = 0; s < 3; s++) {
    int lx = (int)px - SH_X[s], ly = (int)py - SH_Y;
    if (lx < 0 || lx >= 24 || ly < 0 || ly >= 10) continue;
    int cx = lx / 2, cy = ly / 2;
    if (!shield[s][cy][cx]) continue;
    shield[s][cy][cx] = 0;
    for (int k = 0; k < 3; k++) { int nx = cx + (int)rnd(0, 2) - 1, ny = cy + (int)rnd(0, 2) - 1; if (nx >= 0 && nx < 12 && ny >= 0 && ny < 5) shield[s][ny][nx] = 0; }
    return true;
  }
  return false;
}
static void eatShields() {            // les envahisseurs qui descendent detruisent les boucliers
  for (int r = 0; r < AROWS; r++) for (int c = 0; c < ACOLS; c++) if (alive[r][c]) {
    int ax = (int)gx + c * APX, ay = (int)gy + r * APY;
    for (int s = 0; s < 3; s++) {
      if (ax + AW < SH_X[s] || ax > SH_X[s] + 24 || ay + AH < SH_Y || ay > SH_Y + 10) continue;
      for (int cy = 0; cy < 5; cy++) for (int cx = 0; cx < 12; cx++) {
        int px = SH_X[s] + cx * 2, py = SH_Y + cy * 2;
        if (px + 2 > ax && px < ax + AW && py + 2 > ay && py < ay + AH) shield[s][cy][cx] = 0;
      }
    }
  }
}

static int interval() { int v = 2 + (int)(nAlive * 0.55f) - (wave - 1) * 2; return v < 2 ? 2 : v; }
static void moveAliens() {
  int minC = ACOLS, maxC = -1, maxR = -1;
  for (int r = 0; r < AROWS; r++) for (int c = 0; c < ACOLS; c++) if (alive[r][c]) { if (c < minC) minC = c; if (c > maxC) maxC = c; if (r > maxR) maxR = r; }
  if (maxC < 0) return;
  float left = gx + minC * APX, right = gx + maxC * APX + AW;
  bool edge = (dir > 0 && right + 3 > SCR_W - 3) || (dir < 0 && left - 3 < 3);
  if (edge) { gy += 6; dir = -dir; } else gx += dir * 3;
  frame ^= 1;
  static const int NOTES[4] = {131, 117, 104, 98};
  sfx(NOTES[noteI++ & 3], 45);
  eatShields();
  if (gy + maxR * APY + AH >= SHIP_Y - 1) { boom(padX, SHIP_Y + 3, rgb(255, 200, 80)); gameOver(); }
}

static void spawnBomb() {
  int cols[ACOLS], n = 0;
  for (int c = 0; c < ACOLS; c++) for (int r = 0; r < AROWS; r++) if (alive[r][c]) { cols[n++] = c; break; }
  if (!n) return;
  int c = cols[rnd(0, n - 1)], rr = 0;
  for (int r = AROWS - 1; r >= 0; r--) if (alive[r][c]) { rr = r; break; }
  for (auto &b : bombs) if (!b.on) { b = {gx + c * APX + AW / 2.f, gy + rr * APY + AH, true}; return; }
}

static void step() {
  animT++;
  for (auto &b : booms) if (b.t > 0) b.t--;
  if (state == TITLE || state == PAUSED) return;
  if (state == OVER) { endT++; return; }
  if (state == WAVEUP) { if (++endT > 80) { wave++; startWave(); state = PLAY; } return; }
  tilt::update();
  float t = tilt::x(); if (fabsf(t) < 0.07f) t = 0; else t = t > 0 ? t - 0.07f : t + 0.07f;
  padV += (t * 4.8f - padV) * 0.3f;
  padX = clampf(padX + padV, 10, SCR_W - 10);
  // ----- PLAY -----
  if (invul > 0) invul--;
  if (++moveT >= interval()) { moveT = 0; moveAliens(); if (state != PLAY) return; }
  if (--bombT <= 0) { spawnBomb(); int v = (int)rnd(30, 70) - wave * 4; bombT = v < 14 ? 14 : v; }
  // ovni
  if (ufoOn) {
    ufoX += ufoDir * 1.2f; if ((animT & 7) == 0) sfx(900 + (animT & 8) * 20, 20);
    if (ufoX < -20 || ufoX > SCR_W + 4) { ufoOn = false; ufoT = rnd(800, 1500); }
  } else if (--ufoT <= 0) { ufoOn = true; ufoDir = rnd(0, 1) ? 1 : -1; ufoX = ufoDir > 0 ? -18 : SCR_W + 2; ufoPts = 50 * (int)rnd(1, 3); }
  // tir du joueur
  if (pb) {
    pby -= 6;
    bool done = false;
    if (pby < HUD_H) done = true;
    if (!done && ufoOn && pbx >= ufoX && pbx <= ufoX + 16 && pby >= 15 && pby <= 24) { score += ufoPts; boom(ufoX + 8, 19, rgb(255, 80, 80)); ufoOn = false; ufoT = rnd(800, 1500); sfx(1400, 60); sfx(1900, 90, false); done = true; }
    for (int r = 0; r < AROWS && !done; r++) for (int c = 0; c < ACOLS && !done; c++) if (alive[r][c]) {
      float ax = gx + c * APX, ay = gy + r * APY;
      if (pbx >= ax && pbx <= ax + AW && pby >= ay && pby <= ay + AH) {
        alive[r][c] = 0; nAlive--; score += ROWPTS[r]; boom(ax + AW / 2, ay + AH / 2, TYPECOL[ROWTYPE[r]]); sfx(600, 30); sfx(300, 50, false); done = true;
      }
    }
    if (!done && shieldHit(pbx, pby)) done = true;
    if (done) pb = false;
  }
  // bombes
  for (auto &b : bombs) if (b.on) {
    b.y += 1.7f + wave * 0.12f;
    if (b.y > GROUND_Y) { b.on = false; continue; }
    if (shieldHit(b.x, b.y + 3)) { b.on = false; continue; }
    if (!invul && b.y + 4 >= SHIP_Y && b.y <= SHIP_Y + 8 && fabsf(b.x - padX) < 8) { b.on = false; playerHit(); if (state != PLAY) return; }
  }
  if (nAlive <= 0) { state = WAVEUP; endT = 0; pb = false; sfx(988, 80); sfx(1318, 80, false); sfx(1760, 160, false); }
}

static void drawSpr(const uint8_t* rows, int x, int y, uint16_t col, int sc = 2) {
  for (int j = 0; j < 7; j++) for (int i = 0; i < 8; i++) if (rows[j] & (0x80 >> i)) canvas.fillRect(x + i * sc, y + j * sc, sc, sc, col);
}
static void drawShip(int x, int y, uint16_t col) {
  canvas.fillRect(x - 8, y + 4, 16, 4, col);
  canvas.fillRect(x - 6, y + 2, 12, 3, col);
  canvas.fillRect(x - 1, y - 2, 3, 5, col);
  canvas.fillRect(x - 8, y + 7, 16, 1, rgb(40, 120, 40));
}
static void drawUfo(int x, int y) {
  canvas.fillEllipse(x + 8, y + 4, 8, 3, rgb(230, 60, 60));
  canvas.fillEllipse(x + 8, y + 2, 4, 3, rgb(255, 140, 140));
  for (int i = 0; i < 3; i++) canvas.fillRect(x + 3 + i * 4, y + 4, 2, 1, rgb(255, 240, 120));
}

static void render() {
  canvas.fillScreen(rgb(2, 3, 12));
  for (int i = 0; i < 24; i++) { int sx = (i * 97 + 13) % SCR_W, sy = HUD_H + 2 + (i * 53) % 110; canvas.drawPixel(sx, sy, rgb(60 + (i * 7) % 60, 60 + (i * 7) % 60, 90)); }
  // boucliers
  for (int s = 0; s < 3; s++) for (int r = 0; r < 5; r++) for (int c = 0; c < 12; c++) if (shield[s][r][c]) canvas.fillRect(SH_X[s] + c * 2, SH_Y + r * 2, 2, 2, rgb(70, 220, 90));
  // envahisseurs
  for (int r = 0; r < AROWS; r++) for (int c = 0; c < ACOLS; c++) if (alive[r][c]) drawSpr(SPR[ROWTYPE[r]][frame], (int)gx + c * APX, (int)gy + r * APY, TYPECOL[ROWTYPE[r]]);
  if (ufoOn) drawUfo((int)ufoX, 15);
  // tirs
  if (pb) canvas.fillRect((int)pbx, (int)pby - 2, 2, 6, TFT_WHITE);
  for (auto &b : bombs) if (b.on) { int o = ((int)b.y >> 2) & 1; canvas.fillRect((int)b.x + o, (int)b.y, 2, 3, rgb(255, 230, 80)); canvas.fillRect((int)b.x + 1 - o, (int)b.y + 3, 2, 3, rgb(255, 230, 80)); }
  // canon
  if (state != OVER && (invul == 0 || (animT & 4))) drawShip((int)padX, SHIP_Y, rgb(90, 255, 120));
  // explosions
  for (auto &b : booms) if (b.t > 0) {
    int k = 12 - b.t; int x = (int)b.x, y = (int)b.y;
    for (int a = 0; a < 8; a++) { float an = a * 0.7854f; canvas.drawPixel(x + (int)(cosf(an) * (2 + k)), y + (int)(sinf(an) * (2 + k)), b.col); canvas.drawPixel(x + (int)(cosf(an) * (1 + k / 2)), y + (int)(sinf(an) * (1 + k / 2)), TFT_WHITE); }
  }
  canvas.drawFastHLine(0, GROUND_Y, SCR_W, rgb(40, 140, 60));
  // HUD
  canvas.fillRect(0, 0, SCR_W, HUD_H, rgb(10, 12, 30)); canvas.drawFastHLine(0, HUD_H, SCR_W, rgb(50, 60, 110));
  char b[32];
  snprintf(b, sizeof b, "%lu", (unsigned long)score); txt(b, 5, 0, &fonts::Font2, TFT_WHITE);
  snprintf(b, sizeof b, L("WAVE %d","VAGUE %d"), wave); txt(b, SCR_W / 2, 0, &fonts::Font2, rgb(255, 210, 80), textdatum_t::top_center);
  for (int i = 0; i < lives - (state == OVER ? 0 : 1); i++) drawShip(SCR_W - 14 - i * 20, 4, rgb(90, 255, 120));
  if (state == TITLE) {
    canvas.fillRect(0, HUD_H + 1, SCR_W, SCR_H, rgb(2, 3, 12));
    for (int t = 0; t < 3; t++) drawSpr(SPR[t][(animT / 25) & 1], 62 + t * 46, 24, TYPECOL[t]);
    txtO("INVADERS", SCR_W / 2, 48, &fonts::Font4, rgb(90, 255, 120), rgb(10, 60, 20), textdatum_t::top_center);
    if (best > 0) { snprintf(b, sizeof b, L("best %lu","record %lu"), (unsigned long)best); txt(b, SCR_W / 2, 112, &fonts::Font2, rgb(255, 230, 120), textdatum_t::top_center); }
  }
  if (state == PAUSED) { canvas.fillRoundRect(80, 52, 80, 28, 5, rgb(10, 12, 30)); txt("PAUSE", SCR_W / 2, 56, &fonts::Font4, TFT_WHITE, textdatum_t::top_center); }
  if (state == WAVEUP) { canvas.fillRoundRect(50, 52, 140, 28, 5, rgb(10, 12, 30)); canvas.drawRoundRect(50, 52, 140, 28, 5, rgb(90, 255, 120)); txt(L("WAVE CLEAR!","VAGUE REUSSIE !"), SCR_W / 2, 59, &fonts::Font2, rgb(90, 255, 120), textdatum_t::top_center); }
  if (state == OVER) {
    canvas.fillRoundRect(36, 40, 168, 62, 6, rgb(10, 12, 30)); canvas.drawRoundRect(36, 40, 168, 62, 6, rgb(230, 80, 70));
    txt("GAME OVER", SCR_W / 2, 44, &fonts::Font4, rgb(230, 80, 70), textdatum_t::top_center);
    snprintf(b, sizeof b, L("score %lu  best %lu","score %lu  record %lu"), (unsigned long)score, (unsigned long)best); txt(b, SCR_W / 2, 72, &fonts::Font2, TFT_WHITE, textdatum_t::top_center);
  }
}

void loop() {
  uint32_t now = micros();
  if (last == 0) last = now;
  acc += now - last; last = now; if (acc > 100000) acc = 100000;
  bool a = M5.BtnA.wasPressed(), p = M5.BtnPWR.wasPressed();
  switch (state) {
    case TITLE: if (a) { reset(); state = PLAY; sfx(660, 40); } break;
        case PLAY:
      if (p) { state = PAUSED; sfx(440, 50); }
      else if (a && !pb) { pb = true; pbx = padX; pby = SHIP_Y - 3; sfx(1500, 20); sfx(900, 30, false); }
      break;
    case PAUSED: if (p || a) { state = PLAY; sfx(660, 50); } break;
    case WAVEUP: break;
    case OVER: if (a && endT > 40) { reset(); state = PLAY; sfx(660, 40); } break;
  }
  while (acc >= STEP_US) { step(); acc -= STEP_US; }
  render();
  bgm::run(11, state == PLAY);
  present(0, 0);
}

void icon(int x, int y) {
  canvas.fillRoundRect(x, y, 64, 64, 6, rgb(2, 3, 12));
  for (int r = 0; r < 2; r++) for (int c = 0; c < 3; c++) drawSpr(SPR[r == 0 ? 0 : 1][0], x + 4 + c * 20, y + 5 + r * 17, TYPECOL[r == 0 ? 0 : 1], 2);
  drawSpr(SPR[2][0], x + 24, y + 38, TYPECOL[2], 1); drawSpr(SPR[2][0], x + 38, y + 38, TYPECOL[2], 1);
  canvas.fillRect(x + 31, y + 44, 2, 5, TFT_WHITE);
  drawShip(x + 32, y + 52, rgb(90, 255, 120));
  canvas.drawFastHLine(x + 4, y + 60, 56, rgb(40, 140, 60));
}

}  // namespace invaders
