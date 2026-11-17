// ============================================================================
//  AD ARCADE - M5StickC Plus2
//  Menu facon console + jeux. Menu : B (cote) = suivant, HAUT (PWR) = precedent, M5 (A) = lancer
//  Dans un jeu : maintenir HAUT (PWR) 1,5 s = retour au menu
// ============================================================================
#include "common.h"

M5Canvas canvas(&M5.Display);

int  g_bright = 2;
bool g_sound = true;
bool g_music = true;
int  g_sleepIdx = 1;
int  g_lang = 0;                              // 0 = English, 1 = Francais
bool g_quit = false;
static const int BRI[5] = {30, 70, 120, 180, 255};
static const uint32_t SLEEP_MS[5] = {30000, 60000, 120000, 300000, 0};
static Preferences mp;

void applyBrightness() { M5.Display.setBrightness(BRI[g_bright]); }
void saveSettings() { mp.putInt("bri", g_bright); mp.putBool("snd", g_sound); mp.putBool("mus", g_music); mp.putInt("slp", g_sleepIdx); mp.putInt("lang", g_lang); }
void present(int ox, int oy) {
  static float z = -1;
  if (z < 0) { int w = M5.Display.width(), h = M5.Display.height(); if (w < h) { int t = w; w = h; h = t; } z = (w >= SCR_W && h >= SCR_H) ? 0 : fminf((float)w / SCR_W, (float)h / SCR_H); }
  if (z == 0) canvas.pushSprite(ox, oy);
  else canvas.pushRotateZoom(&M5.Display, M5.Display.width() / 2.0f, M5.Display.height() / 2.0f, 0, z, z);   // petit ecran : reduction, bandes noires si besoin
}

static bool g_pwrHold = false;   // vrai une frame quand l'utilisateur demande "retour au menu" (PWR maintenu ou A+B maintenus)

// M5.update() + corrections de boutons selon l'appareil :
//  - StickC / StickC Plus / StickS3 : le bouton PWR est lu par le circuit d'alimentation (AXP192 / M5PM1). La bibliotheque ne
//    donne alors que wasClicked()/wasHold() : wasPressed()/isPressed()/pressedFor() restent faux. On les recree ici
//    (un clic = appui virtuel de 120 ms). Le StickS3 ne signale jamais "maintenu" : on utilise donc aussi A+B.
//  - Nesso N1 : pas de 3e bouton, un doigt sur l'ecran joue le role de PWR.
//  - Tous : A+B maintenus ~1,2 s = retour au menu (marche meme si PWR ne peut pas etre maintenu).
void btnUpdate() {
  M5.update();
  uint32_t now = millis();
  g_pwrHold = false;
#if defined(CONFIG_IDF_TARGET_ESP32C6)
  M5.BtnPWR.setRawState(now, M5.Touch.getCount() > 0);
#else
  bool pmicBtn = false;
#if defined(CONFIG_IDF_TARGET_ESP32S3)
  pmicBtn = true;
#else
  { auto bd = M5.getBoard(); pmicBtn = (bd == m5::board_t::board_M5StickC || bd == m5::board_t::board_M5StickCPlus); }
#endif
  if (pmicBtn) {
    static uint32_t until = 0;
    if (M5.BtnPWR.wasHold()) g_pwrHold = true;
    if (M5.BtnPWR.wasClicked() || M5.BtnPWR.wasHold()) until = now + 120;
    M5.BtnPWR.setRawState(now, now < until);
  }
#endif
  static uint32_t chord = 0;
  if (M5.BtnA.isPressed() && M5.BtnB.isPressed()) { if (!chord) chord = now; else if (now - chord > 1200) { g_pwrHold = true; chord = 0; } }
  else chord = 0;
}

void sfx(int freq, int ms, bool stopPrev) { if (g_sound) { bgm::onSfx(ms); M5.Speaker.tone(freq, ms, -1, stopPrev); } }

