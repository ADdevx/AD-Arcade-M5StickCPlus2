// ============================================================================
//  M5 ARCADE - elements communs a tous les jeux
// ============================================================================
#pragma once
#include <M5Unified.h>
#include <Preferences.h>
#include <math.h>

#ifndef SCR_ROT
#define SCR_ROT 3          // 1 ou 3 : change le sens de l'ecran (donc haut/bas physiques)
#endif
#define AD_VERSION "1.5"   // version affichee dans les reglages
#define SCR_W   240
#define SCR_H   135

extern M5Canvas canvas;    // tampon plein ecran partage par tous les jeux (cree dans main.cpp)

static inline uint16_t rgb(uint8_t r, uint8_t g, uint8_t b) { return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3); }
// generateur aleatoire : vrai hasard, sauf en "defi du jour" / "2 joueurs" ou une graine commune rend les parties comparables
extern uint32_t g_rngState; extern bool g_rngSeeded;
static inline uint32_t rawRand() { if (!g_rngSeeded) return esp_random(); uint32_t x = g_rngState; x ^= x << 13; x ^= x >> 17; x ^= x << 5; g_rngState = x; return x; }
static inline void seedRand(uint32_t s) { g_rngState = s ? s : 0x9E3779B9u; g_rngSeeded = true; }
static inline uint32_t rnd(uint32_t a, uint32_t b) { return a + rawRand() % (b - a + 1); }
static inline float clampf(float v, float lo, float hi) { return v < lo ? lo : (v > hi ? hi : v); }

void present(int ox = 0, int oy = 0);   // envoie le tampon a l'ecran (mis a l'echelle sur les petits ecrans, ex. StickC 160x80)
void btnUpdate();   // M5.update() + bouton PWR de remplacement sur les appareils qui n'en ont pas (Nesso N1 : toucher l'ecran)
void sfx(int freq, int ms, bool stopPrev = true);   // son (defini dans main.cpp) ; muet si le son est coupe dans les reglages

// reglages globaux (definis dans main.cpp, modifies dans settings.cpp)
extern int  g_bright;       // 0..4
extern bool g_sound;
extern int  g_theme;        // theme de couleurs du menu (0 = auto)
int  themeCount();
const char* themeName(int i);
extern bool g_music;         // petites musiques dans les jeux
extern int  g_vol;           // volume 0..5 (0 = muet)
extern int  g_diff;          // difficulte : 0 facile, 1 normal, 2 difficile
extern int  g_skin;          // apparence du heros des jeux (debloquee avec les medailles)
static inline float dif(float easy, float normal, float hard) { return g_diff == 0 ? easy : (g_diff == 2 ? hard : normal); }
static inline int   difi(int easy, int normal, int hard) { return g_diff == 0 ? easy : (g_diff == 2 ? hard : normal); }
// espace de noms des records selon la difficulte : "flap" (normal), "flapE" (facile), "flapH" (difficile)
static inline const char* dnsFor(const char* base, int d) { static char buf[4][20]; static int k = 0; char* o = buf[k = (k + 1) & 3]; snprintf(o, 20, "%s%s", base, d == 0 ? "E" : (d == 2 ? "H" : "")); return o; }
static inline const char* dns(const char* base) { return dnsFor(base, g_diff); }
extern int  g_lang;           // 0 = English (defaut), 1 = Francais
static inline const char* L(const char* en, const char* fr) { return g_lang ? fr : en; }
extern int  g_sleepIdx;     // 0..4 (30 s, 1 min, 2 min, 5 min, jamais)
extern bool g_quit;         // un jeu / l'ecran de reglages met true pour revenir au menu
void applyBrightness(); void applyVolume();
void saveSettings();

// melange de 2 couleurs RGB565 (t = 0..256)
static inline uint16_t mixc(uint16_t a, uint16_t b, int t) {
  int ar = (a >> 11) & 31, ag = (a >> 5) & 63, ab = a & 31, br = (b >> 11) & 31, bg = (b >> 5) & 63, bb = b & 31;
  return (uint16_t)(((ar + (((br - ar) * t) >> 8)) << 11) | ((ag + (((bg - ag) * t) >> 8)) << 5) | (ab + (((bb - ab) * t) >> 8)));
}

// texte : police + couleur + alignement en un seul appel (polices ASCII : pas d'accents)
static inline void txt(const char* s, int x, int y, const lgfx::IFont* f, uint16_t col,
                       textdatum_t d = textdatum_t::top_left, float size = 1.0f) {
  canvas.setFont(f); canvas.setTextSize(size); canvas.setTextDatum(d); canvas.setTextColor(col);
  canvas.drawString(s, x, y);
  canvas.setTextSize(1.0f);
}
// texte avec contour (lisible sur n'importe quel fond)
static inline void txtO(const char* s, int x, int y, const lgfx::IFont* f, uint16_t col, uint16_t outline,
                        textdatum_t d = textdatum_t::top_left, float size = 1.0f) {
  for (int dy = -1; dy <= 1; dy++) for (int dx = -1; dx <= 1; dx++) if (dx || dy) txt(s, x + dx, y + dy, f, outline, d, size);
  txt(s, x, y, f, col, d, size);
}

