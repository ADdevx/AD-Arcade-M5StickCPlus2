# EMBER PINBALL : geometrie du plateau (physique) + art pixel du plateau, des panneaux et des pieces mobiles
# Le meme fichier definit les murs et les dessine : l'art colle toujours a la physique.
import os, sys
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','cover'))
from forest import *
import mk
TW,TH=128,300
# ---------------------------------------------------------------- geometrie (coordonnees du plateau)
K_WALL,K_SLING,K_TARGET,K_GATE=0,1,2,3
SEGS=[]
def seg(a,b,k=K_WALL,tag=0): SEGS.append((a[0],a[1],b[0],b[1],k,tag))
seg((4,300),(4,64)); seg((124,64),(124,300)); seg((112,300),(112,96))
arc=[(64+math.cos(math.radians(180+i*180/16))*60,64+math.sin(math.radians(180+i*180/16))*60) for i in range(17)]
for a,b in zip(arc,arc[1:]): seg(a,b)
seg((4,232),(32,256)); seg((112,232),(84,256))
L1,L2,L3=(16,198),(16,224),(30,236); seg(L1,L2); seg(L2,L3); seg(L3,L1,K_SLING)
R1,R2,R3=(100,198),(100,224),(86,236); seg(R1,R2); seg(R2,R3); seg(R3,R1,K_SLING)
for x in (44,60,76,92): seg((x,18),(x,32))
for i,(y0,y1) in enumerate(((138,150),(154,166),(170,182))): seg((10,y0),(10,y1),K_TARGET,i)
# (pas de portillon : une bille qui retombe dans le couloir revient au lanceur)
BUMPERS=[(44,94,8),(78,90,8),(61,120,8)]
SAUCER=(94,150,5)
LANES=[(52,26),(68,26),(84,26)]                 # centres des couloirs (capteurs)
FLIP_L=(34,258); FLIP_R=(82,258); FLIP_LEN=20
INSERTS=[(46,228),(56,231),(66,231),(76,228)]   # x2 x3 x4 x5
SHOOT=(118,290)

# ---------------------------------------------------------------- art du plateau
def rail(s,a,b,w=3):
    m=m_line(a[0],a[1],b[0],b[1],w)
    for (x,y) in m:
        if 0<=x<TW and 0<=y<TH:
            # metal : clair en haut-gauche
            dx,dy=b[0]-a[0],b[1]-a[1]; L_=math.hypot(dx,dy) or 1
            side=((x-a[0])*(-dy)+(y-a[1])*dx)/L_
            s.set(x,y,ix(St,H) if side<-0.6 else (ix(St,L) if side<0.4 else ix(St,S_)))
def text(s,t,x,y,col,shadow=None):
    G=mk.G; cx=x
    for ch in t:
        g=G.get(ch.upper(),G[' '])
        for r,row in enumerate(g):
            for k,bit in enumerate(row):
                if bit=='1':
                    if shadow is not None: s.set(cx+k+1,y+r+1,shadow)
                    s.set(cx+k,y+r,col)
        cx+=6