struct GameDef { const char* en; const char* fr; void (*begin)(); void (*loop)(); void (*icon)(int, int); };
static const GameDef GAMES[] = {
  {"CHROME DINO",    "CHROME DINO",    dino::begin,     dino::loop,     dino::icon},
  {"FLAP BIRD",      "FLAP BIRD",      flap::begin,     flap::loop,     flap::icon},
  {"METEORS",        "METEORES",       space::begin,    space::loop,    space::icon},
  {"MAZE",           "LABYRINTHE",     maze::begin,     maze::loop,     maze::icon},
  {"BREAKOUT",       "CASSE-BRIQUES",  breakout::begin, breakout::loop, breakout::icon},
  {"INVADERS",       "INVADERS",       invaders::begin, invaders::loop, invaders::icon},
  {"SLALOM",         "SLALOM",         ski::begin,      ski::loop,      ski::icon},
  {"STACK",          "STACK",          stack::begin,    stack::loop,    stack::icon},
  {"RACING",         "COURSE",         race::begin,     race::loop,     race::icon},
  {"FLIGHT",         "AVION",          sky::begin,      sky::loop,      sky::icon},
  {"RIVER",          "RIVIERE",        river::begin,    river::loop,    river::icon},
  {"FISH",           "POISSON",        fish::begin,     fish::loop,     fish::icon},
  {"TETRIS",         "TETRIS",         tetris::begin,   tetris::loop,   tetris::icon},
  {"SNAKE",          "SNAKE",          snake::begin,    snake::loop,    snake::icon},
  {"LUNAR LANDER",   "ALUNISSAGE",     lander::begin,   lander::loop,   lander::icon},
  {"MUSIC",          "MUSIQUE",        music::begin,    music::loop,    music::icon},
  {"SETTINGS",       "REGLAGES",       settings::begin, settings::loop, settings::icon},
};
static const int NGAMES = sizeof(GAMES) / sizeof(GAMES[0]);
static int sel = 0, running = -1;
static float slide = 0;                       // animation de defilement (en tuiles)
static uint32_t lastAct = 0;                  // dernier appui (pour l'ecran de veille)
static int saver = 0;                         // 0 = normal, 1 = veille (animation), 2 = ecran eteint
static int batLevel = 100; static bool batChg = false; static uint32_t batT = 0;

// ----------------------------------------------------------------------------- menu
static void dim(int x, int y) { for (int j = 0; j < 64; j += 2) canvas.drawFastHLine(x, y + j, 64, rgb(10, 10, 18)); }

static void drawBattery(int x, int y, int lvl, bool chg) {            // petite pile facon telephone + pourcentage
  uint16_t col = lvl <= 15 ? rgb(235, 60, 60) : (lvl <= 35 ? rgb(250, 190, 40) : rgb(90, 220, 110));
  canvas.drawRoundRect(x, y, 22, 11, 3, rgb(220, 224, 240)); canvas.fillRect(x + 22, y + 3, 2, 5, rgb(220, 224, 240));
  int w = (lvl * 18) / 100; if (w < 1 && lvl > 0) w = 1;
  canvas.fillRoundRect(x + 2, y + 2, w, 7, 2, col);
  if (chg) { canvas.fillTriangle(x + 12, y + 1, x + 7, y + 6, x + 11, y + 6, rgb(255, 255, 255)); canvas.fillTriangle(x + 10, y + 5, x + 14, y + 5, x + 9, y + 10, rgb(255, 255, 255)); }
  char b[8]; snprintf(b, sizeof b, "%d%%", lvl); txt(b, x + 28, y + 1, &fonts::Font0, rgb(220, 224, 240));
}

static uint16_t rainbow(int h) {
  h &= 255; int r, g, b;
  if (h < 85) { r = 255 - h * 3; g = h * 3; b = 0; } else if (h < 170) { h -= 85; r = 0; g = 255 - h * 3; b = h * 3; } else { h -= 170; r = h * 3; g = 0; b = 255 - h * 3; }
  return rgb(r, g, b);
}
struct Star { float x, y, v; };
static Star stars[40]; static bool starsInit = false;
static void initStars() { for (auto &s : stars) s = {(float)rnd(0, SCR_W), (float)rnd(0, SCR_H), 0.15f + (float)rnd(0, 100) / 120.0f}; starsInit = true; }