// ----------------------------- les jeux -------------------------------------
// begin() : appele au lancement ; loop() : appele a chaque tour (dessine et pousse l'ecran) ;
// icon(x, y) : dessine l'icone 64x64 du menu (coin haut-gauche en x, y)
namespace dino  { void begin(); void loop(); void icon(int x, int y); }
namespace flap  { void begin(); void loop(); void icon(int x, int y); }
namespace space { void begin(); void loop(); void icon(int x, int y); }
namespace maze  { void begin(); void loop(); void icon(int x, int y); }
namespace breakout { void begin(); void loop(); void icon(int x, int y); }
namespace invaders { void begin(); void loop(); void icon(int x, int y); }
namespace ski { void begin(); void loop(); void icon(int x, int y); }
namespace stack { void begin(); void loop(); void icon(int x, int y); }
namespace sky { void begin(); void loop(); void icon(int x, int y); }
namespace race { void begin(); void loop(); void icon(int x, int y); }
namespace river { void begin(); void loop(); void icon(int x, int y); }
namespace fish { void begin(); void loop(); void icon(int x, int y); }
namespace tetris { void begin(); void loop(); void icon(int x, int y); }
namespace snake { void begin(); void loop(); void icon(int x, int y); }
namespace lander { void begin(); void loop(); void icon(int x, int y); }
namespace music { void begin(); void loop(); void icon(int x, int y); void end(); }
namespace settings { void begin(); void loop(); void icon(int x, int y); }

// ----------------------------- musiques de fond des jeux (boucles originales)
// run(id, on) : a appeler a chaque tour de boucle ; on = la partie est en cours
namespace trophy {
enum Id { T_DINO, T_FLAP, T_METEORS, T_MAZE, T_BREAKOUT, T_INVADERS, T_SLALOM, T_STACK, T_RACING, T_FLIGHT, T_RIVER, T_FISH, T_TETRIS, T_SNAKE, T_LANDER, T_COUNT };
int  total();                          // medailles gagnees (normal + difficile)
int  medalAt(int id, int diff);        // 0..3 : meilleure medaille du jeu a cette difficulte
void record(int id, uint32_t value);   // fin de partie : medaille bronze / argent / or selon la valeur
void banner();                         // bandeau "nouvelle medaille" (appele par present())
void begin(); void loop(); void icon(int x, int y);
}

// ----------------------------- skins (apparences) : debloques avec les medailles
namespace skin {
int  count();                      // nombre d'apparences
const char* name(int i);
int  need(int i);                  // nombre de medailles necessaires
bool unlocked(int i);
// couleur du heros : 0 corps, 1 ombre, 2 reflet, 3 accent ; renvoie def si l'apparence "Classic" est choisie
uint16_t c(int slot, uint16_t def);
}

// ----------------------------- modes speciaux : defi du jour, 2 joueurs, stats
namespace session {
void onOver(int gameId, int score);      // appele par chaque jeu a la fin d'une partie
int  activeGame();                       // jeu en cours dans un mode special (-1 si aucun)
void end();                              // appele au retour au menu
bool dateEditing(); void dateBegin(); void dateLoop();   // reglage de la date (reglages + defi du jour)
void overlay();                          // bandeau dessine par present()
}
namespace daily { void begin(); void loop(); void icon(int x, int y); }
namespace duo   { void begin(); void loop(); void icon(int x, int y); }
namespace stats { void begin(); void loop(); void icon(int x, int y); void play(int idx); void tick(int idx); void flush(); int total(); }
// acces aux jeux depuis les modes speciaux (definis dans main.cpp) : indices 0..14 = identifiants trophy::Id
void gameBegin(int idx); void gameLoop(int idx); const char* gameName(int idx); void gameIcon(int idx, int x, int y);

namespace bgm { void run(int id, bool on); void stop(); void onSfx(int ms); }

// ----------------------------- inclinaison (IMU) -----------------------------
// Calibrage automatique : on montre quel cote pencher, le module trouve tout seul
// quel axe de l'accelerometre correspond (et dans quel sens). Memorise en flash.
namespace tilt {
  void  load();                 // lit le calibrage sauvegarde
  bool  valid();                // un calibrage existe ?
  void  startCalibration();     // lance l'assistant (3 etapes, bouton A)
  bool  calibrating();          // l'assistant est-il actif ?
  void  calibrationStep();      // a appeler a chaque tour tant que calibrating() : dessine + lit A
  void  update();               // lit l'IMU (1 fois par image)
  bool  adapt();                // au lancement d'un jeu : si le M5 n'est plus tenu comme au demarrage (a plat <-> debout), re-stabilise tout seul ; true si fait
  int   posture();              // 0 = a plat (ecran vers le haut), 1 = debout / paysage (comme une console)
  void  zero();                 // memorise la position "a plat" actuelle (~60 ms) : fait au demarrage + dans Reglages
  float x();                    // -1..1 : + = on penche le cote DROIT vers le bas
  float y();                    // -1..1 : + = on penche le HAUT de l'ecran vers le bas
}
