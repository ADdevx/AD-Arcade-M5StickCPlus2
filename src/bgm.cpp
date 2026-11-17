// ============================================================================
//  BGM - petites musiques de fond (boucles ORIGINALES) pour certains jeux.
//  Mono : une note a la fois, sur un canal a part du buzzer, a volume reduit.
//  Elle se tait pendant les effets sonores (sfx) et reprend en suivant le temps.
//  Reglage : Settings > "Game music" (g_music).
// ============================================================================
#include "common.h"

namespace bgm {

struct Loop { int bpm; const char* seq; };
static const Loop LOOPS[] = {
  /* 0 FLAP    */ {138, "C5:.5 E5:.5 G5:.5 E5:.5 A5:.5 G5:.5 E5:.5 D5:.5 C5:.5 E5:.5 G5:.5 C6:.5 B5:.5 G5:.5 A5:.5 R:.5 "
                        "F5:.5 A5:.5 C6:.5 A5:.5 G5:.5 E5:.5 G5:.5 D5:.5 E5:.5 G5:.5 A5:.5 G5:.5 E5:.5 D5:.5 C5:1"},
  /* 1 SNAKE   */ {128, "A4:.5 R:.5 C5:.5 R:.5 E5:.5 D5:.5 C5:.5 R:.5 A4:.5 R:.5 B4:.5 R:.5 C5:1 R:1 "
                        "G4:.5 R:.5 B4:.5 R:.5 D5:.5 C5:.5 B4:.5 R:.5 E4:.5 G#4:.5 B4:.5 E5:.5 A4:2"},
  /* 2 TETRIS  */ {124, "D5:.5 F#5:.5 A5:1 F#5:.5 D5:.5 E5:1 G5:1 A5:.5 F#5:.5 D5:1 B4:2 "
                        "B4:.5 D5:.5 G5:1 F#5:.5 E5:.5 D5:1 F#5:1 E5:.5 C#5:.5 A4:1 D5:2"},
  /* 3 STACK   */ {100, "C5:1 G4:1 E5:1 G4:1 D5:1 A4:1 F5:1 A4:1 E5:1 B4:1 G5:1 B4:1 D5:1 G4:1 C5:2"},
  /* 4 FISH    */ {150, "E5:.25 G5:.25 C6:.25 G5:.25 E5:.25 G5:.25 C6:.25 G5:.25 F5:.25 A5:.25 C6:.25 A5:.25 F5:.25 A5:.25 C6:.25 A5:.25 "
                        "D5:.25 G5:.25 B5:.25 G5:.25 D5:.25 G5:.25 B5:.25 G5:.25 E5:.25 G5:.25 C6:.25 G5:.25 C5:.5 R:.5"},
  /* 5 RIVER   */ {112, "D5:1 F#5:.5 A5:.5 F#5:1 D5:1 E5:1 G5:.5 B5:.5 G5:1 E5:1 F#5:1 A5:.5 B5:.5 A5:1 F#5:1 E5:2 D5:2"},
  /* 6 LANDER  */ {92,  "A4:2 E5:1 A5:1 G5:2 E5:1 D5:1 F5:2 C5:1 A4:1 E5:2 B4:1 G#4:1"},
  /* 7 DINO     */ {150, "E5:.5 E5:.5 R:.5 E5:.5 G5:.5 R:.5 E5:.5 D5:.5 C5:.5 C5:.5 R:.5 C5:.5 E5:.5 R:.5 D5:.5 C5:.5 "
                        "A4:.5 A4:.5 R:.5 A4:.5 C5:.5 R:.5 A4:.5 G4:.5 B4:.5 B4:.5 R:.5 B4:.5 D5:.5 R:.5 G5:.5 D5:1"},
  /* 8 METEORS  */ {120, "A4:.5 E5:.5 A4:.5 E5:.5 C5:.5 G5:.5 C5:.5 G5:.5 B4:.5 F#5:.5 B4:.5 F#5:.5 E5:1 R:1"},
  /* 9 MAZE     */ {96,  "C5:1 E5:1 G5:1 E5:1 A4:1 C5:1 E5:1 C5:1 F4:1 A4:1 C5:1 A4:1 G4:1 B4:1 D5:1 G5:1"},
  /* 10 BREAKOUT*/ {140, "C5:.5 G4:.5 C5:.5 E5:.5 G5:1 E5:.5 C5:.5 D5:.5 A4:.5 D5:.5 F5:.5 A5:1 F5:.5 D5:.5 B4:.5 G4:.5 B4:.5 D5:.5 G5:1 D5:.5 B4:.5 C5:2"},
  /* 11 INVADERS*/ {108, "A4:.5 A4:.5 E5:1 A4:.5 A4:.5 D5:1 A4:.5 A4:.5 C5:1 B4:.5 B4:.5 E5:1"},
  /* 12 SLALOM  */ {160, "G5:.5 E5:.5 C5:.5 E5:.5 G5:.5 A5:.5 F5:.5 D5:.5 F5:.5 A5:.5 B5:.5 G5:.5 E5:.5 G5:.5 C6:1"},
  /* 13 RACE    */ {170, "A4:.5 A4:.5 C5:.5 A4:.5 E5:.5 A4:.5 C5:.5 A4:.5 G4:.5 G4:.5 B4:.5 G4:.5 D5:.5 G4:.5 B4:.5 G4:.5 "
                        "F4:.5 F4:.5 A4:.5 F4:.5 C5:.5 F4:.5 A4:.5 F4:.5 E4:.5 E4:.5 G#4:.5 E4:.5 B4:.5 E4:.5 G#4:.5 B4:.5"},
  /* 14 FLIGHT  */ {104, "C5:1 G5:2 E5:1 D5:1 A5:2 F5:1 E5:1 B5:2 G5:1 C6:2 G5:1 E5:1 C5:2 R:1"},
};
static const int NL = sizeof(LOOPS) / sizeof(LOOPS[0]);
struct Note { float freq; int start, dur; };
static Note notes[48]; static int nNotes = 0, totalMs = 1;
static int cur = -1, curId = -1, idx = -1;
static uint32_t t0 = 0, sfxUntil = 0;
static const int CH = 6;

static void load(int id) {
  const char* p = LOOPS[id].seq; float beat = 60000.f / LOOPS[id].bpm; int ms = 0; nNotes = 0;
  static const int base[7] = {9, 11, 0, 2, 4, 5, 7};
  while (*p && nNotes < 48) {
    while (*p == ' ') p++;
    if (!*p) break;
    int midi = -1;
    if (*p == 'R') p++; else {
      int n = base[*p++ - 'A']; if (*p == '#') { n++; p++; }
      midi = 12 * ((*p++ - '0') + 1) + n;
    }
    p++;
    float d = atof(p); while (*p && *p != ' ') p++;
    int dur = (int)(d * beat);
    if (midi >= 0) notes[nNotes++] = {440.f * powf(2.f, (midi - 69) / 12.f), ms, dur};
    ms += dur;
  }
  totalMs = ms > 0 ? ms : 1;
}

void stop() { if (curId >= 0) M5.Speaker.stop(CH); curId = -1; cur = -1; }
void onSfx(int ms) { sfxUntil = millis() + ms + 20; if (curId >= 0) { M5.Speaker.stop(CH); cur = -1; } }

void run(int id, bool on) {
  if (!on || !g_sound || !g_music || id < 0 || id >= NL) { if (curId >= 0) stop(); return; }
  if (curId != id) { load(id); curId = id; t0 = millis(); cur = -1; M5.Speaker.setChannelVolume(CH, 40); }
  uint32_t now = millis();
  if (now < sfxUntil) return;
  int t = (int)((now - t0) % totalMs), i = -1;
  for (int k = 0; k < nNotes; k++) if (t >= notes[k].start && t < notes[k].start + notes[k].dur) { i = k; break; }
  if (i < 0) { cur = -1; return; }
  if (i != cur || (cur == i && false)) {
    cur = i; int rem = notes[i].start + notes[i].dur - t; int d = rem * 9 / 10; if (d < 25) d = 25;
    M5.Speaker.tone(notes[i].freq, d, CH, true);
  }
}

}  // namespace bgm