static uint32_t toastT = 0; static bool adapted = false;                                    // message "FLAT / UPRIGHT" apres une (re)stabilisation
static const uint16_t ACC_RGB[17][3] = {                       // couleur d'ambiance de chaque entree
  {120,200,120},{250,210,60},{120,160,255},{110,220,200},{250,120,90},{120,230,130},{90,190,255},{255,170,70},{240,70,70},{90,170,255},{70,200,230},{70,150,255},{170,90,240},{90,220,90},{200,200,220},{255,110,190},{170,176,200}};
static uint16_t accOf(int idx) { const uint16_t* c = ACC_RGB[idx % 17]; return rgb(c[0], c[1], c[2]); }

static void drawBackdrop(uint16_t acc) {                       // ciel degrade + aurore + etoiles + montagnes + sol en grille
  uint32_t t = millis();
  for (int y = 0; y < 84; y += 3) canvas.fillRect(0, y, SCR_W, 3, mixc(mixc(rgb(8, 8, 30), acc, 22), mixc(rgb(66, 26, 92), acc, 40), y * 256 / 84));
  for (int i = 0; i < 3; i++) {                                // bandes d'aurore ondulantes
    for (int x = 0; x < SCR_W; x += 4) {
      int yy = 26 + i * 14 + (int)(sinf(x * 0.035f + t * 0.0012f * (i + 1) + i * 2.0f) * 9);
      canvas.fillRect(x, yy, 4, 5 + i, mixc(rgb(14, 12, 40), mixc(acc, rainbow((int)(t / 40) + i * 40 + x / 3), 120), 80 + i * 20));
    }
  }
  if (!starsInit) initStars();
  for (auto &s2 : stars) {
    s2.x -= s2.v * 0.6f; if (s2.x < 0) { s2.x += SCR_W; s2.y = rnd(0, 80); }
    int tw = ((int)(t / 130) + (int)s2.x) % 9 == 0;
    uint16_t c = tw ? rgb(255, 255, 255) : (s2.v > 0.8f ? rgb(230, 230, 255) : (s2.v > 0.45f ? rgb(170, 170, 220) : rgb(100, 100, 150)));
    canvas.drawPixel((int)s2.x, (int)s2.y % 82, c); if (s2.v > 0.8f) canvas.drawPixel((int)s2.x + 1, (int)s2.y % 82, c);
  }
  for (int layer = 0; layer < 2; layer++) {                    // montagnes lointaines (parallaxe)
    uint16_t mc = layer ? mixc(rgb(34, 18, 66), acc, 26) : mixc(rgb(24, 14, 52), acc, 14);
    for (int x = 0; x < SCR_W; x += 2) {
      float wx = x + t * (layer ? 0.010f : 0.004f);
      int h = (int)(10 + layer * 6 + sinf(wx * 0.045f + layer * 2.2f) * 7 + sinf(wx * 0.11f + layer) * 3);
      canvas.fillRect(x, 84 - h, 2, h + 1, mc);
    }
  }
  canvas.fillRect(0, 84, SCR_W, 19, rgb(20, 10, 44));          // sol
  for (int i = 0; i < 7; i++) { float f = (float)((i * 16 + (t / 55) % 16)) / 112.0f; int y = 84 + (int)(f * f * 24); if (y < 103) canvas.drawFastHLine(0, y, SCR_W, mixc(rgb(60, 30, 110), acc, 70)); }
  for (int i = -8; i <= 8; i++) canvas.drawLine(SCR_W / 2 + i * 6, 84, SCR_W / 2 + i * 26, 103, mixc(rgb(50, 26, 96), acc, 60));
  canvas.drawFastHLine(0, 84, SCR_W, mixc(rgb(120, 70, 200), acc, 120));
}

static void haloRays(int cx, int cy, uint16_t acc, uint32_t t) {   // rayons qui tournent derriere l'icone choisie
  float a0 = t * 0.0006f;
  for (int i = 0; i < 12; i++) {
    float a1 = a0 + i * 0.5236f, a2 = a1 + 0.2618f;
    canvas.fillTriangle(cx, cy, cx + (int)(cosf(a1) * 130), cy + (int)(sinf(a1) * 130), cx + (int)(cosf(a2) * 130), cy + (int)(sinf(a2) * 130), mixc(rgb(26, 16, 60), acc, 64));
  }
}

