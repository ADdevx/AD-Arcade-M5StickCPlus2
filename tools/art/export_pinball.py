# Export d'Ember Pinball vers src/pinball_art.h (art 4 bits/RLE + geometrie de collision)
import os
from pinball import *
ROOT=os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..'))
def encode(s):
    flat=[v for row in s.p for v in row]; cols=sorted({v for v in flat if v is not None}); runs=[]; i=0
    while i<len(flat):
        j=i
        while j<len(flat) and flat[j]==flat[i] and j-i<255: j+=1
        runs+=[j-i,255 if flat[i] is None else flat[i]]; i=j
    if len(cols)<=15:
        m={c:k+1 for k,c in enumerate(cols)}; nib=[m[v] if v is not None else 0 for v in flat]
        if len(nib)%2: nib.append(0)
        packed=list(cols)+[(nib[k]<<4)|nib[k+1] for k in range(0,len(nib),2)]
        if len(packed)<=len(runs): return 0,len(cols),packed
    return 1,0,runs
def pal565(p): return [((r>>3)<<11)|((g>>2)<<5)|(b>>3) for (r,g,b) in p]
SP=[('TABLE',table()),('PANEL_L',panel_left()),('PANEL_R',panel_right()),('BALL',ball()),('BUMPER',bumper(False)),('BUMPER_LIT',bumper(True)),('TARGET_UP',target(True)),('TARGET_DOWN',target(False))]
blob=[]; ent=[]; names=[]
for n,s in SP:
    fmt,nl,d=encode(s); ent.append((s.w,s.h,fmt,nl,len(blob))); blob+=d; names.append(n)
L_=['// GENERE par tools/art/export_pinball.py -- ne pas modifier a la main','#pragma once','#include <stdint.h>','namespace pbart {',
 'static const uint16_t PAL[48] = {%s};'%','.join('0x%04X'%v for v in pal565(PAL)),
 'struct Spr { uint16_t w, h; uint8_t fmt, nlut; uint32_t off; };',
 'static const Spr SPR[%d] = {%s};'%(len(ent),','.join('{%d,%d,%d,%d,%d}'%e for e in ent))]
for i,n in enumerate(names): L_.append('static const uint8_t S_%s = %d;'%(n,i))
L_.append('static const uint8_t BLOB[%d] = {'%len(blob))
for i in range(0,len(blob),40): L_.append(','.join(map(str,blob[i:i+40]))+',')
L_.append('};')
L_.append('enum { K_WALL, K_SLING, K_TARGET, K_GATE };')
L_.append('static const int16_t SEGS[%d][6] = {%s};   // x0 y0 x1 y1 type tag'%(len(SEGS),','.join('{%d,%d,%d,%d,%d,%d}'%tuple(int(round(v)) for v in sg) for sg in SEGS)))
L_.append('static const int16_t BUMPERS[%d][3] = {%s};'%(len(BUMPERS),','.join('{%d,%d,%d}'%b for b in BUMPERS)))
L_.append('static const int16_t SAUCER[3] = {%d,%d,%d};'%SAUCER)
L_.append('static const int16_t LANES[3][2] = {%s};'%','.join('{%d,%d}'%l for l in LANES))
L_.append('static const int16_t INSERTS[4][2] = {%s};'%','.join('{%d,%d}'%l for l in INSERTS))
L_.append('static const int16_t FLIP_L[2] = {%d,%d}, FLIP_R[2] = {%d,%d}, SHOOT[2] = {%d,%d};'%(FLIP_L+FLIP_R+SHOOT))
L_.append('static const int TW = %d, TH = %d, FLIP_LEN = %d;'%(TW,TH,FLIP_LEN))
L_.append('}  // namespace pbart')
open(os.path.join(ROOT,'src','pinball_art.h'),'w',encoding='utf-8',newline='\n').write('\n'.join(L_)+'\n')
print('pinball art %.1f Ko'%(len(blob)/1024))
