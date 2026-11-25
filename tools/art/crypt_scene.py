import os, sys
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','cover'))
import mk
from crypt import *
from scene import hud_s, shade_ell, W, Hh, HUD
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'preview')
COLS,ROWS=15,7
# 1 = mur (dessus), 2 = face de mur, 0 = sol
GRID=[[1]*COLS]+[[1]+[2]*13+[1]]+[[1]+[0]*13+[1] for _ in range(5)]
FACEV={3:3,5:1,10:2,11:3,12:1}
FLOORV={(3,4):1,(5,11):2,(4,2):3,(6,3):3,(5,5):4,(3,12):2,(6,12):1,(2,9):1}
def is_wall(r,c): return r<0 or c<0 or c>=COLS or (r<ROWS and GRID[r][c]>0)
def ground(t):
    sc=S(W,Hh)
    for r in range(ROWS):
        for c in range(COLS):
            x,y=c*16,HUD+r*16; g=GRID[r][c]
            if g==1:
                m=sum(b<<i for i,b in enumerate((is_wall(r-1,c),is_wall(r,c+1),is_wall(r+1,c) if r+1<ROWS else 1,is_wall(r,c-1))))
                sc.paste(wall_top(m),x,y)
            elif g==2: sc.paste(wall_face(FACEV.get(c,0)),x,y)
            else: sc.paste(slab_floor(FLOORV.get((r,c),0)),x,y)
    # ombre portee des murs sur le sol (haut + cote gauche)
    for y in range(HUD+32,HUD+37):
        for x in range(16,224):
            v=sc.p[y][x]
            if v is not None and v<45 and v%5>1 and ((x+y)%2==0 or y<HUD+35): sc.p[y][x]=v-1
    for y in range(HUD+32,Hh):
        for x in range(16,19):
            v=sc.p[y][x]
            if v is not None and v<45 and v%5>1: sc.p[y][x]=v-1
    return sc
def compose(t=0,action=False):
    sc=ground(t); Y=HUD; items=[]; k4=t%4
    def add(x,y,sp,sh=True,front=0): items.append((y+sp.h+front,x,y,sp,sh))
    sc.paste(crypt_door(),104,Y)
    lights=[]
    for i,tx in enumerate((42,186)):
        sc.paste(wall_torch((k4+i*2)%4),tx,Y+4); lights.append((tx+6,Y+10,50+[0,2,-1,3][(t+i)%4],1.0))
    sc.paste(chain(k4),62,Y+3); sc.paste(chain((k4+2)%4),164,Y+3)
    sc.paste(cobweb(),16,Y+32); sc.paste(cobweb('tr'),208,Y+32)
    sc.paste(puddle(t//2%2,True),30,Y+92); sc.paste(puddle((t//2+1)%2),178,Y+66)
    sc.paste(drip(t%4),38,Y+74)
    for c in (9,10,11): sc.paste(spikes((t//2+c)%4 if not action else 2),c*16,Y+96)
    add(74,Y+12,statue()); add(140,Y+12,statue(True))
    add(16,Y+20,pillar()); add(206,Y+20,pillar()); add(16,Y+64,pillar(True))
    add(102,Y+52,sarcophagus())
    for bx in (78,144):
        add(bx,Y+56,brazier((k4+bx)%4)); lights.append((bx+9,Y+64,40+[1,-1,2,0][(t+bx)%4],0.95))
    add(44,Y+34,urn()); add(172,Y+36,urn(1)); add(186,Y+76,chest()); add(58,Y+86,bones()); add(200,Y+92,tombstone(1))
    if not action:
        bx=46+(t*2)%20
        add(bx,Y+54,bonewalker(t%4)); lights.append((bx+11,Y+56,22,0.8))
        add(160,Y+66+[0,-1,-2,-1][t%4],shroudling(t%4).mirror(),True)
        add(70,Y+100,gravespinner(t%4),True)
        hx,hy=118,Y+84
        add(hx,hy,human('up',t%4,HERO))
    else:
        add(56,Y+52,bonewalker(1,'attack')); lights.append((67,Y+54,22,0.8))
        add(132,Y+60,shroudling(1,'attack').mirror())
        add(104,Y+84,attack('right',1)); hx,hy=112,Y+90
        add(70,Y+98,gravespinner(0,'attack')); sc.paste(webshot(2),88,Y+96)
    lights.append((hx+8 if not action else 120,hy+12 if not action else Y+100,32,0.75))   # petite aura du heros
    items.sort(key=lambda a:(a[0],a[1]))
    for b,x,y,sp,sh in items:
        if sh: shade_ell(sc,x+sp.w//2,y+sp.h-1,max(3,sp.w//2-2),2)
        sc.paste(sp,x,y)
    return light(sc,lights,t)
def light(sc,lights,t):
    imgs=[sc.image(p) for p in (DARK,MID,LIT)]
    px=[im.load() for im in imgs]
    out=Image.new('RGBA',(W,Hh),tuple(DARK[BLACK])+(255,)); o=out.load()
    for y in range(HUD,Hh):
        for x in range(W):
            Lv=0
            for (lx,ly,r,st) in lights:
                d=math.hypot(x-lx,(y-ly)*1.2)
                if d<r: Lv=max(Lv,(1-d/r)*st)
            q=Lv*2.7+(BAYER[y%4][x%4]/16-0.5)*0.32
            k=2 if q>=1.2 else (1 if q>=0.42 else 0)
            c=px[k][x,y]
            if c[3]==0: c=tuple(DARK[BLACK])+(255,)
            if Lv>0.45:
                a=(Lv-0.45)*1.4
                c=(min(255,int(c[0]+70*a)),min(255,int(c[1]+34*a)),c[2],255)
            o[x,y]=c
    # emissif: runes des statues
    for (rx,ry) in ((81,HUD+51),(147,HUD+51)):
        for i in range(4):
            for dy in range(3):
                x=rx+i*3; y=ry+dy
                if 0<=x<W and (x+dy)%2==0: o[x,y]=tuple(PAL[ix(Bl,H)])+(255,)
    out.alpha_composite(hud_s(t,(3,5)).image(PAL),(0,0))
    mk.text(out,"x27",17,17,1,(255,248,232)); mk.text(out,"x1",63,17,1,(255,248,232))
    return out
def up(im,sc=4): return im.convert('RGB').resize((im.width*sc,im.height*sc),Image.NEAREST)
if __name__=='__main__':
    up(compose(1)).save(f'{OUT}/O_crypt_room.png')
    up(compose(2,action=True)).save(f'{OUT}/O_crypt_action.png')
    fr=[up(compose(t),3) for t in range(12)]
    fr[0].save(f'{OUT}/crypt.gif',save_all=True,append_images=fr[1:],duration=120,loop=0)
    print('ok')
