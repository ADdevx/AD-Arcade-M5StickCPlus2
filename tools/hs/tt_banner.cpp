#include "common.h"
namespace bannertest { void begin(){ trophy::record(trophy::T_TETRIS, 9000); } void loop(){ canvas.fillScreen(rgb(60,120,200)); trophy::banner(); present(0,0); delay(16); } }
