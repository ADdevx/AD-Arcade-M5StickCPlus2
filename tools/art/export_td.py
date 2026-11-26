# Export de l'art + des 12 niveaux de POCKET SIEGE vers src/td_art.h
# Lancer : cd tools/art && python export_td.py
import os, hashlib
from td_worlds_sheets import *
from export_zelda import encode, palette          # meme format de sprites que Emberwood (4 bits / RLE)
ROOT=os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..'))
OUTH=os.path.join(ROOT,'src','td_art.h')

SPR=[]; BYH={}; NAMES={}
def reg(s,name=None):
    k=hashlib.md5(repr((s.w,s.h,s.p)).encode()).hexdigest()
    if k in BYH and not name: return BYH[k]
    i=len(SPR); SPR.append(s); BYH.setdefault(k,i)
    if name: NAMES[name]=i
    return i
def seq(frames,name):
    i0=len(SPR); SPR.extend(frames); NAMES[name]=i0; return i0

# ---------------- tours : (type*3 + niveau-1)*2 + frame
TW=[tower_archer,tower_cannon,tower_frost,tower_storm]
seq([f(l,k) for f in TW for l in (1,2,3) for k in (0,1)],'TOWER')
seq([pad(),pad(True)],'PAD')
def icon_upgrade():
    s=S(22,22); m=m_ell(0,0,21,21); sphere(s,m,G,0.4)
    for p in m_poly([(11,3),(18,11),(14,11),(14,18),(8,18),(8,11),(4,11)]): s.set(*p,GOLD)
    s.set(10,6,WHITE); return outline(s)
def icon_sell():
    s=S(22,22); m=m_ell(0,0,21,21); sphere(s,m,Tc,0.3)
    s.paste(coin(0),6,6); return outline(s)
seq([ring_btn(f(1)) for f in TW]+[ring_btn(f(1),sel=True) for f in TW]+[icon_upgrade(),icon_sell()],'RING')   # 0-3, sel 4-7, 8 up, 9 vendre
# ---------------- ennemis (regardent a droite) : 4 frames chacun
seq([slime(k) for k in range(4)],'E_SLIME'); seq([goblin(k) for k in range(4)],'E_GOBLIN'); seq([orc_knight(k) for k in range(4)],'E_KNIGHT')
seq([bat(k) for k in range(4)],'E_BAT'); seq([shaman(k%2,cast=(k>=2)) for k in range(4)],'E_SHAMAN'); seq([ogre(k) for k in range(4)],'E_OGRE')
# ---------------- effets
reg(arrow(),'FX_ARROW'); reg(cannonball(),'FX_BALL'); reg(frostbolt(),'FX_FROST')
seq([explosion(k) for k in range(4)],'FX_BOOM'); seq([frostburst(k) for k in range(3)],'FX_ICE'); seq([coin(k) for k in range(4)],'FX_COIN')
reg(heart_s2(),'ICON_HEART'); seq([star_icon(False),star_icon(True)],'ICON_STAR')
seq([level_node(s) for s in range(5)],'NODE'); seq([shop_icon(k) for k in ('damage','range','gold','lives','speed')],'SHOP')
seq([rift_portal(k) for k in range(4)],'PORTAL'); seq([castle(0),castle(1)],'CASTLE')
# ---------------- decor par monde
WORLDS=['meadow','desert','snow','volcano']
DEC=[[reg(s) for _,s in WORLD_DECOR[w]] for w in WORLDS]
DEC[0]+= [reg(flowers_tile(0))] if False else []
seq([vent(0),vent(1)],'VENT')
# ---------------- tuiles : par monde 4 sols + 15 masques de chemin
TILEBASE=[]
for w in WORLDS:
    i0=len(SPR)
    for v in range(4): SPR.append(GROUNDS[w](v))
    for m in range(1,16): SPR.append(world_path(w,m))
    TILEBASE.append(i0); NAMES['TILES_%s'%w.upper()]=i0
