// ============================================================================
//  Inclinaison via l'accelerometre (MPU6886) avec calibrage automatique des axes
// ============================================================================
#include "common.h"

namespace tilt {

static Preferences pr;
static int   axX = 0, axY = 1;           // quel axe de l'accelerometre = gauche/droite, haut/bas
static float sgX = 1, sgY = 1;           // sens
static float sgZ = 1;                    // sens de l'axe perpendiculaire a l'ecran (+ = l'ecran regarde vers le haut quand le M5 est a plat)
static float zeroV[3] = {0, 0, 0};       // position "a plat"
static float filt[3]  = {0, 0, 0};
static bool  ok = false;

static bool  calib = false;
static int   step = 0;                   // 0 = a plat, 1 = cote droit en bas, 2 = haut de l'ecran en bas
static bool  capturing = false;
static uint32_t capStart = 0; static int capN = 0; static float capSum[3];
static float base[3];
static const char* warn = nullptr;
static const float SCALE = 0.45f;        // 0.45 g (~27 degres) = pleine inclinaison

static void readRaw(float* a) {
  float x = 0, y = 0, z = 0;
  M5.Imu.getAccel(&x, &y, &z);
  a[0] = x; a[1] = y; a[2] = z;
}

void load() {
  pr.begin("tilt", false);
  ok = pr.getBool("ok", false);
  if (ok) {
    axX = pr.getInt("ax", 0); axY = pr.getInt("ay", 1);
    sgX = pr.getInt("sx", 1) >= 0 ? 1.f : -1.f; sgY = pr.getInt("sy", 1) >= 0 ? 1.f : -1.f;
    sgZ = pr.getInt("sz", 1) >= 0 ? 1.f : -1.f;
    if (axX < 0 || axX > 2 || axY < 0 || axY > 2 || axX == axY) ok = false;
  }
}
bool valid() { return ok; }
bool calibrating() { return calib; }

void startCalibration() { calib = true; step = 0; capturing = false; warn = nullptr; }

void update() {
  float a[3]; readRaw(a);
  for (int i = 0; i < 3; i++) filt[i] += 0.35f * (a[i] - filt[i]);
}

static int mode = 0;                     // 0 = a plat, 1 = debout (paysage, comme une console)
static void detectMode() { int axZ = 3 - axX - axY; mode = fabsf(sgZ * zeroV[axZ]) > 0.7f ? 0 : 1; }
int posture() { return mode; }

void zero() {
  float s[3] = {0, 0, 0}; const int N = 10;
  for (int i = 0; i < N; i++) { float a[3]; readRaw(a); for (int k = 0; k < 3; k++) s[k] += a[k]; delay(6); }
  for (int k = 0; k < 3; k++) { zeroV[k] = s[k] / N; filt[k] = zeroV[k]; }
  detectMode();
}

// Au lancement d'un jeu : on compare la pose actuelle a celle memorisee au demarrage.
// Differente (par ex. demarre a plat, joue debout) -> on re-stabilise silencieusement, sinon on garde la stabilisation unique.
bool adapt() {
  if (!ok) return false;
  float s[3] = {0, 0, 0}; const int N = 6;
  for (int i = 0; i < N; i++) { float a[3]; readRaw(a); for (int k = 0; k < 3; k++) s[k] += a[k]; delay(5); }
  float dmax = 0; for (int k = 0; k < 3; k++) { s[k] /= N; float d = fabsf(s[k] - zeroV[k]); if (d > dmax) dmax = d; }
  if (dmax < 0.30f) return false;
  for (int k = 0; k < 3; k++) { zeroV[k] = s[k]; filt[k] = s[k]; }
  detectMode();
  return true;
}

float x() { return ok ? clampf(sgX * (filt[axX] - zeroV[axX]) / SCALE, -1.f, 1.f) : 0.f; }
// y() s'adapte a la facon dont on tient le M5 au moment de la stabilisation :
//  - a plat (ecran vers le haut) : le haut de l'ecran qui descend = + (axe Y de l'accelerometre)
//  - debout / en paysage (comme une Game Boy) : on pousse le haut de l'ecran vers l'avant = + (axe perpendiculaire a l'ecran)
//  - entre les deux (tenu en biais) : melange continu. Dans tous les cas, gauche/droite = pencher le cote droit vers le bas.
float y() {
  if (!ok) return 0.f;
  int axZ = 3 - axX - axY;
  float u0 = sgY * zeroV[axY], w0 = sgZ * zeroV[axZ];
  float n = sqrtf(u0 * u0 + w0 * w0);
  float pu = 1.f, pw = 0.f;                                  // direction de bascule "haut vers le bas" dans le plan (Y ecran, perpendiculaire)
  if (n > 0.5f) { pu = w0 / n; pw = -u0 / n; }
  float du = sgY * (filt[axY] - zeroV[axY]), dw = sgZ * (filt[axZ] - zeroV[axZ]);
  return clampf((du * pu + dw * pw) / SCALE, -1.f, 1.f);
}

// ----------------------------- assistant ------------------------------------
static void drawDevice(int cx, int cy, int hi) {
  // le M5 vu de face, a l'horizontale ; hi : 0 = rien, 1 = cote droit, 2 = haut
  canvas.fillRoundRect(cx - 50, cy - 20, 100, 40, 5, rgb(60, 60, 70));
  canvas.fillRoundRect(cx - 40, cy - 14, 66, 28, 3, rgb(20, 30, 60));
  canvas.fillCircle(cx + 38, cy, 5, rgb(230, 90, 40));
  if (hi == 1) { canvas.fillRect(cx + 46, cy - 20, 5, 40, rgb(250, 220, 60)); canvas.fillTriangle(cx + 62, cy + 6, cx + 78, cy + 6, cx + 70, cy + 20, rgb(250, 220, 60)); }
  if (hi == 2) { canvas.fillRect(cx - 50, cy - 20, 100, 5, rgb(250, 220, 60)); canvas.fillTriangle(cx - 10, cy - 38, cx + 10, cy - 38, cx, cy - 26, rgb(250, 220, 60)); }
}

void calibrationStep() {
  update();
  const char* title[3] = {L("1/3  FLAT","1/3  A PLAT"), L("2/3  RIGHT SIDE DOWN","2/3  COTE DROIT EN BAS"), L("3/3  TOP OF SCREEN DOWN","3/3  HAUT DE L'ECRAN EN BAS")};
  const char* help[3] = {L("Hold the M5 flat and still","Tiens le M5 horizontal et immobile"), L("Tilt the RIGHT side down","Penche le cote DROIT vers le bas"), L("Tilt the TOP of the screen down","Penche le HAUT de l'ecran vers le bas")};
  canvas.fillScreen(rgb(10, 12, 24));
  txt(L("CALIBRATION","CALIBRAGE"), SCR_W / 2, 4, &fonts::Font2, rgb(250, 220, 60), textdatum_t::top_center);
  txt(title[step], SCR_W / 2, 24, &fonts::Font2, TFT_WHITE, textdatum_t::top_center);
  drawDevice(SCR_W / 2 - 4, 76, step);
  txt(help[step], SCR_W / 2, 108, &fonts::Font0, rgb(180, 200, 255), textdatum_t::top_center);
  if (warn) txt(warn, SCR_W / 2, 52, &fonts::Font0, rgb(255, 110, 90), textdatum_t::top_center);

  if (!capturing) {
    txt(L("press M5 (A) then hold still","appuie sur M5 (A) puis ne bouge plus"), SCR_W / 2, 122, &fonts::Font0, rgb(140, 150, 180), textdatum_t::top_center);
    if (M5.BtnA.wasPressed()) { capturing = true; capStart = millis(); capN = 0; capSum[0] = capSum[1] = capSum[2] = 0; warn = nullptr; }
  } else {
    uint32_t el = millis() - capStart;
    txt(L("hold still...","ne bouge plus..."), SCR_W / 2, 122, &fonts::Font0, rgb(120, 255, 140), textdatum_t::top_center);
    if (el > 400) { float a[3]; readRaw(a); for (int k = 0; k < 3; k++) capSum[k] += a[k]; capN++; }   // 400 ms de latence, puis moyenne
    if (el > 900 && capN > 0) {
      float v[3]; for (int k = 0; k < 3; k++) v[k] = capSum[k] / capN;
      capturing = false;
      if (step == 0) { for (int k = 0; k < 3; k++) base[k] = v[k]; step = 1; sfx(880, 60); }
      else {
        float d[3]; for (int k = 0; k < 3; k++) d[k] = v[k] - base[k];
        int best = -1; float bv = 0;
        for (int k = 0; k < 3; k++) { if (step == 2 && k == axX) continue; if (fabsf(d[k]) > bv) { bv = fabsf(d[k]); best = k; } }
        if (best < 0 || bv < 0.20f) { warn = L("not enough tilt, try again","pas assez incline, recommence"); sfx(200, 150); }
        else if (step == 1) { axX = best; sgX = d[best] > 0 ? 1.f : -1.f; step = 2; sfx(880, 60); }
        else {
          axY = best; sgY = d[best] > 0 ? 1.f : -1.f;
          for (int k = 0; k < 3; k++) zeroV[k] = base[k];
          pr.putBool("ok", true); pr.putInt("ax", axX); pr.putInt("ay", axY); sgZ = base[3 - axX - axY] >= 0 ? 1.f : -1.f; pr.putInt("sz", (int)sgZ);
          pr.putInt("sx", (int)sgX); pr.putInt("sy", (int)sgY);
          ok = true; calib = false; detectMode(); sfx(1320, 80); sfx(1760, 120, false);
        }
      }
    }
  }
  present(0, 0);
}

}  // namespace tilt
