# Export des icones du menu v2 (icons2.py) vers src/icons_art.h
# format : par icone une palette RGB565 (<= 255 couleurs) + RLE (n, index)
import os
from icons2 import *
ROOT=os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..'))
def c565(c): r,g,b=c; return ((r>>3)<<11)|((g>>2)<<5)|(b>>3)
I=all_icons(); pal=[]; data=[]; ent=[]; MAP=[255]*25
for k in sorted(I):
    im=I[k]; px=list(im.getdata())
    cols=[]; idx={}
    for c in px:
        c5=c565(c)
        if c5 not in idx: idx[c5]=len(cols); cols.append(c5)
    assert len(cols)<=255, (k,len(cols))
    p0=len(pal); pal+=cols; d0=len(data)
    seq=[idx[c565(c)] for c in px]; i=0
    while i<len(seq):
        j=i
        while j<len(seq) and seq[j]==seq[i] and j-i<255: j+=1
        data+=[j-i,seq[i]]; i=j
    MAP[k]=len(ent); ent.append((p0,d0))
L_=['// GENERE par tools/art/export_icons.py -- ne pas modifier a la main','#pragma once','#include <stdint.h>','namespace iart {',
    'struct Icon { uint16_t pal; uint32_t data; };   // 64x64, palette RGB565 + RLE (n, index)',
    'static const Icon ICONS[%d] = {%s};'%(len(ent),','.join('{%d,%d}'%e for e in ent)),
    'static const uint8_t ICON_FOR[25] = {%s};   // index du menu -> icone (255 = icone dessinee par le jeu)'%','.join(map(str,MAP)),
    'static const uint16_t PAL[%d] = {%s};'%(len(pal),','.join('0x%04X'%v for v in pal)),
    'static const uint8_t DATA[%d] = {'%len(data)]
for i in range(0,len(data),40): L_.append(','.join(map(str,data[i:i+40]))+',')
L_+=['};','}  // namespace iart']
open(os.path.join(ROOT,'src','icons_art.h'),'w',encoding='utf-8',newline='\n').write('\n'.join(L_)+'\n')
print('icones',len(ent),'palette',len(pal),'data %.1f Ko'%(len(data)/1024))
