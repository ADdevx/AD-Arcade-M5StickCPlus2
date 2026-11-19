// ============================================================================
//  CASSE-BRIQUES - M5 a l'horizontale : pencher a droite / a gauche = la raquette suit
//  M5 (A) = jouer / lancer la balle ; B (cote) = recalibrer ; HAUT (PWR) = pause
// ============================================================================
#include "common.h"

namespace breakout {

static const uint32_t STEP_US = 20000;               // 50 Hz
static const int COLS = 12, MAXROWS = 7, BW = 18, BH = 7, PITCH_X = 20, PITCH_Y = 9, TOP = 20;
static const int PAD_Y = 124, PAD_H = 4, PAD_W = 52, HUD_H = 15;
static const float BALL_R = 3.0f;
enum State { TITLE, READY, PLAY, PAUSED, LEVELUP, OVER };
static State state = TITLE;
static Preferences pr;
static uint32_t last = 0, acc = 0;
static uint8_t hp[MAXROWS][COLS];
static int rows = 4, bricksLeft = 0;
static float padX = 120, padV = 0;
static float bx, by, vx, vy;
static bool stuck = true;
static int lives = 3, level = 1, readyT = 0, endT = 0, animT = 0, hits = 0;
static uint32_t score = 0, best = 0;

static const uint16_t ROWCOL[MAXROWS] = {
  rgb(230, 60, 60), rgb(240, 140, 40), rgb(240, 210, 50), rgb(70, 200, 80), rgb(60, 200, 220), rgb(70, 110, 240), rgb(170, 90, 230)
};

static void buildLevel() {
  rows = 4 + (level - 1); if (rows > MAXROWS) rows = MAXROWS;
  bricksLeft = 0;
  memset(hp, 0, sizeof hp);
  for (int r = 0; r < rows; r++) for (int c = 0; c < COLS; c++) {
    if (level > 1 && rnd(0, 99) < 8 + level * 2) continue;          // quelques trous a partir du niveau 2
    hp[r][c] = (level >= 3 && r == 0) ? 2 : 1;                       // rangee du haut : 2 coups
    bricksLeft++;
  }
}
static float baseSpeed() { float s = 2.3f + 0.25f * (level - 1) + hits * 0.012f; return s > 4.0f ? 4.0f : s; }
static void stick() { stuck = true; bx = padX; by = PAD_Y - BALL_R - 1; vx = vy = 0; }
static void reset() {
  lives = 3; level = 1; score = 0; hits = 0; padX = SCR_W / 2; padV = 0; animT = 0; endT = 0;
  buildLevel(); stick();
}
void begin() {
  pr.begin("breakout", false); best = pr.getInt("best", 0);
  tilt::load();
  reset(); state = TITLE; last = 0; acc = 0;
}

static void launch() {
  stuck = false; float s = baseSpeed();
  float a = ((int)rnd(0, 40) - 20) * 0.01f + (padV > 0.5f ? 0.25f : (padV < -0.5f ? -0.25f : 0.f));
  vx = s * sinf(a); vy = -s * cosf(a);
  sfx(660, 30); sfx(990, 40, false);
}
static void gameOver() {
  state = OVER; endT = 0;
  trophy::record(trophy::T_BREAKOUT, score); if (score > best) { best = score; pr.putInt("best", best); }
  sfx(300, 120); sfx(120, 300, false);
}

// teste la balle contre les briques ; retourne true si touchee (et detruit/abime la brique)
static bool hitBrick() {
  int c0 = (int)((bx - BALL_R - 1) / PITCH_X), c1 = (int)((bx + BALL_R - 1) / PITCH_X);
  int r0 = (int)((by - BALL_R - TOP) / PITCH_Y), r1 = (int)((by + BALL_R - TOP) / PITCH_Y);
  if (by - BALL_R - TOP < 0) r0 = 0;
  for (int r = r0; r <= r1; r++) for (int c = c0; c <= c1; c++) {
    if (r < 0 || r >= rows || c < 0 || c >= COLS || !hp[r][c]) continue;
    float x0 = 1 + c * PITCH_X, y0 = TOP + r * PITCH_Y;
    float nx = clampf(bx, x0, x0 + BW), ny = clampf(by, y0, y0 + BH);
    float dx = bx - nx, dy = by - ny;
    if (dx * dx + dy * dy <= BALL_R * BALL_R) {
      if (--hp[r][c] == 0) { bricksLeft--; score += 10 * (rows - r); hits++; sfx(700 + (MAXROWS - r) * 110, 40); }
      else { sfx(300, 40); }
      return true;
    }
  }
  return false;
}

static void step() {
  animT++;
  if (state == TITLE || state == OVER || state == PAUSED) { if (state == OVER) endT++; return; }
  if (state == LEVELUP) { endT++; return; }
  tilt::update();
  float t = tilt::x(); if (fabsf(t) < 0.07f) t = 0; else t = t > 0 ? t - 0.07f : t + 0.07f;
  float target = t * 7.5f;
  padV += (target - padV) * 0.3f;
  padX += padV; padX = clampf(padX, PAD_W / 2.f, SCR_W - PAD_W / 2.f);
  if (stuck) { bx = padX; by = PAD_Y - BALL_R - 1; return; }
  // balle : 2 sous-pas par image
  for (int s = 0; s < 2; s++) {
    bx += vx * 0.5f;
    if (bx < BALL_R) { bx = BALL_R; vx = fabsf(vx); sfx(500, 15); }
    if (bx > SCR_W - BALL_R) { bx = SCR_W - BALL_R; vx = -fabsf(vx); sfx(500, 15); }
    if (hitBrick()) { vx = -vx; bx += vx * 0.5f; }
    by += vy * 0.5f;
    if (by < HUD_H + BALL_R) { by = HUD_H + BALL_R; vy = fabsf(vy); sfx(500, 15); }
    if (hitBrick()) { vy = -vy; by += vy * 0.5f; }
    // raquette
    if (vy > 0 && by + BALL_R >= PAD_Y && by - BALL_R <= PAD_Y + PAD_H && bx > padX - PAD_W / 2.f - BALL_R && bx < padX + PAD_W / 2.f + BALL_R) {
      float rel = clampf((bx - padX) / (PAD_W / 2.f + BALL_R), -1.f, 1.f);
      float a = rel * 1.05f + padV * 0.03f; a = clampf(a, -1.1f, 1.1f);
      float sp = baseSpeed();
      vx = sp * sinf(a); vy = -sp * cosf(a); by = PAD_Y - BALL_R;
      sfx(440, 25);
    }
  }
  if (bricksLeft <= 0) { state = LEVELUP; endT = 0; sfx(988, 80); sfx(1318, 80, false); sfx(1760, 160, false); return; }
  if (by > SCR_H + BALL_R) {
    if (--lives <= 0) { gameOver(); return; }
    sfx(200, 100); sfx(110, 160, false); stick();
  }
}

static void render() {
  canvas.fillScreen(rgb(8, 10, 26));
  // briques
  for (int r = 0; r < rows; r++) for (int c = 0; c < COLS; c++) if (hp[r][c]) {
    int x = 1 + c * PITCH_X, y = TOP + r * PITCH_Y;
    uint16_t col = ROWCOL[r];
    canvas.fillRect(x, y, BW, BH, col);
    canvas.drawFastHLine(x, y, BW, rgb(255, 255, 255 - 60));
    canvas.drawFastHLine(x, y + BH - 1, BW, rgb(40, 40, 60));
    if (hp[r][c] == 2) canvas.drawRect(x, y, BW, BH, rgb(255, 255, 255));
  }
  // raquette
  int px = (int)(padX - PAD_W / 2);
  canvas.fillRoundRect(px, PAD_Y, PAD_W, PAD_H, 2, rgb(200, 210, 235)); canvas.fillRect(px + 2, PAD_Y, 6, 2, rgb(240, 80, 70)); canvas.fillRect(px + PAD_W - 8, PAD_Y, 6, 2, rgb(240, 80, 70));
  // balle
  if (state != TITLE) { canvas.fillCircle((int)bx + 1, (int)by + 1, (int)BALL_R, rgb(40, 40, 70)); canvas.fillCircle((int)bx, (int)by, (int)BALL_R, TFT_WHITE); }
  // HUD
  canvas.fillRect(0, 0, SCR_W, HUD_H, rgb(16, 18, 34)); canvas.drawFastHLine(0, HUD_H, SCR_W, rgb(60, 70, 120));
  char b[24];
  snprintf(b, sizeof b, "%lu", (unsigned long)score); txt(b, 6, 1, &fonts::Font2, TFT_WHITE);
  snprintf(b, sizeof b, L("LVL %d","NIV %d"), level); txt(b, SCR_W / 2, 1, &fonts::Font2, rgb(255, 210, 80), textdatum_t::top_center);
  for (int i = 0; i < lives; i++) canvas.fillCircle(SCR_W - 8 - i * 10, 7, 3, TFT_WHITE);
  if (state == TITLE) {
    canvas.fillRoundRect(16, 70, 208, 52, 6, rgb(16, 18, 34)); canvas.drawRoundRect(16, 70, 208, 52, 6, rgb(120, 140, 220));
    txt(L("BREAKOUT","CASSE-BRIQUES"), SCR_W / 2, 74, &fonts::Font4, rgb(255, 210, 80), textdatum_t::top_center);
    if (best > 0) { snprintf(b, sizeof b, L("best %lu","record %lu"), (unsigned long)best); txt(b, SCR_W - 4, 124, &fonts::Font0, rgb(255, 230, 120), textdatum_t::top_right); }
  }
  if (state == PAUSED) { canvas.fillRoundRect(80, 84, 80, 28, 5, rgb(16, 18, 34)); txt("PAUSE", SCR_W / 2, 88, &fonts::Font4, TFT_WHITE, textdatum_t::top_center); }
  if (state == LEVELUP) {
    canvas.fillRoundRect(40, 60, 160, 54, 6, rgb(16, 18, 34)); canvas.drawRoundRect(40, 60, 160, 54, 6, rgb(70, 200, 80));
    txt(L("LEVEL CLEAR!","NIVEAU REUSSI !"), SCR_W / 2, 66, &fonts::Font2, rgb(70, 200, 80), textdatum_t::top_center);
    snprintf(b, sizeof b, "score %lu", (unsigned long)score); txt(b, SCR_W / 2, 84, &fonts::Font2, TFT_WHITE, textdatum_t::top_center);
  }
  if (state == OVER) {
    canvas.fillRoundRect(36, 60, 168, 62, 6, rgb(16, 18, 34)); canvas.drawRoundRect(36, 60, 168, 62, 6, rgb(230, 80, 70));
    txt("GAME OVER", SCR_W / 2, 64, &fonts::Font4, rgb(230, 80, 70), textdatum_t::top_center);
    snprintf(b, sizeof b, L("score %lu  best %lu","score %lu  record %lu"), (unsigned long)score, (unsigned long)best); txt(b, SCR_W / 2, 92, &fonts::Font2, TFT_WHITE, textdatum_t::top_center);
  }
}

void loop() {
  uint32_t now = micros();
  if (last == 0) last = now;
  acc += now - last; last = now; if (acc > 100000) acc = 100000;
  bool a = M5.BtnA.wasPressed(), p = M5.BtnPWR.wasPressed();
  switch (state) {
    case TITLE: if (a) { reset(); state = PLAY; sfx(660, 40); } break;
        case PLAY: if (p) { state = PAUSED; sfx(440, 50); } else if (a && stuck) launch(); break;
    case PAUSED: if (p || a) { state = PLAY; sfx(660, 50); } break;
    case LEVELUP: if (a && endT > 40) { level++; buildLevel(); stick(); state = PLAY; sfx(660, 40); } break;
    case OVER: if (a && endT > 40) { reset(); state = PLAY; sfx(660, 40); } break;
  }
  while (acc >= STEP_US) { step(); acc -= STEP_US; }
  render();
  bgm::run(10, state == PLAY);
  present(0, 0);
}

void icon(int x, int y) {
  canvas.fillRoundRect(x, y, 64, 64, 6, rgb(8, 10, 26));
  for (int r = 0; r < 4; r++) for (int c = 0; c < 4; c++) if (!(r == 2 && c == 1)) canvas.fillRect(x + 4 + c * 15, y + 6 + r * 8, 13, 6, ROWCOL[r]);
  canvas.fillCircle(x + 40, y + 42, 3, TFT_WHITE);
  canvas.drawLine(x + 36, y + 36, x + 40, y + 42, rgb(120, 130, 170));
  canvas.fillRoundRect(x + 20, y + 54, 26, 4, 2, rgb(200, 210, 235));
}

}  // namespace breakout
