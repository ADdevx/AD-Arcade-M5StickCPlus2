// ============================================================================
//  STACK - un bloc glisse, M5 (A) ou B = le poser sur la tour.
//  Ce qui depasse tombe dans le vide : le bloc retrecit. Rate completement = fin.
//  Pose parfaite (a 3 px pres) = pas de perte, 3 parfaits de suite = le bloc regrandit.
//  HAUT (PWR) = pause
// ============================================================================
#include "common.h"

namespace stack {

static const uint32_t STEP_US = 20000;
static const int BH = 9, START_W = 84, MAX_W = 96, MAXL = 220;
enum State { TITLE, PLAY, PAUSED, OVER };
static State state = TITLE;
static Preferences pr;
static uint32_t last = 0, acc = 0;

struct Layer { float x, w; uint8_t hue; };
static Layer LY[MAXL]; static int n = 0;                 // blocs poses (LY[0] = base)
static float mx, mw, mdir; static uint8_t mhue;         // bloc qui glisse
static float cam = 0;
static int combo = 0, perfectT = 0, endT = 0, animT = 0;
static float perfX, perfW; static int perfN;
static uint32_t best = 0;
struct Chunk { float x, y, w, vy; uint16_t col; bool on; }; static Chunk chunks[8];
struct Star { uint8_t x, y, b; }; static Star stars[40];

static uint16_t hsv(int h, float s, float v) {
  h %= 360; float c = v * s, x = c * (1 - fabsf(fmodf(h / 60.f, 2) - 1)), m = v - c, r, g, b;
  if (h < 60) { r = c; g = x; b = 0; } else if (h < 120) { r = x; g = c; b = 0; } else if (h < 180) { r = 0; g = c; b = x; }
  else if (h < 240) { r = 0; g = x; b = c; } else if (h < 300) { r = x; g = 0; b = c; } else { r = c; g = 0; b = x; }
  return rgb((int)((r + m) * 255), (int)((g + m) * 255), (int)((b + m) * 255));
}
static inline float layerY(int i) { return SCR_H - (i + 1) * BH + cam; }          // y ecran du haut du bloc i
static inline uint8_t hueOf(int i) { return (uint8_t)((i * 6) % 240); }              // teinte 0..239 -> x1.5 = 0..360

static void newBlock() {
  mhue = hueOf(n);
  mw = LY[n - 1].w;
  bool fromLeft = (n & 1) == 0;
  mx = fromLeft ? 0 : SCR_W - mw; mdir = fromLeft ? 1 : -1;
}
static float spd() { float m = dif(0.8f, 1.0f, 1.2f); float v = (1.7f + n * 0.05f) * m; return v > 5.0f * m ? 5.0f * m : v; }

static void reset() {
  n = 1; LY[0] = {(SCR_W - START_W) / 2.f, (float)START_W, hueOf(0)};
  combo = 0; perfectT = 0; endT = 0; animT = 0; cam = 0;
  for (auto &c : chunks) c.on = false;
  newBlock();
}
void begin() {
  pr.begin(dns("stack"), false); best = pr.getInt("best", 0);
  for (auto &s : stars) s = {(uint8_t)rnd(0, SCR_W - 1), (uint8_t)rnd(0, SCR_H - 1), (uint8_t)rnd(80, 200)};
  reset(); state = TITLE; last = 0; acc = 0;
}

static void addChunk(float x, float y, float w, uint16_t col) {
  if (w < 1) return;
  for (auto &c : chunks) if (!c.on) { c = {x, y, w, 0.5f, col, true}; return; }
}
static void gameOver() {
  state = OVER; endT = 0;
  uint32_t sc = n - 1;
  trophy::record(trophy::T_STACK, sc); if (sc > best) { best = sc; pr.putInt("best", best); }
  sfx(300, 120); sfx(120, 320, false);
}

static void drop() {
  const Layer &t = LY[n - 1];
  float y = layerY(n);
  uint16_t col = hsv(mhue * 3 / 2, 0.55f, 0.95f);
  float left = fmaxf(mx, t.x), right = fminf(mx + mw, t.x + t.w), ov = right - left;
  if (ov <= 0) {                                 // rate completement : le bloc entier tombe
    addChunk(mx, y, mw, col); sfx(200, 100); sfx(120, 250, false); gameOver(); return;
  }
  if (fabsf(mx - t.x) <= 3.0f) {                 // pose parfaite
    mx = t.x; ov = mw = fminf(mw, t.w); combo++; left = mx;
    if (combo >= 3) { float nw = fminf(MAX_W, mw + 3); float grow = nw - mw; mx -= grow / 2; if (mx < 0) mx = 0; if (mx + nw > SCR_W) mx = SCR_W - nw; mw = nw; ov = nw; left = mx; }
    perfectT = 18; perfX = left; perfW = ov; perfN = n;
    int cb = combo > 8 ? 8 : combo; sfx(880 + cb * 110, 50); sfx(1320 + cb * 110, 70, false);
  } else {                                       // on coupe ce qui depasse
    combo = 0;
    if (mx < t.x) addChunk(mx, y, t.x - mx, col);                       // depasse a gauche
    if (mx + mw > t.x + t.w) addChunk(t.x + t.w, y, mx + mw - (t.x + t.w), col);   // depasse a droite
    sfx(220, 40);
  }
  if (n < MAXL) { LY[n] = {left, ov, mhue}; n++; }
  else { memmove(&LY[0], &LY[MAXL / 2], sizeof(Layer) * (MAXL / 2)); n = MAXL / 2; LY[n++] = {left, ov, mhue}; }   // tres longue partie : on recycle
  newBlock();
}

static void step() {
  animT++;
  for (auto &c : chunks) if (c.on) { c.vy += 0.35f; c.y += c.vy; if (c.y > SCR_H + 12) c.on = false; }
  if (perfectT > 0) perfectT--;
  float camT = fmaxf(0, (n + 1) * BH - (SCR_H - 42));
  cam += (camT - cam) * 0.12f;
  if (state == TITLE) { mx += mdir * 1.8f; if (mx < 0) { mx = 0; mdir = 1; } if (mx + mw > SCR_W) { mx = SCR_W - mw; mdir = -1; } return; }
  if (state == OVER) { endT++; return; }
  mx += mdir * spd();
  if (mx < 0) { mx = 0; mdir = 1; }
  if (mx + mw > SCR_W) { mx = SCR_W - mw; mdir = -1; }
}

static void drawBlock(float x, float y, float w, uint16_t col) {
  int ix = (int)(x + 0.5f), iy = (int)(y + 0.5f), iw = (int)(w + 0.5f);
  if (iw < 1) return;
  canvas.fillRect(ix, iy, iw, BH, col);
  canvas.drawFastHLine(ix, iy, iw, rgb(255, 255, 255));
  canvas.fillRect(ix, iy + BH - 2, iw, 2, rgb(0, 0, 0));
  canvas.drawRect(ix, iy, iw, BH, rgb(20, 20, 40));
}
static uint16_t lerp565(int r1, int g1, int b1, int r2, int g2, int b2, float t) { return rgb(r1 + (int)((r2 - r1) * t), g1 + (int)((g2 - g1) * t), b1 + (int)((b2 - b1) * t)); }

static void render() {
  // ciel : devient de plus en plus sombre avec la hauteur
  float h = fminf(1.f, n / 40.f);
  for (int y = 0; y < SCR_H; y += 5) {
    float t = y / (float)SCR_H;
    uint16_t c = lerp565(int(40 - h * 34 + t * 10), int(60 - h * 52 + t * 40), int(120 - h * 96 + t * 50), int(18 - h * 14), int(20 - h * 16), int(50 - h * 40), 1 - t);
    canvas.fillRect(0, y, SCR_W, 5, c);
  }
  if (n > 8) for (auto &s : stars) { int sy = ((int)s.y + (int)(cam * 0.25f)) % SCR_H; uint8_t b = (uint8_t)(s.b * fminf(1.f, (n - 8) / 12.f)); canvas.drawPixel(s.x, sy, rgb(b, b, b)); }
  // sol (visible au debut)
  if (cam < SCR_H) canvas.fillRect(0, (int)(SCR_H + cam - 1), SCR_W, 4, rgb(20, 24, 40));
  // tour
  for (int i = 0; i < n; i++) { float y = layerY(i); if (y > SCR_H || y < -BH) continue; drawBlock(LY[i].x, y, LY[i].w, hsv(LY[i].hue * 3 / 2, 0.55f, 0.95f)); }
  // effet "parfait"
  if (perfectT > 0 && perfN > 0) { float y = layerY(perfN); int k = 18 - perfectT; canvas.drawRect((int)perfX - k, (int)y - k, (int)perfW + 2 * k, BH + 2 * k, TFT_WHITE); }
  // morceaux qui tombent
  for (auto &c : chunks) if (c.on) drawBlock(c.x, c.y, c.w, c.col);
  // bloc qui glisse
  if (state != OVER) drawBlock(mx, layerY(n), mw, hsv(mhue * 3 / 2, 0.55f, 0.95f));
  // infos
  char b[32];
  if (state != TITLE) { snprintf(b, sizeof b, "%d", n - 1); txtO(b, SCR_W / 2, 2, &fonts::Font4, TFT_WHITE, rgb(10, 10, 30), textdatum_t::top_center); }
  if (state != TITLE && combo >= 2) { snprintf(b, sizeof b, L("PERFECT x%d","PARFAIT x%d"), combo); txtO(b, SCR_W / 2, 26, &fonts::Font2, rgb(255, 230, 90), rgb(60, 30, 0), textdatum_t::top_center); }
  if (state == TITLE) {
    canvas.fillRoundRect(20, 14, 200, 52, 7, rgb(10, 12, 32)); canvas.drawRoundRect(20, 14, 200, 52, 7, rgb(120, 140, 230));
    txt("STACK", SCR_W / 2, 18, &fonts::Font4, rgb(255, 210, 80), textdatum_t::top_center, 1.2f);
    if (best > 0) { snprintf(b, sizeof b, L("best %lu","record %lu"), (unsigned long)best); txt(b, SCR_W / 2, 124, &fonts::Font2, rgb(255, 230, 120), textdatum_t::top_center); }
  }
  if (state == PAUSED) { canvas.fillRoundRect(80, 50, 80, 28, 5, rgb(10, 12, 32)); txt("PAUSE", SCR_W / 2, 54, &fonts::Font4, TFT_WHITE, textdatum_t::top_center); }
  if (state == OVER) {
    canvas.fillRoundRect(40, 34, 160, 62, 6, rgb(10, 12, 32)); canvas.drawRoundRect(40, 34, 160, 62, 6, rgb(230, 80, 70));
    txt("GAME OVER", SCR_W / 2, 38, &fonts::Font4, rgb(230, 80, 70), textdatum_t::top_center);
    snprintf(b, sizeof b, L("%d blocks   best %lu","%d blocs   record %lu"), n - 1, (unsigned long)best); txt(b, SCR_W / 2, 66, &fonts::Font2, TFT_WHITE, textdatum_t::top_center);
  }
}

void loop() {
  uint32_t now = micros();
  if (last == 0) last = now;
  acc += now - last; last = now; if (acc > 100000) acc = 100000;
  bool a = M5.BtnA.wasPressed() || M5.BtnB.wasPressed(), p = M5.BtnPWR.wasPressed();
  switch (state) {
    case TITLE: if (a) { reset(); state = PLAY; sfx(660, 40); } break;
    case PLAY: if (p) { state = PAUSED; sfx(440, 50); } else if (a) drop(); break;
    case PAUSED: if (p || a) { state = PLAY; sfx(660, 50); } break;
    case OVER: if (a && endT > 40) { reset(); state = PLAY; sfx(660, 40); } break;
  }
  while (acc >= STEP_US) { if (state != PAUSED) step(); acc -= STEP_US; }
  render();
  bgm::run(3, state == PLAY);
  present(0, 0);
}

void icon(int x, int y) {
  canvas.fillRoundRect(x, y, 64, 64, 6, rgb(40, 60, 130));
  canvas.fillRect(x, y + 56, 64, 8, rgb(20, 24, 40));
  static const int W[5] = {40, 34, 26, 26, 18}, X[5] = {12, 15, 18, 18, 22};
  for (int i = 0; i < 5; i++) { int by = y + 56 - (i + 1) * 9; uint16_t c = hsv(i * 55, 0.55f, 0.95f); canvas.fillRect(x + X[i], by, W[i], 9, c); canvas.drawFastHLine(x + X[i], by, W[i], TFT_WHITE); canvas.drawRect(x + X[i], by, W[i], 9, rgb(20, 20, 40)); }
  canvas.fillRect(x + 36, y + 4, 22, 9, hsv(280, 0.55f, 0.95f)); canvas.drawRect(x + 36, y + 4, 22, 9, rgb(20, 20, 40));
  canvas.fillRect(x + 50, y + 22, 10, 9, hsv(280, 0.55f, 0.95f)); canvas.drawRect(x + 50, y + 22, 10, 9, rgb(20, 20, 40));   // morceau coupe qui tombe
}

}  // namespace stack
