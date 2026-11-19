// ============================================================================
//  METEORES - M5 tenu a l'horizontale : pencher a droite / a gauche = le vaisseau suit
//  M5 (A) = jouer ; B (cote) = recalibrer ; HAUT (PWR) = pause
// ============================================================================
#include "common.h"

namespace space {

static const uint32_t STEP_US = 20000;
static const int SHIP_Y = 116;
enum State { TITLE, READY, PLAY, PAUSED, OVER };
static State state = TITLE;
static Preferences pr;
static uint32_t last = 0, acc = 0;
static float shipX = 120, shipV = 0;
static int lives = 3, invul = 0, readyT = 0, overT = 0, animT = 0;
static uint32_t score = 0, best = 0;
static float speedMul = 1.0f; static int spawnT = 0;
struct Met { float x, y, vx, vy, r, ang, spin; uint8_t shape[8]; bool on; };
static Met mets[10];
struct Star { float x, y, v; };
static Star stars[36];
struct Spark { float x, y, vx, vy; int life; };
static Spark sparks[24];

static void spark(float x, float y, int n) {
  for (int i = 0; i < n; i++) for (auto &s : sparks) if (s.life <= 0) { float a = rnd(0, 628) / 100.f, v = rnd(5, 25) / 10.f; s = {x, y, cosf(a) * v, sinf(a) * v, (int)rnd(10, 26)}; break; }
}
static void reset() {
  shipX = SCR_W / 2; shipV = 0; lives = 3; invul = 0; score = 0; speedMul = 1.0f; spawnT = 30; animT = 0; overT = 0;
  for (auto &m : mets) m.on = false;
  for (auto &s : sparks) s.life = 0;
}
void begin() {
  pr.begin("space", false); best = pr.getInt("best", 0);
  tilt::load();
  for (auto &s : stars) s = {(float)rnd(0, SCR_W), (float)rnd(0, SCR_H), rnd(4, 20) / 10.f};
  reset(); state = TITLE; last = 0; acc = 0;
}

static void spawn() {
  for (auto &m : mets) if (!m.on) {
    m.on = true; m.r = rnd(5, 14); m.x = rnd(m.r, SCR_W - m.r); m.y = -m.r - 2;
    m.vy = (rnd(10, 22) / 10.f) * speedMul; m.vx = ((int)rnd(0, 20) - 10) / 20.f;
    m.ang = 0; m.spin = ((int)rnd(0, 20) - 10) / 100.f;
    for (int i = 0; i < 8; i++) m.shape[i] = rnd(72, 100);
    return;
  }
}
static void gameOver() {
  state = OVER; overT = 0;
  trophy::record(trophy::T_METEORS, score / 10); if (score / 10 > best) { best = score / 10; pr.putInt("best", best); }
  sfx(300, 120); sfx(120, 300, false);
}

static void step() {
  animT++;
  for (auto &s : stars) { s.y += s.v * (state == PLAY ? 1.f + speedMul * 0.4f : 1.f); if (s.y > SCR_H) { s.y = 0; s.x = rnd(0, SCR_W); } }
  for (auto &p : sparks) if (p.life > 0) { p.x += p.vx; p.y += p.vy; p.life--; }
  if (state == TITLE) return;
  if (state == OVER) { overT++; for (auto &m : mets) if (m.on) { m.y += m.vy; m.ang += m.spin; if (m.y > SCR_H + 20) m.on = false; } return; }
  tilt::update();
  float t = tilt::x(); if (fabsf(t) < 0.08f) t = 0; else t = t > 0 ? t - 0.08f : t + 0.08f;
  float target = t * 5.0f;
  shipV += (target - shipV) * 0.25f;
  shipX += shipV; shipX = clampf(shipX, 9, SCR_W - 9);
  // PLAY
  score++;
  speedMul = 1.0f + score / 1500.f; if (speedMul > 2.6f) speedMul = 2.6f;
  if (--spawnT <= 0) { spawn(); spawnT = (int)(rnd(18, 42) / (0.6f + speedMul * 0.4f)); if (spawnT < 6) spawnT = 6; }
  if (invul > 0) invul--;
  for (auto &m : mets) if (m.on) {
    m.x += m.vx; m.y += m.vy; m.ang += m.spin;
    if (m.y > SCR_H + m.r + 2) { m.on = false; continue; }
    float dx = m.x - shipX, dy = m.y - (SHIP_Y + 1);
    float rr = m.r * 0.82f + 5.0f;
    if (!invul && dx * dx + dy * dy < rr * rr) {
      m.on = false; spark(m.x, m.y, 14); spark(shipX, SHIP_Y, 10);
      if (--lives <= 0) { gameOver(); return; }
      invul = 80; sfx(200, 100); sfx(110, 140, false);
    }
  }
}

static void drawMeteor(const Met &m) {
  int cx = (int)m.x, cy = (int)m.y;
  int px[8], py[8];
  for (int i = 0; i < 8; i++) { float a = m.ang + i * 0.7854f, r = m.r * m.shape[i] / 100.f; px[i] = cx + (int)(cosf(a) * r); py[i] = cy + (int)(sinf(a) * r); }
  uint16_t fill = rgb(130, 110, 95), lt = rgb(175, 150, 125), dk = rgb(70, 58, 50);
  for (int i = 0; i < 8; i++) canvas.fillTriangle(cx, cy, px[i], py[i], px[(i + 1) & 7], py[(i + 1) & 7], (i < 3) ? lt : fill);
  for (int i = 0; i < 8; i++) canvas.drawLine(px[i], py[i], px[(i + 1) & 7], py[(i + 1) & 7], dk);
  if (m.r > 8) { canvas.fillCircle(cx + (int)(m.r * 0.25f * cosf(m.ang)), cy + (int)(m.r * 0.25f * sinf(m.ang)), m.r / 4, dk); }
}
static void drawShip(int x, int y, float bank, bool flame) {
  int w = 9 + (int)(bank * 0), sh = (int)(bank * 2);
  uint16_t body = rgb(210, 220, 235), dk = rgb(90, 100, 130), red = rgb(230, 60, 50);
  if (flame) { int f = 4 + (animT & 3) * 2; canvas.fillTriangle(x - 3, y + 6, x + 3, y + 6, x, y + 8 + f, rgb(255, 170, 40)); canvas.fillTriangle(x - 1, y + 6, x + 1, y + 6, x, y + 6 + f / 2, rgb(255, 240, 150)); }
  canvas.fillTriangle(x - w, y + 7, x, y - 2, x + w, y + 7, dk);                                       // ailes
  canvas.fillTriangle(x - 3 + sh, y + 8, x + sh, y - 11, x + 3 + sh, y + 8, body);                    // fuselage
  canvas.fillTriangle(x - 2 + sh, y - 4, x + sh, y - 11, x + 2 + sh, y - 4, red);
  canvas.fillCircle(x + sh, y - 1, 2, rgb(100, 200, 255));
  canvas.fillRect(x - w, y + 5, 3, 3, red); canvas.fillRect(x + w - 2, y + 5, 3, 3, red);
}

static void render() {
  canvas.fillScreen(rgb(4, 6, 20));
  for (auto &s : stars) { uint8_t b = 90 + (int)(s.v * 70); canvas.drawPixel((int)s.x, (int)s.y, rgb(b, b, b)); if (s.v > 1.5f) canvas.drawPixel((int)s.x, (int)s.y - 1, rgb(b / 2, b / 2, b / 2)); }
  for (auto &m : mets) if (m.on) drawMeteor(m);
  for (auto &p : sparks) if (p.life > 0) canvas.fillRect((int)p.x, (int)p.y, 2, 2, p.life > 12 ? rgb(255, 220, 120) : rgb(230, 90, 40));
  if (state != OVER && state != TITLE && (invul == 0 || (animT & 4))) drawShip((int)shipX, SHIP_Y, shipV / 5.0f, true);
  if (state == TITLE) drawShip(SCR_W / 2, 100, 0, true);
  if (state == PLAY || state == PAUSED || state == READY) {
    char b[16]; snprintf(b, sizeof b, "%lu", (unsigned long)(score / 10));
    txt(b, 6, 4, &fonts::Font2, TFT_WHITE);
    for (int i = 0; i < lives; i++) { int hx = SCR_W - 14 - i * 14; canvas.fillTriangle(hx - 4, hx * 0 + 14, hx, 4, hx + 4, 14, rgb(210, 220, 235)); }
  }
  if (state == TITLE) {
    txtO(L("METEORS","METEORES"), SCR_W / 2, 10, &fonts::Font4, rgb(255, 200, 60), rgb(90, 30, 0), textdatum_t::top_center);
    if (best > 0) { char b[24]; snprintf(b, sizeof b, L("best %lu","record %lu"), (unsigned long)best); txt(b, SCR_W / 2, 74, &fonts::Font2, rgb(255, 230, 120), textdatum_t::top_center); }
  }
  if (state == PAUSED) txtO("PAUSE", SCR_W / 2, 52, &fonts::Font4, TFT_WHITE, rgb(0, 0, 0), textdatum_t::top_center);
  if (state == OVER) {
    canvas.fillRoundRect(40, 28, 160, 70, 6, rgb(14, 18, 44)); canvas.drawRoundRect(40, 28, 160, 70, 6, rgb(120, 140, 220));
    txt(L("SHIP DESTROYED","VAISSEAU DETRUIT"), SCR_W / 2, 34, &fonts::Font2, rgb(255, 110, 90), textdatum_t::top_center);
    char b[40]; snprintf(b, sizeof b, L("score %lu   best %lu","score %lu   record %lu"), (unsigned long)(score / 10), (unsigned long)best);
    txt(b, SCR_W / 2, 56, &fonts::Font2, TFT_WHITE, textdatum_t::top_center);
  }
}

void loop() {
  uint32_t now = micros();
  if (last == 0) last = now;
  acc += now - last; last = now; if (acc > 100000) acc = 100000;
  bool a = M5.BtnA.wasPressed(), p = M5.BtnPWR.wasPressed();
  switch (state) {
    case TITLE: if (a) { reset(); state = PLAY; sfx(660, 40); } break;
        case PLAY: if (p) { state = PAUSED; sfx(440, 50); } break;
    case PAUSED: if (p || a) { state = PLAY; sfx(660, 50); } break;
    case OVER: if (a && overT > 40) { reset(); state = PLAY; sfx(660, 40); } break;
  }
  while (acc >= STEP_US) { if (state != PAUSED) step(); acc -= STEP_US; }
  render();
  bgm::run(8, state == PLAY);
  present(0, 0);
}

void icon(int x, int y) {
  canvas.fillRoundRect(x, y, 64, 64, 6, rgb(4, 6, 20));
  uint8_t sx[9] = {6, 18, 50, 58, 30, 12, 44, 55, 22}, sy[9] = {8, 40, 12, 36, 6, 22, 52, 56, 30};
  for (int i = 0; i < 9; i++) canvas.drawPixel(x + sx[i], y + sy[i], rgb(200, 200, 220));
  Met m{}; m.x = x + 44; m.y = y + 18; m.r = 11; m.ang = 0.4f; for (int i = 0; i < 8; i++) m.shape[i] = 70 + ((i * 53) % 30); drawMeteor(m);
  m.x = x + 16; m.y = y + 28; m.r = 6; m.ang = 1.0f; drawMeteor(m);
  animT = 0; drawShip(x + 32, y + 48, 0, true);
}

}  // namespace space