# HUD
def hud_bar():
    s=S(W,HUD); paint(s,m_rect(0,0,W-1,HUD-1),Wd,tex='hatch')
    for x in range(W): s.set(x,HUD-1,ix(Wd,O)); s.set(x,HUD-2,GOLD if x%2==0 else ix(E,B)); s.set(x,0,ix(Wd,L))
    s.paste(heart_s2(),6,7); s.paste(coin(0),46,7); frame_box(s,W-28,2,24,18)
    return s
reg(hud_bar(),'HUD_BG')
def ff_icon(on):
    s=S(16,12)
    for i in range(2):
        for p in m_poly([(1+i*7,1),(8+i*7,6),(1+i*7,11)]): s.set(*p,ix(G,H if on else L) if True else 0)
    return outline(s)
seq([ff_icon(False),ff_icon(True)],'ICON_FF')

# ---------------- niveaux
LEVELS=[
 [(0,40),(104,40),(104,80),(240,80)],
 [(0,24),(88,24),(88,88),(168,88),(168,40),(240,40)],
 [(0,88),(64,88),(64,32),(136,32),(136,80),(192,80),(192,40),(240,40)],
 [(0,88),(56,88),(56,24),(136,24),(136,72),(240,72)],
 [(0,32),(120,32),(120,96),(200,96),(200,48),(240,48)],
 [(0,72),(40,72),(40,24),(96,24),(96,96),(152,96),(152,24),(208,24),(208,64),(240,64)],
 [(0,40),(40,40),(40,96),(120,96),(120,24),(200,24),(200,72),(240,72)],
 [(0,96),(72,96),(72,48),(152,48),(152,96),(240,96)],
 [(0,24),(72,24),(72,96),(160,96),(160,40),(240,40)],
 [(0,96),(48,96),(48,24),(192,24),(192,88),(240,88)],
 [(0,56),(64,56),(64,24),(128,24),(128,96),(184,96),(184,56),(240,56)],
 [(0,24),(56,24),(56,96),(136,96),(136,32),(200,32),(200,80),(240,80)],
]
def seg_dist(px,py,a,b_):
    ax,ay=a; bx,by=b_; dx,dy=bx-ax,by-ay; L2=dx*dx+dy*dy or 1
    t=max(0,min(1,((px-ax)*dx+(py-ay)*dy)/L2)); return math.hypot(px-(ax+dx*t),py-(ay+dy*t))