static void drawMenu() {
  uint32_t t = millis();
  float fs = slide;                                            // couleur d'ambiance : fondu pendant le defilement
  uint16_t acc = mixc(accOf(sel), accOf(sel - (slide > 0 ? 1 : (slide < 0 ? -1 : 0)) + NGAMES), (int)(fabsf(fs) * 200));
  drawBackdrop(acc);
  haloRays(SCR_W / 2, 56, acc, t);
  // --- barre du haut
  for (int y = 0; y < 19; y++) canvas.drawFastHLine(0, y, SCR_W, mixc(rgb(24, 20, 56), rgb(8, 6, 24), y * 14));
  { uint16_t rb = rainbow((int)(t / 12)); canvas.drawFastHLine(0, 19, SCR_W, rb); canvas.drawFastHLine(0, 20, SCR_W, mixc(rb, 0, 190)); }
  drawBattery(5, 4, batLevel, batChg);
  { const char* T = "AD ARCADE"; int n = 9, x0 = SCR_W / 2 - 40 + 6;                    // titre : lettres en degrade qui ondulent
    for (int i = 0; i < n; i++) { char ch[2] = {T[i], 0}; int yy = 2 + (int)(sinf(t * 0.006f + i * 0.7f) * 1.2f);
      txt(ch, x0 + i * 9 + 1, yy + 1, &fonts::Font2, rgb(40, 10, 40)); txt(ch, x0 + i * 9, yy, &fonts::Font2, mixc(rgb(255, 230, 90), rgb(255, 120, 200), i * 32 + 20)); } }
  char b[10]; snprintf(b, sizeof b, "%d/%d", sel + 1, NGAMES); txt(b, SCR_W - 5, 6, &fonts::Font0, rgb(170, 180, 220), textdatum_t::top_right);
  // --- carrousel
  float pulse = (sinf(t * 0.008f) + 1) * 0.5f;
  for (int d = -1; d <= 1; d++) {
    int idx = (sel + d + NGAMES) % NGAMES;
    float px = SCR_W / 2 - 32 + (d - slide) * 82;
    int ix = (int)px, iy = 24 + (d == 0 ? (int)(sinf(t * 0.006f) * 2) : 7);
    if (ix > SCR_W || ix < -64) continue;
    float cen = 1.0f - fminf(1.0f, fabsf(d - slide));            // 1 = pile au centre
    canvas.fillEllipse(ix + 32, 97, 26 + (int)(cen * 6), 3, rgb(6, 4, 16));                 // ombre au sol
    if (cen > 0.05f) {
      uint16_t gl = mixc(rgb(30, 20, 60), acc, 80 + (int)(pulse * 90 * cen));
      canvas.fillRoundRect(ix - 8, iy - 8, 80, 80, 13, mixc(rgb(20, 12, 44), gl, (int)(cen * 200)));
      canvas.fillRoundRect(ix - 5, iy - 5, 74, 74, 10, mixc(acc, 0xFFFF, 70 + (int)(pulse * 60)));
      canvas.fillRoundRect(ix - 3, iy - 3, 70, 70, 8, rgb(16, 12, 34));
      for (int k = 0; k < 6; k++) {                              // petites perles qui courent autour du cadre
        float a = t * 0.004f + k * 1.0472f; int bx = ix + 32 + (int)(cosf(a) * 41), by = iy + 32 + (int)(sinf(a) * 41);
        bx = bx < ix - 5 ? ix - 5 : (bx > ix + 69 ? ix + 69 : bx); by = by < iy - 5 ? iy - 5 : (by > iy + 69 ? iy + 69 : by);
        canvas.fillCircle(bx, by, 1, rgb(255, 255, 255));
      }
    }
    GAMES[idx].icon(ix, iy);
    if (cen < 0.5f) dim(ix, iy);
    if (cen > 0.05f) { canvas.drawFastHLine(ix + 4, iy + 1, 20, mixc(0xFFFF, 0, 120)); }   // reflet
  }
  uint16_t ar = mixc(rgb(255, 210, 80), 0xFFFF, (int)(pulse * 140));
  canvas.fillTriangle(6, 58, 15, 50, 15, 66, ar); canvas.fillTriangle(SCR_W - 6, 58, SCR_W - 15, 50, SCR_W - 15, 66, ar);
  // --- bandeau du bas : nom + pagination
  for (int y = 103; y < SCR_H; y++) canvas.drawFastHLine(0, y, SCR_W, mixc(rgb(26, 18, 56), rgb(8, 6, 22), (y - 103) * 8));
  canvas.drawFastHLine(0, 103, SCR_W, mixc(acc, 0xFFFF, 60)); canvas.drawFastHLine(0, 104, SCR_W, mixc(acc, 0, 150));
  const char* nm = L(GAMES[sel].en, GAMES[sel].fr);
  txt(nm, SCR_W / 2 + 1, 105, &fonts::Font4, rgb(30, 10, 30), textdatum_t::top_center);
  txt(nm, SCR_W / 2, 104, &fonts::Font4, TFT_WHITE, textdatum_t::top_center);
  for (int i = 0; i < NGAMES; i++) {                                                     // points de pagination
    int x = SCR_W / 2 - (NGAMES * 9) / 2 + i * 9 + 3; bool on = i == sel;
    if (on) canvas.fillRoundRect(x - 2, 130, 8, 3, 1, mixc(acc, 0xFFFF, 100)); else canvas.fillRect(x, 131, 3, 2, rgb(70, 66, 110));
  }
  if (toastT && t - toastT < 2200) {                                                     // posture detectee par le gyroscope
    bool flat = tilt::posture() == 0; int w = 84;
    canvas.fillRoundRect(SCR_W / 2 - w / 2, 23, w, 15, 6, rgb(10, 8, 26)); canvas.drawRoundRect(SCR_W / 2 - w / 2, 23, w, 15, 6, acc);
    txt(flat ? L("FLAT MODE", "MODE A PLAT") : L("UPRIGHT MODE", "MODE DEBOUT"), SCR_W / 2, 26, &fonts::Font0, TFT_WHITE, textdatum_t::top_center);
  }
}

