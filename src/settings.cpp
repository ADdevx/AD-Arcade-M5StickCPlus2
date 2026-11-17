// ============================================================================
//  REGLAGES - luminosite, son, delai de veille, stabilisation et calibrage de l'inclinaison
//  B = ligne suivante, HAUT = ligne precedente, M5 = changer / valider
// ============================================================================
#include "common.h"

namespace settings {

static const int NROWS = 8;
static const char* ROWS_EN[NROWS] = {"Brightness", "Sound", "Game music", "Sleep", "Stabilize", "Calibrate", "Language", "Back"};
static const char* ROWS_FR[NROWS] = {"Luminosite", "Son", "Musique jeux", "Veille", "Stabiliser", "Calibrage", "Langue", "Retour"};
static const char* SLEEPS_EN[5] = {"30 s", "1 min", "2 min", "5 min", "never"};
static const char* SLEEPS_FR[5] = {"30 s", "1 min", "2 min", "5 min", "jamais"};
static int sel = 0;
static uint32_t stabStart = 0;       // > 0 : compte a rebours de stabilisation en cours

void begin() { sel = 0; stabStart = 0; }

static void render() {
  canvas.fillScreen(rgb(14, 16, 34));
  canvas.fillRect(0, 0, SCR_W, 14, rgb(26, 30, 62));
  txt(L("SETTINGS","REGLAGES"), SCR_W / 2, -2, &fonts::Font2, rgb(255, 210, 80), textdatum_t::top_center);
  txt("v" AD_VERSION, SCR_W - 4, 3, &fonts::Font0, rgb(150, 160, 210), textdatum_t::top_right);
  for (int i = 0; i < NROWS; i++) {
    int y = 15 + i * 15; bool s = i == sel;
    if (s) { canvas.fillRoundRect(6, y, SCR_W - 12, 14, 5, rgb(48, 56, 120)); canvas.drawRoundRect(6, y, SCR_W - 12, 14, 5, rgb(255, 210, 80)); }
    txt((g_lang ? ROWS_FR : ROWS_EN)[i], 14, y, &fonts::Font2, s ? TFT_WHITE : rgb(160, 170, 210));
    int vx = SCR_W - 16;
    if (i == 0) { for (int k = 0; k < 5; k++) canvas.fillRect(vx - 5 * 11 + k * 11 + 1, y + 10 - k * 2 - 2, 8, 4 + k * 2, k <= g_bright ? rgb(255, 210, 80) : rgb(60, 64, 100)); }
    else if (i == 1 || i == 2) { bool on = i == 1 ? g_sound : g_music; canvas.fillRoundRect(vx - 34, y + 2, 34, 11, 5, on ? rgb(60, 200, 110) : rgb(110, 110, 130)); canvas.fillCircle(on ? vx - 6 : vx - 28, y + 7, 4, TFT_WHITE); }
    else if (i == 3) txt((g_lang ? SLEEPS_FR : SLEEPS_EN)[g_sleepIdx], vx, y, &fonts::Font2, rgb(150, 220, 255), textdatum_t::top_right);
    else if (i == 6) txt(g_lang ? "FRANCAIS" : "ENGLISH", vx, y, &fonts::Font2, rgb(150, 220, 255), textdatum_t::top_right);
    else if (i == 4 || i == 5) txt("M5", vx, y + 3, &fonts::Font0, rgb(120, 130, 180), textdatum_t::top_right);
  }
  if (stabStart) {
    int left = 3 - (int)((millis() - stabStart) / 1000);
    canvas.fillRoundRect(30, 38, 180, 60, 8, rgb(10, 12, 28)); canvas.drawRoundRect(30, 38, 180, 60, 8, rgb(255, 210, 80));
    txt(L("Hold the M5 as you play","Tiens le M5 comme pour jouer"), SCR_W / 2, 46, &fonts::Font2, TFT_WHITE, textdatum_t::top_center);
    char b[4]; snprintf(b, sizeof b, "%d", left < 1 ? 1 : left); txt(b, SCR_W / 2, 66, &fonts::Font4, rgb(255, 210, 80), textdatum_t::top_center);
  }
}

void loop() {
  if (stabStart) {
    if (millis() - stabStart >= 3000) { tilt::zero(); stabStart = 0; sfx(1320, 80); sfx(1760, 120, false); }
  } else {
    bool a = M5.BtnA.wasPressed(), b = M5.BtnB.wasPressed(), p = M5.BtnPWR.wasPressed();
    if (b) { sel = (sel + 1) % NROWS; sfx(1200, 15); }
    else if (p) { sel = (sel + NROWS - 1) % NROWS; sfx(1000, 15); }
    else if (a) {
      switch (sel) {
        case 0: g_bright = (g_bright + 1) % 5; applyBrightness(); saveSettings(); sfx(1100, 20); break;
        case 1: g_sound = !g_sound; saveSettings(); sfx(1100, 40); sfx(1500, 60, false); break;
        case 2: g_music = !g_music; saveSettings(); sfx(1100, 40); sfx(1500, 60, false); break;
        case 3: g_sleepIdx = (g_sleepIdx + 1) % 5; saveSettings(); sfx(1100, 20); break;
        case 4: stabStart = millis(); sfx(880, 40); break;
        case 5: tilt::startCalibration(); break;
        case 6: g_lang ^= 1; saveSettings(); sfx(1100, 40); sfx(1500, 60, false); break;
        case 7: g_quit = true; break;
      }
    }
  }
  render();
  present(0, 0);
  delay(10);
}

void icon(int x, int y) {
  canvas.fillRoundRect(x, y, 64, 64, 6, rgb(40, 46, 96));
  int cx = x + 32, cy = y + 32;
  for (int k = 0; k < 8; k++) { float a = k * 0.7854f; canvas.fillCircle(cx + (int)(cosf(a) * 21), cy + (int)(sinf(a) * 21), 5, rgb(190, 198, 230)); }
  canvas.fillCircle(cx, cy, 20, rgb(190, 198, 230)); canvas.fillCircle(cx, cy, 8, rgb(40, 46, 96)); canvas.drawCircle(cx, cy, 14, rgb(150, 158, 200));
}

}  // namespace settings