def pdist(px,py,pts): return min(seg_dist(px,py,a,b_) for a,b_ in zip(pts,pts[1:]))
LVDATA=[]
for li,pts in enumerate(LEVELS):
    w=li//3; V=vgrid_from(pts); base=TILEBASE[w]
    tiles=[]
    for r in range(7):
        row=[]
        for c in range(15):
            m=V[r][c]|(V[r][c+1]<<1)|(V[r+1][c]<<2)|(V[r+1][c+1]<<3)
            row.append(base+4+m-1 if m else base+(r*3+c*5+li)%4)
        tiles.append(row)
    ex,ey=pts[-1]; cast=(196,ey-40); sx,sy=pts[0]
    def on_path(x,y):
        r,c=int(y)//16,int(x)//16
        if not (0<=r<7 and 0<=c<15): return False
        m=V[r][c]|(V[r][c+1]<<1)|(V[r+1][c]<<2)|(V[r+1][c+1]<<3)
        return m and cfield(m,int(x)%16,int(y)%16,11)>=0.38
    def clear_of_path(x,y,rx,ry): return not any(on_path(x+dx,y+dy) for dx in (-rx,0,rx) for dy in (-ry,0,ry))
    def free_zone(x,y):
        if x>186 and abs(y-ey)<34: return False          # chateau
        if x<34 and abs(y-sy)<30: return False           # portail
        return True
    rng=random.Random(li*7+3); cands=[]
    for y in range(36,106,6):
        for x in range(14,228,6):
            d=pdist(x,y,pts)
            if 20<=d<=42 and free_zone(x,y) and clear_of_path(x,y,12,8): cands.append((d+rng.random()*6,x,y))
    cands.sort(); pads=[]
    for d,x,y in cands:
        if all(math.hypot(x-px,y-py)>=30 for px,py in pads): pads.append((x,y))
        if len(pads)>=7: break
    pads.sort(key=lambda p:(p[0],p[1]))
    dec=[]; dl=DEC[w]
    for t_ in range(400):
        x=rng.randrange(-4,226); y=rng.randrange(-6,100)
        sp=SPR[dl[rng.randrange(len(dl))]] if False else None
        k=rng.randrange(len(dl)); s_=SPR[dl[k]]
        cx,cy=x+s_.w//2,y+s_.h-3
        if pdist(cx,cy,pts)<20 or not free_zone(cx,cy) or cy<8 or cy>110 or not clear_of_path(cx,cy,s_.w//2,4): continue
        if any(math.hypot(cx-px,cy-py)<22 for px,py in pads): continue
        if any(math.hypot(cx-(dx+SPR[ds].w//2),cy-(dy+SPR[ds].h-3))<18 for ds,dx,dy in dec): continue
        dec.append((dl[k],x,y))
        if len(dec)>=7: break
    LVDATA.append((w,pts,pads,dec,tiles,cast))

# ---------------- ecriture
blob=[]; ent=[]
for s in SPR:
    fmt,nl,data=encode(s); off=len(blob); blob+=data; ent.append((s.w,s.h,fmt,1,nl,off))
L_=['// GENERE par tools/art/export_td.py -- ne pas modifier a la main','#pragma once','#include <stdint.h>','namespace tdart {']
L_.append('static const uint16_t PAL[48] = {%s};'%','.join('0x%04X'%v for v in palette(PAL)))
L_.append('struct Spr { uint8_t w, h, fmt, anim, nlut; uint32_t off; };')
L_.append('static const Spr SPR[%d] = {%s};'%(len(ent),','.join('{%d,%d,%d,%d,%d,%d}'%e for e in ent)))
L_.append('static const uint8_t BLOB[%d] = {'%len(blob))
for i in range(0,len(blob),40): L_.append(','.join(map(str,blob[i:i+40]))+',')
L_.append('};')
for n,i in sorted(NAMES.items(),key=lambda a:a[1]): L_.append('static const uint16_t %s = %d;'%(n,i))
L_.append('struct Level { uint8_t world, npts, npads, ndec; int16_t pts[12][2]; int16_t pads[8][2]; uint16_t dec[8][3]; uint16_t tiles[7][15]; int16_t castle[2]; };')
L_.append('static const Level LEVELS[%d] = {'%len(LVDATA))
for (w,pts,pads,dec,tiles,cast) in LVDATA:
    P=pts+[(0,0)]*(12-len(pts)); Q=pads+[(0,0)]*(8-len(pads)); D=dec+[(0,0,0)]*(8-len(dec))
    enc=lambda v: v & 0xFFFF
    L_.append('{%d,%d,%d,%d,{%s},{%s},{%s},{%s},{%d,%d}},'%(w,len(pts),len(pads),len(dec),
        ','.join('{%d,%d}'%p for p in P),','.join('{%d,%d}'%p for p in Q),','.join('{%d,%d,%d}'%(a,enc(b_),enc(c)) for a,b_,c in D),
        ','.join('{'+','.join(map(str,r))+'}' for r in tiles),cast[0],cast[1]))
L_.append('};'); L_.append('static const int NLEVELS = %d;'%len(LVDATA)); L_.append('}  // namespace tdart')
open(OUTH,'w',encoding='utf-8',newline='\n').write('\n'.join(L_)+'\n')
print('sprites',len(SPR),'blob %.1f Ko'%(len(blob)/1024),'pads',[len(d[2]) for d in LVDATA],'decor',[len(d[3]) for d in LVDATA])