// ----------------------------------------------------------------------------- ecran de veille
static float svx = 60, svy = 30, svdx = 0.9f, svdy = 0.7f; static int svGame = 0;
static void drawSaver() {
  canvas.fillScreen(0);
  for (int i = 0; i < 20; i++) { int sx = (i * 61 + 7) % SCR_W, sy = (i * 37 + 11) % SCR_H; if (((millis() / 400) + i) % 5) canvas.drawPixel(sx, sy, rgb(70, 74, 100)); }
  svx += svdx; svy += svdy; bool hit = false;
  if (svx < 0) { svx = 0; svdx = -svdx; hit = true; } if (svx > SCR_W - 64) { svx = SCR_W - 64; svdx = -svdx; hit = true; }
  if (svy < 0) { svy = 0; svdy = -svdy; hit = true; } if (svy > SCR_H - 64) { svy = SCR_H - 64; svdy = -svdy; hit = true; }
  if (hit) svGame = (svGame + 1) % NGAMES;
  GAMES[svGame].icon((int)svx, (int)svy);
  present(0, 0);
}

static void toMenu() {
  music::end(); bgm::stop(); running = -1; slide = 0; g_quit = false; lastAct = millis(); saver = 0; if (adapted) { toastT = millis(); adapted = false; }
  M5.Speaker.stop(); applyBrightness();
}

