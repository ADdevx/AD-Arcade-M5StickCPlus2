import os, sys
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','cover'))
import mk
from forest import *
from scene import hud_s, shade_ell, dialogbox, W, Hh, HUD
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'preview')
COLS,ROWS=15,7
def vgrid(): return [[0]*(COLS+1) for _ in range(ROWS+1)]
# --- carte en sommets (autotiling par coins) ---
WV=vgrid(); PV=vgrid()
for r in range(2,ROWS+1):
    for c in (9,10,11): WV[r][c]=1
for c in (8,12): WV[2][c]=1; WV[3][c]=1           # bassin sous la cascade
for c in list(range(0,9))+[12,13]: PV[4][c]=1      # chemin
for (r,c) in ((5,3),(6,3),(7,3),(4,14),(3,14),(3,15),(4,15)): PV[r][c]=1
def tmask(V,r,c): return V[r][c]|(V[r][c+1]<<1)|(V[r+1][c]<<2)|(V[r+1][c+1]<<3)
FLOORV={(r,c):(r*7+c*3+r*c)%4 for r in range(ROWS) for c in range(COLS)}
def ground(t):
    sc=S(W,Hh); k=(t//1)%4
    for r in range(ROWS):
        for c in range(COLS):
            x,y=c*16,HUD+r*16
            if r<2: sc.paste(cliff_t(r,(c*5+1)%4 if c not in (8,11) else 2),x,y); continue
            wm=tmask(WV,r,c); pm=tmask(PV,r,c)
            if wm: sc.paste(water_c(wm,k),x,y)
            elif pm: sc.paste(path_c(pm),x,y)
            else: sc.paste(floor_t(FLOORV[(r,c)]),x,y)
    return sc
def compose(t=0,mode='day',action=False,dialog=None,hero=None):
    sc=ground(t); Y=HUD; items=[]
    def add(x,y,sp,sh=True,front=0): items.append((y+sp.h+front,x,y,sp,sh))
    k4=t%4
    # cascade (derriere tout)
    sc.paste(waterfall(k4),144,Y-12)
    # arbres
    add(-8,Y-6,oak()); add(26,Y-14,pine()); add(206,Y-12,maple()); add(98,Y-2,birch())
    add(178,Y-16,pine()); add(-6,Y+64,oak(True))
    # decor
    add(66,Y+28,bush()); add(186,Y+34,bush(False))
    add(120,Y+34,rock_s()); add(186,Y+86,rock_b()); add(112,Y+96,stump())
    add(36,Y+92,hollow_log())
    add(84,Y+94,mush_red()); add(100,Y+82,fern(t//3%2)); add(224,Y+60,fern((t//3+1)%2))
    add(124,Y+100,mush_glow((t//4)%2),True); add(160,Y+96,tallgrass(t//3%2)); add(212,Y+96,tallgrass((t//3+1)%2)); add(228,Y+96,mush_brown())
    add(56,Y+70,tallgrass((t//3)%2)) if not action else None
    add(128,Y+51,bridge(),False,-30)
    # personnages
    fly_y=Y+12+int(3*math.sin(t*0.9))
    if not action:
        hx=hero if hero is not None else 70+t*2
        add(hx,Y+44,human('right',t%4,HERO))
        add(60+((t*2)%24),Y+86,sporeling(t%4))
        add(214-t,Y+44,thornboar(t%4).mirror())
        add(150,fly_y+56,leafbat(t%4),False,60)
    else:
        a=human('right',0,HERO)
        add(168-8,Y+44-6,attack('right',1))            # heros frappe sur le pont
        add(188,Y+44,thornboar(1,'attack').mirror())
        add(58,Y+62,sporeling(1,'attack'))
        add(96,Y+44,burst(leafbat(0),1),False,60)  # chauve-souris abattue
        add(150,Y+66-4,leafbat(0,'dive'),False,60)
    items.sort(key=lambda a:(a[0],a[1]))
    for b,x,y,sp,sh in items:
        if sh: shade_ell(sc,x+sp.w//2,y+sp.h-1,max(3,sp.w//2-2),2)
        sc.paste(sp,x,y)
    # feuilles qui tombent (de l'erable)
    if mode!='night':
        for i in range(6):
            lx=(200+i*9+int(10*math.sin((t+i*5)*0.5)))%W; ly=Y+10+((t*3+i*19)%90)
            sc.paste(leaf((t+i)%4,[Tc,E,Tc,G][i%4]),lx,ly)
    if mode=='day': pal=PAL
    elif mode=='dusk': pal=tint(PAL,(1.05,0.8,0.72),0.12,(190,90,60))
    else: pal=tint(PAL,(0.38,0.52,0.8),0.2,(8,24,52))
    im=sc.image(pal); bg=Image.new('RGBA',(W,Hh),tuple(pal[BLACK])+(255,)); bg.alpha_composite(im)
    bg.alpha_composite(hud_s(t,(4,5) if not action else (3,5)).image(PAL),(0,0))
    mk.text(bg,"x27",17,17,1,(255,248,232)); mk.text(bg,"x1",63,17,1,(255,248,232))
    if mode=='night': night_fx(bg,t)
    if dialog: dialogbox(bg,dialog,pal,t)
    return bg
def glow_at(bg,lx,ly,rad,col,strength=1.0):
    d=bg.load()
    for y in range(int(ly-rad),int(ly+rad)+1):
        for x in range(int(lx-rad),int(lx+rad)+1):
            if 0<=x<W and HUD<=y<Hh:
                dd=math.hypot(x-lx,(y-ly)*1.15)/rad
                if dd<1:
                    a=(1-dd)**1.6*strength
                    if dd>0.55 and (x+y)%2: a*=0.5          # bord tramé
                    r,g,b,al=d[x,y]; d[x,y]=(min(255,int(r+col[0]*a)),min(255,int(g+col[1]*a)),min(255,int(b+col[2]*a)),al)
def night_fx(bg,t):
    glow_at(bg,130,HUD+106,16,(60,140,220),0.9+0.3*((t//4)%2))     # champignons lumineux
    glow_at(bg,160,HUD+30,22,(40,70,120),0.5)
    glow_at(bg,130,HUD+60,26,(30,30,10),0.0)                         # reflet cascade
    rng=random.Random(3)
    for i in range(14):                                              # lucioles
        bx=rng.randrange(8,232); by=rng.randrange(HUD+8,Hh-8)
        x=int(bx+6*math.sin((t+i*3)*0.35)); y=int(by+4*math.cos((t+i*2)*0.27))
        ph=(t+i)%6
        if ph==5: continue
        glow_at(bg,x+3,y+3,7,(150,190,60),0.9 if ph in (1,2) else 0.5)
        ff=firefly([0,1,2,3,0][ph]).image(PAL); bg.alpha_composite(ff,(x,y))
def up(im,sc=4): return im.convert('RGB').resize((im.width*sc,im.height*sc),Image.NEAREST)
if __name__=='__main__':
    up(compose(2,'day')).save(f'{OUT}/J_forest_day.png')
    up(compose(3,'day',action=True)).save(f'{OUT}/J_forest_action.png')
    up(compose(5,'dusk',hero=90)).save(f'{OUT}/J_forest_dusk.png')
    up(compose(6,'night',hero=96)).save(f'{OUT}/J_forest_night.png')
    fr=[up(compose(t,'day'),3) for t in range(16)]
    fr[0].save(f'{OUT}/forest.gif',save_all=True,append_images=fr[1:],duration=110,loop=0)
    fn=[up(compose(t,'night',hero=96),3) for t in range(12)]
    fn[0].save(f'{OUT}/forest_night.gif',save_all=True,append_images=fn[1:],duration=130,loop=0)
    print('ok')
