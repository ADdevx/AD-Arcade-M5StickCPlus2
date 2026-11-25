import os, sys
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','cover'))
import mk
from boss import *
from scene import hud_s, shade_ell, W, Hh, HUD
from forest_scene import glow_at
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'preview')
COLS,ROWS=15,7
GRID=[[1]*COLS]+[[1]+[2]*13+[1]]+[[1]+[0]*13+[1] for _ in range(5)]
LV=[[0]*(COLS+1) for _ in range(ROWS+1)]
for r in range(4,8):
    for c in (1,2,3): LV[r][c]=1
    for c in (12,13,14): LV[r][c]=1
LV[3][13]=1; LV[3][14]=1; LV[7][4]=1; LV[7][11]=1
def tmask(r,c): return LV[r][c]|(LV[r][c+1]<<1)|(LV[r+1][c]<<2)|(LV[r+1][c+1]<<3)
FV={(3,5):3,(5,6):2,(4,9):3,(6,7):1,(2,3):2,(3,10):1,(6,9):3}
def is_wall(r,c): return r<0 or c<0 or c>=COLS or (r<ROWS and GRID[r][c]>0)
def ground(t):
    sc=S(W,Hh); k=t%4
    for r in range(ROWS):
        for c in range(COLS):
            x,y=c*16,HUD+r*16; g=GRID[r][c]
            if g==1:
                m=sum(b<<i for i,b in enumerate((is_wall(r-1,c),is_wall(r,c+1),is_wall(r+1,c) if r+1<ROWS else 1,is_wall(r,c-1))))
                sc.paste(wall_top(m),x,y)
            elif g==2: sc.paste(basalt_face(1 if c in (3,11) else 0),x,y)
            else:
                lm=tmask(r,c)
                sc.paste(lava_c(lm,k) if lm else basalt_floor(FV.get((r,c),0)),x,y)
    for y in range(HUD+32,HUD+36):
        for x in range(16,224):
            v=sc.p[y][x]
            if v is not None and v<45 and v%5>1 and ((x+y)%2==0 or y<HUD+34): sc.p[y][x]=v-1
    return sc
LAVA_GLOW=[(24,HUD+100),(40,HUD+88),(212,HUD+84),(222,HUD+104)]
def compose(t=0,scene='p1',hp=1.0):
    sc=ground(t); Y=HUD; items=[]; k=t%4; glows=list(LAVA_GLOW)
    def add(x,y,sp,sh=True,front=0): items.append((y+sp.h+front,x,y,sp,sh))
    sc.paste(rune_circle(k if scene!='p1' else t//3%4),88,Y+62)
    gx,gy=78,Y-10
    if scene=='p1':
        add(gx,gy,golem('idle',k,1)); add(112,Y+84,human('up',t%4,HERO)); glows.append((120,Y+30,0))
    elif scene=='p2':
        add(gx,gy,golem('slam',0,2)); sc.paste(shockwave(1+k%3),72,Y+70)
        for (ex,ey,kk) in ((40,Y+40,(k+1)%4),(186,Y+44,(k+3)%4)): add(ex,ey,eruption(kk),False); glows.append((ex+8,ey+36,1))
        add(150,Y+82,roll(k%2)); glows.append((120,Y+40,1))
    elif scene=='p3':
        add(gx,gy,golem('throw1',1,3)); add(150,Y+52,boulder(k,3),False,80); sc.paste(fire_trail(k),132,Y+56)
        add(88,Y+76,attack('up',1)); glows.append((120,Y+40,2)); glows.append((158,Y+60,1))
    else:
        add(gx,gy,death(3)); add(112,Y+82,victory(t%2)); add(150,Y+76,heart_container(t%2)); glows.append((122,Y+40,1))
    if scene!='p1':
        rng=random.Random(t)
        for i in range(10): sc.paste(ember(rng.randrange(4)),rng.randrange(16,224),Y+rng.randrange(30,108))
    items.sort(key=lambda a:(a[0],a[1]))
    for b,x,y,sp,sh in items:
        if sh: shade_ell(sc,x+sp.w//2,y+sp.h-1,max(3,min(18,sp.w//2-2)),2)
        sc.paste(sp,x,y)
    im=sc.image(ARENA); bg=Image.new('RGBA',(W,Hh),tuple(ARENA[BLACK])+(255,)); bg.alpha_composite(im)
    for g in glows:
        lx,ly=g[0],g[1]
        if len(g)==2: glow_at(bg,lx,ly,24,(90,30,0),0.55+0.1*(t%2))
        else: glow_at(bg,lx,ly,[20,26,32][g[2]],(110,50,0),0.6+0.15*(t%2))
    # barre du boss
    if scene!='win':
        pass
    bg.alpha_composite(hud_s(t,(5,5) if scene=='p1' else ((2,5) if scene=='p3' else (3,5))).image(PAL),(0,0))
    mk.text(bg,"x27",17,17,1,(255,248,232)); mk.text(bg,"x1",63,17,1,(255,248,232))
    if scene!='win':
        bg.alpha_composite(boss_bar(hp).image(PAL),(80,3))
        mk.text(bg,"EMBER GOLEM",82,14,1,(255,214,120))
    return bg
def up(im,sc=4): return im.convert('RGB').resize((im.width*sc,im.height*sc),Image.NEAREST)
if __name__=='__main__':
    up(compose(1,'p1',1.0)).save(f'{OUT}/R_boss_phase1.png')
    up(compose(2,'p2',0.62)).save(f'{OUT}/R_boss_phase2.png')
    up(compose(1,'p3',0.2)).save(f'{OUT}/R_boss_phase3.png')
    up(compose(1,'win',0)).save(f'{OUT}/R_boss_victory.png')
    fr=[up(compose(t,s,h),3) for s,h in (('p1',1.0),('p2',0.62),('p3',0.2),('win',0)) for t in range(6)]
    fr[0].save(f'{OUT}/boss.gif',save_all=True,append_images=fr[1:],duration=140,loop=0)
    print('ok')