// ----------------------------------------------------------------------------- intro facon demo scene des annees 90
static void intro() {
  const char* SCROLL = "     WELCOME TO AD ARCADE ***  17 GAMES IN YOUR POCKET ***  TILT  PRESS  PLAY ***  "
                       "TETRIS  SNAKE  LUNAR LANDER  FLAP BIRD  RACING  FLIGHT  AND MORE ***  "
                       "25 FAMOUS TUNES TO PLAY ***  CODED ON AN ESP32 WITH LOVE ***  GREETINGS TO ALL M5 FANS ***  ENJOY !!!     ";
  const int SL = strlen(SCROLL);
  const char* SUB = "WELCOME  -  M5STICKC PLUS2 EDITION";
  static const int ARP[16] = {220, 262, 330, 440, 330, 262, 220, 262, 196, 247, 294, 392, 294, 247, 196, 247};
  if (!starsInit) initStars();
  float sx = SCR_W; int t = 0;
  btnUpdate();
  while (true) {
    btnUpdate();
    if (t > 15 && (M5.BtnA.wasPressed() || M5.BtnB.wasPressed() || M5.BtnPWR.wasPressed())) break;
    sx -= 5.0f; if (sx + SL * 12 < 0) break;
    canvas.fillScreen(rgb(4, 2, 16));
    for (int y = 0; y < SCR_H; y += 3) canvas.fillRect(0, y, SCR_W, 3, mixc(rgb(4, 2, 16), rgb(30, 12, 52), y * 256 / SCR_H));
    for (int k = 0; k < 3; k++) {                                              // barres "copper"
      int cy = 56 + (int)(sinf(t * 0.055f + k * 1.9f) * 38);
      uint16_t base = k == 0 ? rgb(255, 90, 40) : (k == 1 ? rgb(40, 200, 255) : rgb(230, 60, 255));
      for (int d = -8; d <= 8; d++) { int lvl = (9 - abs(d)) * 28; uint16_t c = mixc(rgb(8, 2, 20), base, lvl > 256 ? 256 : lvl); if (d == 0) c = mixc(base, TFT_WHITE, 120); canvas.drawFastHLine(0, cy + d, SCR_W, c); }
    }
    for (auto &st : stars) { st.x -= st.v * 2.5f; if (st.x < 0) { st.x += SCR_W; st.y = rnd(0, SCR_H); } canvas.drawPixel((int)st.x, (int)st.y, st.v > 0.8f ? TFT_WHITE : rgb(150, 150, 210)); }
    // logo : lettres qui tombent puis ondulent
    const char* LOGO = "AD ARCADE";
    for (int i = 0; i < 9; i++) {
      int tt = t - i * 4; if (tt < 0) continue;
      int y = 30 + (tt < 18 ? -((18 - tt) * (18 - tt)) / 3 : 0) + (int)(sinf(t * 0.14f + i * 0.7f) * 7);
      int x = 12 + i * 24; char ch[2] = {LOGO[i], 0}; if (ch[0] == ' ') continue;
      txt(ch, x + 3, y + 3, &fonts::Font0, rgb(10, 4, 30), textdatum_t::top_left, 4.0f);
      txt(ch, x + 1, y + 1, &fonts::Font0, TFT_WHITE, textdatum_t::top_left, 4.0f);
      txt(ch, x, y, &fonts::Font0, rainbow(i * 26 + t * 5), textdatum_t::top_left, 4.0f);
    }
    int n = (t - 50) / 2; if (n > (int)strlen(SUB)) n = strlen(SUB);
    if (n > 0) { char sb[40]; memcpy(sb, SUB, n); sb[n] = 0; txt(sb, SCR_W / 2, 78, &fonts::Font0, (t / 4) & 1 ? rgb(255, 230, 120) : TFT_WHITE, textdatum_t::top_center, 1.0f); }
    canvas.fillRect(0, 98, SCR_W, 37, rgb(0, 0, 0)); canvas.drawFastHLine(0, 98, SCR_W, rainbow(t * 4)); canvas.drawFastHLine(0, 99, SCR_W, rainbow(t * 4 + 60)); canvas.drawFastHLine(0, 134, SCR_W, rainbow(t * 4 + 120));
    for (int i = 0; i < SL; i++) {
      int x = (int)sx + i * 12; if (x < -12 || x > SCR_W) continue;
      char ch[2] = {SCROLL[i], 0}; if (ch[0] == ' ') continue;
      int y = 109 + (int)(sinf(t * 0.2f + i * 0.5f) * 7);
      txt(ch, x + 1, y + 1, &fonts::Font0, rgb(40, 20, 60), textdatum_t::top_left, 2.0f);
      txt(ch, x, y, &fonts::Font0, rainbow(i * 14 + t * 6), textdatum_t::top_left, 2.0f);
    }
    present(0, 0);
    if (t % 4 == 0) sfx(ARP[(t / 4) & 15] * ((t / 64) & 1 ? 2 : 1), 90);
    if (t % 16 == 0) sfx(ARP[(t / 16) & 3] / 2, 120, false);
    t++; delay(24);
  }
  M5.Speaker.stop();
  for (int f = 0; f < 12; f++) {                                              // fondu en damier
    for (int by = 0; by < 9; by++) for (int bx = 0; bx < 15; bx++) if (((bx * 7 + by * 3) % 13) < f + 1) canvas.fillRect(bx * 16, by * 16, 16, 16, rgb(12, 10, 30));
    present(0, 0); delay(25);
  }
  sfx(660, 70); sfx(880, 70, false); sfx(1320, 140, false);
}