def table():
    s=S(TW,TH)
    for y in range(TH):
        for x in range(TW):
            n=fnoise(x,y,200)+0.5*fnoise(x*0.5,y*0.5,201)
            v=0.55+n*0.45+(y/TH)*0.35
            s.set(x,y,ix(Bl,dt(v,x,y,0,1)) if v>0.3 else BLACK)
    rng=random.Random(4)
    for _ in range(70):
        x,y=rng.randrange(6,122),rng.randrange(6,296); s.set(x,y,WHITE if rng.random()<0.3 else ix(Bl,L))
    # embleme de braise au centre
    for (x,y) in m_ell(36,150,86,206):
        d=math.hypot((x-61)/25,(y-178)/28)
        if d<1:
            t=dt(3.6-d*3.0+0.3*fnoise(x,y,9),x,y,0,4)
            s.set(x,y,[ix(Tc,O),ix(Tc,S_),ix(Tc,B),ix(E,H),GOLD][t])
    flame=m_poly([(61,150),(70,168),(66,166),(72,186),(61,204),(50,186),(56,166),(52,168)])
    for (x,y) in flame: s.set(x,y,GOLD if (x+y)%3 else WHITE) if abs(x-61)<4 and y>170 else s.set(x,y,ix(E,H) if (x+y)%2 else GOLD)
    text(s,"EMBER",46,208,GOLD,ix(Tc,O))
    # fleches vers les bumpers et le trou
    for (cx,cy,ang) in ((30,128,-60),(92,128,-120),(92,168,-90)):
        for i in range(3):
            for j in range(-3+i,4-i):
                a=math.radians(ang); x=int(cx+math.cos(a)*i*2-math.sin(a)*j); y=int(cy+math.sin(a)*i*2+math.cos(a)*j)
                s.set(x,y,ix(Tc,S_))
    # emplacements de lumieres (eteintes ; allumees par le jeu)
    for (x,y) in LANES:
        for p in m_ell(x-3,y+12,x+3,y+18): s.set(*p,ix(Tc,O))
    for (x,y) in INSERTS:
        for p in m_ell(x-4,y-3,x+4,y+3): s.set(*p,ix(Tc,O))
    # trou (saucer)
    sx,sy,sr=SAUCER
    for p in m_ell(sx-sr-2,sy-sr-2,sx+sr+2,sy+sr+2): s.set(*p,ix(St,B))
    for p in m_ell(sx-sr,sy-sr,sx+sr,sy+sr): s.set(*p,BLACK)
    s.set(sx-2,sy-sr-2,ix(St,H))
    # fentes des cibles
    for p in m_rect(5,136,9,184): s.set(*p,BLACK)
    # couloir de lancement
    for y in range(96,300):
        for x in range(113,124): s.set(x,y,ix(St,O) if (x+y)%5 else ix(St,S_))
    for y in range(110,290,14):
        for x in range(115,122): s.set(x,y,ix(Tc,S_))
    # slingshots (plastique rouge, caoutchouc blanc sur la face qui renvoie)
    for (A,Bq,C) in ((L1,L2,L3),(R1,R2,R3)):
        for (x,y) in m_poly([A,Bq,C]): s.set(x,y,ix(Tc,dt(2.6-((y-198)/40),x,y,1,4)))
        for p in m_line(C[0],C[1],A[0],A[1],2): s.set(*p,WHITE)
    # rails (murs)
    for (x0,y0,x1,y1,k,tag) in SEGS:
        if k in (K_WALL,K_GATE): rail(s,(x0,y0),(x1,y1),3 if k==K_WALL else 1)
    # tableau du bas : zone de vidange sombre
    for y in range(262,300):
        for x in range(36,82):
            if s.get(x,y) is not None and ramp_of(s.get(x,y))==Bl: s.set(x,y,BLACK if (x+y)%2 else ix(Bl,O))
    return s

# ---------------------------------------------------------------- pieces mobiles
def ball():
    s=S(8,8); sphere(s,m_ell(0,0,7,7),St,0.6,lo=1); s.set(2,2,WHITE); s.set(3,2,WHITE); s.set(2,3,ix(St,H)); return s
def bumper(lit):
    s=S(20,20)
    for p in m_ell(0,0,19,19): s.set(*p,ix(St,S_))
    for p in m_ell(2,2,17,17): s.set(*p,WHITE if lit else ix(Pl,L))       # anneau en caoutchouc
    sphere(s,m_ell(4,3,15,14),Tc if not lit else E,0.4 if not lit else 1.0)
    for p in m_ell(7,6,12,11): s.set(*p,GOLD if lit else ix(Tc,H))
    s.set(8,7,WHITE)
    return outline(s)
def target(up):
    s=S(5,13)
    if up:
        for p in m_rect(0,0,4,12): s.set(*p,ix(E,L) if p[0]<2 else ix(E,B))
        for y in range(0,13,4): s.set(2,y+1,GOLD)
    else:
        for p in m_rect(0,0,4,12): s.set(*p,ix(St,O))
    return s

# ---------------------------------------------------------------- panneaux lateraux (56x135)
def panel_left():
    s=S(56,135)
    paint(s,m_rect(0,0,55,134),Wd,tex='hatch')
    for p in m_rect(4,4,51,130): s.set(*p,ix(St,O))
    for p in m_rect(5,5,50,129): s.set(*p,BLACK)
    for x in range(4,52): s.set(x,4,ix(St,S_)); s.set(x,130,ix(St,L))
    for (cx,cy) in ((2,2),(53,2),(2,132),(53,132)): s.set(cx,cy,GOLD)
    text(s,"EMBER",13,10,GOLD,ix(Tc,O)); text(s,"PINBALL",7,20,ix(E,H),ix(Tc,O))
    for x in range(8,48): s.set(x,30,ix(Tc,S_))
    return s
