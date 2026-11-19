// ============================================================================
//  LABYRINTHE A BILLE - penche le M5 pour faire rouler la bille jusqu'a la sortie verte
//  M5 (A) = jouer ; B (cote) = recalibrer ; HAUT (PWR) = pause
// ============================================================================
#include "common.h"

namespace maze {

static const uint32_t STEP_US = 20000;
static const int COLS = 16, ROWS = 8, CELL = 15, WT = 2;     // 16*15 = 240 ; 8*15 = 120 ; bande du bas = infos
static const float BALL_R = 4.0f;
enum State { TITLE, READY, PLAY, PAUSED, WIN };
static State state = TITLE;
static Preferences pr;
static uint32_t last = 0, acc = 0;
static uint8_t wallR[ROWS][COLS], wallB[ROWS][COLS];       // mur a droite / en bas de chaque case
struct Rect { int16_t x, y, w, h; };
static Rect walls[COLS * ROWS * 2 + 8]; static int nWalls = 0;
struct Hole { int cx, cy; }; static Hole holes[8]; static int nHoles = 0;
static float bx, by, vx, vy;
static int level = 1, bestLevel = 1, readyT = 0, winT = 0, fallT = 0, animT = 0;
static uint32_t levelStart = 0, elapsed = 0;

static void addWall(int x, int y, int w, int h) { if (nWalls < (int)(sizeof(walls) / sizeof(walls[0]))) walls[nWalls++] = {(int16_t)x, (int16_t)y, (int16_t)w, (int16_t)h}; }

static void generate() {
  static uint8_t vis[ROWS][COLS];
  memset(wallR, 1, sizeof wallR); memset(wallB, 1, sizeof wallB); memset(vis, 0, sizeof vis);
  int stack[COLS * ROWS][2], sp = 0;
  stack[sp][0] = 0; stack[sp][1] = 0; sp++; vis[0][0] = 1;
  while (sp > 0) {
    int cx = stack[sp - 1][0], cy = stack[sp - 1][1];
    int dirs[4][2], n = 0;
    if (cx > 0 && !vis[cy][cx - 1]) { dirs[n][0] = -1; dirs[n++][1] = 0; }
    if (cx < COLS - 1 && !vis[cy][cx + 1]) { dirs[n][0] = 1; dirs[n++][1] = 0; }
    if (cy > 0 && !vis[cy - 1][cx]) { dirs[n][0] = 0; dirs[n++][1] = -1; }
    if (cy < ROWS - 1 && !vis[cy + 1][cx]) { dirs[n][0] = 0; dirs[n++][1] = 1; }
    if (!n) { sp--; continue; }
    int k = rnd(0, n - 1), dx = dirs[k][0], dy = dirs[k][1], nx = cx + dx, ny = cy + dy;
    if (dx == 1) wallR[cy][cx] = 0; else if (dx == -1) wallR[cy][nx] = 0;
    else if (dy == 1) wallB[cy][cx] = 0; else wallB[ny][cx] = 0;
    vis[ny][nx] = 1; stack[sp][0] = nx; stack[sp][1] = ny; sp++;
  }
  // quelques passages en plus pour que ce soit moins lineaire
  for (int i = 0; i < 6 + level; i++) {
    int cx = rnd(0, COLS - 2), cy = rnd(0, ROWS - 2);
    if (rnd(0, 1)) wallR[cy][cx] = 0; else wallB[cy][cx] = 0;
  }
  nWalls = 0;
  addWall(0, 0, COLS * CELL, WT); addWall(0, ROWS * CELL - WT, COLS * CELL, WT);
  addWall(0, 0, WT, ROWS * CELL); addWall(COLS * CELL - WT, 0, WT, ROWS * CELL);
  for (int cy = 0; cy < ROWS; cy++) for (int cx = 0; cx < COLS; cx++) {
    if (cx < COLS - 1 && wallR[cy][cx]) addWall((cx + 1) * CELL - WT / 2, cy * CELL, WT, CELL + 1);
    if (cy < ROWS - 1 && wallB[cy][cx]) addWall(cx * CELL, (cy + 1) * CELL - WT / 2, CELL + 1, WT);
  }
  // chemin le plus court depart -> sortie (BFS) : on n'y met jamais de trou, sinon le niveau serait impossible
  static int8_t par[ROWS][COLS]; static uint8_t onPath[ROWS][COLS];
  memset(par, -1, sizeof par); memset(onPath, 0, sizeof onPath);
  { int q[COLS * ROWS][2], qh = 0, qt = 0; q[qt][0] = 0; q[qt++][1] = 0; par[0][0] = 4;
    while (qh < qt) {
      int cx = q[qh][0], cy = q[qh][1]; qh++;
      if (cx < COLS - 1 && !wallR[cy][cx] && par[cy][cx + 1] < 0) { par[cy][cx + 1] = 2; q[qt][0] = cx + 1; q[qt++][1] = cy; }
      if (cx > 0 && !wallR[cy][cx - 1] && par[cy][cx - 1] < 0) { par[cy][cx - 1] = 0; q[qt][0] = cx - 1; q[qt++][1] = cy; }
      if (cy < ROWS - 1 && !wallB[cy][cx] && par[cy + 1][cx] < 0) { par[cy + 1][cx] = 3; q[qt][0] = cx; q[qt++][1] = cy + 1; }
      if (cy > 0 && !wallB[cy - 1][cx] && par[cy - 1][cx] < 0) { par[cy - 1][cx] = 1; q[qt][0] = cx; q[qt++][1] = cy - 1; }
    }
    int cx = COLS - 1, cy = ROWS - 1;      // remonte : 0 = vient de gauche, 1 = du haut, 2 = de droite, 3 = du bas
    while (!(cx == 0 && cy == 0)) { onPath[cy][cx] = 1; int d = par[cy][cx]; if (d == 0) cx++; else if (d == 2) cx--; else if (d == 1) cy++; else cy--; }
    onPath[0][0] = 1; }
  nHoles = 0;
  int want = level - 1; if (want > 7) want = 7;
  for (int tries = 0; nHoles < want && tries < 100; tries++) {
    int cx = rnd(0, COLS - 1), cy = rnd(0, ROWS - 1);
    if (cx + cy < 3 || (cx >= COLS - 2 && cy >= ROWS - 2) || onPath[cy][cx]) continue;
    bool dup = false; for (int i = 0; i < nHoles; i++) if (holes[i].cx == cx && holes[i].cy == cy) dup = true;
    if (dup) continue;
    holes[nHoles++] = {cx, cy};
  }
}
static void placeBall() { bx = CELL / 2; by = CELL / 2; vx = vy = 0; fallT = 0; }
static void newLevel() { generate(); placeBall(); levelStart = millis(); elapsed = 0; }

void begin() {
  pr.begin("maze", false); bestLevel = pr.getInt("lvl", 1);
  tilt::load();
  level = 1; state = TITLE; generate(); placeBall(); last = 0; acc = 0; animT = 0;
}

static void moveAxis(bool horiz, float d) {
  if (horiz) bx += d; else by += d;
  for (int i = 0; i < nWalls; i++) {
    const Rect &r = walls[i];
    float cx = clampf(bx, r.x, r.x + r.w), cy = clampf(by, r.y, r.y + r.h);
    float dx = bx - cx, dy = by - cy;
    if (dx * dx + dy * dy < BALL_R * BALL_R) {
      if (horiz) { bx = (d > 0) ? r.x - BALL_R : r.x + r.w + BALL_R; vx = -vx * 0.3f; }
      else       { by = (d > 0) ? r.y - BALL_R : r.y + r.h + BALL_R; vy = -vy * 0.3f; }
    }
  }
}

static void step() {
  animT++;
  if (state == TITLE || state == WIN) { if (state == WIN) winT++; return; }
  tilt::update();
  if (fallT > 0) { if (--fallT == 0) placeBall(); return; }
  float tx = tilt::x(), ty = -tilt::y();
  if (fabsf(tx) < 0.06f) tx = 0; if (fabsf(ty) < 0.06f) ty = 0;
  vx += tx * 0.20f; vy += ty * 0.20f;
  vx *= 0.96f; vy *= 0.96f;
  vx = clampf(vx, -3.5f, 3.5f); vy = clampf(vy, -3.5f, 3.5f);
  for (int s = 0; s < 2; s++) { moveAxis(true, vx * 0.5f); moveAxis(false, vy * 0.5f); }
  elapsed = millis() - levelStart;
  for (int i = 0; i < nHoles; i++) {
    float dx = bx - (holes[i].cx * CELL + CELL / 2), dy = by - (holes[i].cy * CELL + CELL / 2);
    if (dx * dx + dy * dy < 3.2f * 3.2f) { fallT = 40; vx = vy = 0; bx = holes[i].cx * CELL + CELL / 2; by = holes[i].cy * CELL + CELL / 2; sfx(300, 80); sfx(120, 200, false); return; }
  }
  float gx = (COLS - 1) * CELL + CELL / 2, gy = (ROWS - 1) * CELL + CELL / 2;
  if ((bx - gx) * (bx - gx) + (by - gy) * (by - gy) < 4.5f * 4.5f) {
    state = WIN; winT = 0; sfx(988, 80); sfx(1318, 80, false); sfx(1760, 160, false);
    trophy::record(trophy::T_MAZE, level + 1); if (level + 1 > bestLevel) { bestLevel = level + 1; pr.putInt("lvl", bestLevel); }
  }
}

static void render() {
  canvas.fillScreen(rgb(24, 28, 40));
  canvas.fillRect(0, 0, COLS * CELL, ROWS * CELL, rgb(70, 90, 120));
  for (int cy = 0; cy < ROWS; cy++) for (int cx = 0; cx < COLS; cx++) if (((cx + cy) & 1) == 0) canvas.fillRect(cx * CELL, cy * CELL, CELL, CELL, rgb(76, 98, 130));
  // sortie
  int gx = (COLS - 1) * CELL + CELL / 2, gy = (ROWS - 1) * CELL + CELL / 2;
  canvas.fillCircle(gx, gy, 5, rgb(30, 220, 90)); canvas.fillCircle(gx, gy, 2, rgb(10, 80, 30));
  // trous
  for (int i = 0; i < nHoles; i++) { int hx = holes[i].cx * CELL + CELL / 2, hy = holes[i].cy * CELL + CELL / 2; canvas.fillCircle(hx, hy, 5, rgb(5, 5, 10)); canvas.drawCircle(hx, hy, 5, rgb(40, 40, 60)); }
  for (int i = 0; i < nWalls; i++) { const Rect &r = walls[i]; canvas.fillRect(r.x, r.y, r.w, r.h, rgb(235, 225, 190)); }
  // bille
  int ix = (int)bx, iy = (int)by; int rad = fallT > 0 ? (int)(BALL_R * fallT / 40.f) : (int)BALL_R;
  if (state != TITLE && rad > 0) {
    canvas.fillCircle(ix + 1, iy + 1, rad, rgb(30, 40, 60));
    canvas.fillCircle(ix, iy, rad, rgb(220, 60, 50)); if (rad > 2) canvas.fillCircle(ix - 1, iy - 1, 1, rgb(255, 200, 190));
  }
  // infos
  char b[48]; snprintf(b, sizeof b, L("LVL %d","NIV %d"), level); txt(b, 4, ROWS * CELL + 2, &fonts::Font0, TFT_WHITE);
  snprintf(b, sizeof b, "%02lu:%02lu", (unsigned long)(elapsed / 60000), (unsigned long)((elapsed / 1000) % 60)); txt(b, SCR_W / 2, ROWS * CELL + 2, &fonts::Font0, rgb(255, 230, 120), textdatum_t::top_center);
  snprintf(b, sizeof b, "max %d", bestLevel); txt(b, SCR_W - 4, ROWS * CELL + 2, &fonts::Font0, rgb(150, 200, 255), textdatum_t::top_right);
  if (state == TITLE) {
    canvas.fillRoundRect(20, 22, 200, 76, 6, rgb(14, 18, 34)); canvas.drawRoundRect(20, 22, 200, 76, 6, rgb(235, 225, 190));
    txt(L("MAZE","LABYRINTHE"), SCR_W / 2, 28, &fonts::Font4, rgb(255, 210, 80), textdatum_t::top_center);
  }
  if (state == PAUSED) { canvas.fillRoundRect(80, 48, 80, 28, 5, rgb(14, 18, 34)); txt("PAUSE", SCR_W / 2, 52, &fonts::Font4, TFT_WHITE, textdatum_t::top_center); }
  if (state == WIN) {
    canvas.fillRoundRect(40, 28, 160, 66, 6, rgb(14, 18, 34)); canvas.drawRoundRect(40, 28, 160, 66, 6, rgb(30, 220, 90));
    txt(L("WELL DONE!","BRAVO !"), SCR_W / 2, 32, &fonts::Font4, rgb(30, 220, 90), textdatum_t::top_center);
    snprintf(b, sizeof b, L("level %d in %lu s","niveau %d en %lu s"), level, (unsigned long)(elapsed / 1000)); txt(b, SCR_W / 2, 60, &fonts::Font2, TFT_WHITE, textdatum_t::top_center);
  }
}

void loop() {
  uint32_t now = micros();
  if (last == 0) last = now;
  acc += now - last; last = now; if (acc > 100000) acc = 100000;
  bool a = M5.BtnA.wasPressed(), p = M5.BtnPWR.wasPressed();
  switch (state) {
    case TITLE: if (a) { level = 1; newLevel(); state = PLAY; sfx(660, 40); } break;
        case PLAY: if (p) { state = PAUSED; sfx(440, 50); } break;
    case PAUSED: if (p || a) { state = PLAY; sfx(660, 50); levelStart = millis() - elapsed; } break;
    case WIN: if (a && winT > 40) { level++; newLevel(); state = PLAY; sfx(660, 40); } break;
  }
  while (acc >= STEP_US) { if (state != PAUSED) step(); acc -= STEP_US; }
  render();
  bgm::run(9, state == PLAY);
  present(0, 0);
}

void icon(int x, int y) {
  canvas.fillRoundRect(x, y, 64, 64, 6, rgb(70, 90, 120));
  uint16_t w = rgb(235, 225, 190);
  canvas.drawRect(x + 3, y + 3, 58, 58, w);
  canvas.drawFastHLine(x + 3, y + 18, 34, w); canvas.drawFastVLine(x + 37, y + 18, 24, w);
  canvas.drawFastHLine(x + 18, y + 34, 34, w); canvas.drawFastVLine(x + 18, y + 34, 18, w);
  canvas.drawFastHLine(x + 18, y + 48, 24, w); canvas.drawFastVLine(x + 50, y + 3, 20, w);
  canvas.fillCircle(x + 11, y + 11, 4, rgb(220, 60, 50)); canvas.fillCircle(x + 10, y + 10, 1, rgb(255, 200, 190));
  canvas.fillCircle(x + 52, y + 52, 4, rgb(30, 220, 90));
  canvas.fillCircle(x + 28, y + 26, 4, rgb(5, 5, 10));
}

}  // namespace maze