void setup() {
  auto cfg = M5.config();
  M5.begin(cfg);
  if (M5.getBoard() == m5::board_t::board_M5StickCPlus2) { pinMode(4, OUTPUT); digitalWrite(4, HIGH); }   // maintien de l'alimentation (StickC Plus2 uniquement)
  M5.Display.setRotation(SCR_ROT);
  mp.begin("arcade", false);
  sel = mp.getInt("sel", 0); if (sel < 0 || sel >= NGAMES) sel = 0;
  g_bright = mp.getInt("bri", 2); if (g_bright < 0 || g_bright > 4) g_bright = 2;
  g_sound = mp.getBool("snd", true);
  g_music = mp.getBool("mus", true);
  g_lang = mp.getInt("lang", 0) ? 1 : 0;
  g_sleepIdx = mp.getInt("slp", 1); if (g_sleepIdx < 0 || g_sleepIdx > 4) g_sleepIdx = 1;
  applyBrightness();
  M5.Speaker.setVolume(140);
  canvas.setColorDepth(16);
  canvas.createSprite(SCR_W, SCR_H);
  tilt::load();
  intro();
  if (tilt::valid()) { tilt::zero(); toastT = millis(); }             // stabilisation unique : la position tenue au demarrage = "a plat" pour tous les jeux
  else tilt::startCalibration();               // premier demarrage : assistant d'inclinaison
  lastAct = millis();
}

void loop() {
  btnUpdate();
  bool anyBtn = M5.BtnA.wasPressed() || M5.BtnB.wasPressed() || M5.BtnPWR.wasPressed();
  if (tilt::calibrating()) { tilt::calibrationStep(); lastAct = millis(); return; }
  if (running >= 0) {
    if (M5.BtnPWR.pressedFor(1500) || g_pwrHold || g_quit) { sfx(440, 60); sfx(330, 90, false); toMenu(); return; }
    GAMES[running].loop();
    return;
  }
  uint32_t now = millis();
  // ----- ecran de veille (uniquement dans le menu)
  if (saver) {
    if (anyBtn) { saver = 0; applyBrightness(); lastAct = now; return; }          // le 1er appui reveille seulement
    if (saver == 1) { drawSaver(); delay(16); if (now - lastAct > SLEEP_MS[g_sleepIdx] + 60000) { saver = 2; M5.Display.setBrightness(0); } }
    else delay(40);
    return;
  }
  if (anyBtn) lastAct = now;
  if (SLEEP_MS[g_sleepIdx] && now - lastAct > SLEEP_MS[g_sleepIdx]) { saver = 1; M5.Display.setBrightness(BRI[g_bright] > 40 ? 40 : BRI[g_bright]); return; }
  if (now - batT > 3000 || batT == 0) {
    batT = now; int l = M5.Power.getBatteryLevel(); if (l >= 0) batLevel = l > 100 ? 100 : l;
    batChg = M5.Power.isCharging() == m5::Power_Class::is_charging;
  }
  if (M5.BtnB.wasPressed()) { sel = (sel + 1) % NGAMES; slide = -1; sfx(1200, 20); }
  if (M5.BtnPWR.wasPressed()) { sel = (sel + NGAMES - 1) % NGAMES; slide = 1; sfx(1000, 20); }
  if (slide != 0) { slide *= 0.7f; if (fabsf(slide) < 0.03f) slide = 0; }
  if (M5.BtnA.wasPressed()) {
    mp.putInt("sel", sel); sfx(880, 50); sfx(1320, 90, false);
    if (tilt::adapt()) adapted = true;                                      // detecte a plat / debout et re-stabilise si besoin
    g_quit = false; GAMES[sel].begin(); running = sel;
    return;
  }
  drawMenu();
  present(0, 0);
}