def dragon_head():
    s=S(44,40)
    head=m_poly([(4,20),(14,8),(30,6),(40,14),(42,22),(30,24),(22,32),(8,30)])
    sphere(s,head,Tc,0.2)
    for (x,y) in head:
        if (x+y*2)%7==0 and y>12: s.set(x,y,ix(Tc,S_))                        # ecailles
    for p in m_poly([(16,8),(10,0),(20,6)]): s.set(*p,ix(E,L))                 # cornes
    for p in m_poly([(24,6),(22,0),(30,5)]): s.set(*p,ix(E,L))
    for p in m_ell(26,11,31,15): s.set(*p,GOLD)
    s.set(28,12,BLACK); s.set(29,12,BLACK); s.set(27,11,WHITE)
    for x in range(30,42): s.set(x,21,ix(Tc,O))                               # gueule
    for (x,y) in ((32,22),(35,22),(38,22)): s.set(x,y,WHITE)
    for i in range(10):                                                         # souffle de braise
        y=22+i//3; x=42+i
        if x<44: s.set(x,y,GOLD)
    return outline(s)
def panel_right():
    s=S(56,135)
    paint(s,m_rect(0,0,55,134),Wd,tex='hatch')
    for p in m_rect(4,4,51,130): s.set(*p,ix(St,O))
    for p in m_rect(5,5,50,129): s.set(*p,ix(Bl,O))
    for y in range(5,130):
        for x in range(5,51):
            if (x*7+y*3)%23==0: s.set(x,y,ix(Bl,S_))
    s.paste(dragon_head(),7,12)
    for i in range(30):                                                         # braises qui montent
        x=8+(i*13)%40; y=60+(i*29)%60; s.set(x,y,GOLD if i%3 else ix(Tc,H))
    for (cx,cy) in ((2,2),(53,2),(2,132),(53,132)): s.set(cx,cy,GOLD)
    return s
def flipper_preview(s,piv,ang,left):
    for t in range(FLIP_LEN+1):
        x=piv[0]+math.cos(ang)*t; y=piv[1]+math.sin(ang)*t; w=3.2-t*0.09
        for p in m_ell(int(x-w),int(y-w),int(x+w),int(y+w)): s.set(*p,ix(Tc,B) if t<FLIP_LEN-1 else WHITE)
    for t in range(FLIP_LEN+1):
        x=piv[0]+math.cos(ang)*t; y=piv[1]+math.sin(ang)*t; s.set(int(x),int(y)-1,WHITE)

if __name__=='__main__':
    OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'preview')
    t=table()
    for (x,y,r) in BUMPERS: t.paste(bumper(True if x==44 else False),x-10,y-10)
    for i in range(3): t.paste(target(i!=1),8,138+i*16)
    flipper_preview(t,FLIP_L,math.radians(28),True); flipper_preview(t,FLIP_R,math.radians(152),False)
    t.paste(ball(),58,150)
    # ecran de jeu (camera en bas du plateau)
    scr=S(240,135); scr.paste(panel_left(),0,0); scr.paste(panel_right(),184,0)
    cam=165
    for y in range(135):
        for x in range(TW): scr.set(56+x,y,t.get(x,y+cam))
    im=scr.image(); big=Image.new('RGB',(240*4,135*4)); big.paste(im.resize((960,540),Image.NEAREST))
    mk.text(big,"SCORE",4*10,4*40,2,(255,214,120)); mk.text(big,"125 400",4*8,4*52,2,(255,248,232)); mk.text(big,"BALL 2/3",4*8,4*72,2,(255,248,232)); mk.text(big,"X3",4*20,4*90,3,(255,196,60))
    big.save(f'{OUT}/AF_pinball_screen.png')
    full=t.image().resize((TW*3,TH*3),Image.NEAREST); full.save(f'{OUT}/AF_pinball_table.png')
    print('ok', len(SEGS),'segments')
