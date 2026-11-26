# POCKET SIEGE (tower defense) : tours x3 niveaux, ennemis, carte, effets "juicy" facon pub mobile
# meme moteur / palette 48 couleurs que Emberwood (engine.py, forest.py)
from forest import *

# ------------------------------------------------------------ petits outils
def disc(s,cx,cy,r,ramp,bias=0.0,lo=1,hi=4):
    m=m_ell(int(cx-r),int(cy-r),int(cx+r),int(cy+r)); sphere(s,m,ramp,bias,lo=lo,hi=hi); return m
def cyl(s,x0,x1,y0,y1,ramp,rows=None,sd=0):
    """cylindre vertical eclaire a gauche (tour)"""
    for y in range(y0,y1+1):
        for x in range(x0,x1+1):
            k=(x-x0)/max(1,x1-x0); v=3.5-2.6*k
            if rows and (y-y0)%rows==rows-1: v-=0.9
            if rows and (y-y0)%rows==0: v+=0.4
            if rows and ((x+((y-y0)//rows)*3)%7==0) and (y-y0)%rows!=0: v-=0.8
            s.set(x,y,ix(ramp,dt(v,x,y)))
def roof(s,cx,y0,y1,hw,ramp):
    m=m_poly([(cx-hw,y1),(cx,y0),(cx+hw+1,y1)])
    for (x,y) in m:
        k=(x-(cx-hw))/(2*hw+1); v=3.6-2.2*k
        if (y-y0)%3==2: v-=0.6
        s.set(x,y,ix(ramp,dt(v,x,y)))
    for x in range(cx-hw,cx+hw+2): s.set(x,y1,ix(ramp,S_))
    s.set(cx,y0,GOLD)
def flag(s,x,y,col,k=0):
    for j in range(7): s.set(x,y+j,ix(Wd,B))
    for j in range(3):
        for i in range(4+(k%2)): s.set(x+1+i,y+j+(1 if i>2 and k%2 else 0),ix(col,L if j==0 else B))
def stars(s,n,x,y):
    for i in range(n):
        cx=x+i*4
        for (dx,dy) in ((0,-1),(-1,0),(0,0),(1,0),(0,1)): s.set(cx+dx,y+dy,GOLD)
        s.set(cx,y,WHITE)

# ------------------------------------------------------------ emplacement de construction
def pad(sel=False):
    s=S(20,14)
    m=m_ell(0,1,19,13); sphere(s,m,St,0.2)
    for (x,y) in m:                                   # dalles
        if (x+y*2)%7==0: s.set(x,y,ix(St,S_))
    for p in m_ell(4,4,15,10): s.set(*p,ix(E,B) if (p[0]+p[1])%2 else ix(E,L))
    for (x,y) in ((9,6),(10,6),(9,7),(10,7)): s.set(x,y,GOLD if sel else ix(E,H))
    s=outline(s)
    return s

# ------------------------------------------------------------ TOURS (24 de large, ~34 de haut, pied en bas)
def tower_archer(lv,k=0):
    s=S(24,38); b=37
    for p in m_ell(1,b-6,22,b): s.set(*p,ix(St,S_))           # socle
    sphere(s,m_ell(1,b-7,22,b-1),St,0.2)
    if lv==1:
        for x0 in (5,16):                                         # pilotis
            for y in range(18,b-3): s.set(x0,y,ix(Wd,L)); s.set(x0+1,y,ix(Wd,S_))
        for i in range(10): s.set(6+i,20+i,ix(Wd,B)); s.set(16-i,20+i,ix(Wd,S_))
        cyl(s,3,20,14,19,Wd,rows=3)                               # plateforme
        roof(s,11,4,13,9,Tc)
        top=12
    elif lv==2:
        cyl(s,5,18,16,b-4,St,rows=4)
        cyl(s,3,20,11,16,Wd,rows=3)
        roof(s,11,1,10,9,Tc); flag(s,11,-1+3,Bl,k)
        top=9
    else:
        cyl(s,5,18,14,b-4,St,rows=4)
        for x in range(5,19): s.set(x,22,GOLD) if x%2 else s.set(x,22,ix(E,H))
        cyl(s,2,21,9,14,Pl,rows=3)
        roof(s,11,0,8,10,Bl)
        for x in (3,20): s.set(x,9,GOLD)
        top=7
    # archer (tete + arc) qui depasse
    hy=top+3 if lv==1 else top+3
    for p in m_ell(9,hy,13,hy+4): s.set(*p,ix(Sk,B))
    s.set(10,hy+1,ix(Sk,H)); s.set(12,hy+2,BLACK); s.set(10,hy,ix(G,B)); s.set(11,hy,ix(G,B)); s.set(12,hy,ix(G,L))
    for j in range(6): s.set(15,hy-1+j,ix(Wd,L) if j in (0,5) else ix(Wd,B))
    s.set(16,hy+1,ix(Pl,H)); s.set(16,hy+2,ix(Pl,H)); s.set(16,hy+3,ix(Pl,H))
    s=outline(s)
    if lv>1: stars(s,lv,2,1) if False else None
    return s
def tower_cannon(lv,k=0):
    s=S(24,32); b=31
    sphere(s,m_ell(1,b-7,22,b),St,0.1)
    h={1:12,2:15,3:17}[lv]
    cyl(s,3,20,b-h,b-4,St,rows=4)
    for x in range(3,21):                                    # creneaux
        if (x//3)%2==0: s.set(x,b-h-1,ix(St,L)); s.set(x,b-h-2,ix(St,H) if x<11 else ix(St,L))
    if lv>=2:
        for x in range(3,21): s.set(x,b-h+5,ix(Wd,O) if x%3 else ix(St,L))
    if lv==3:
        for x in range(3,21): s.set(x,b-h+2,GOLD if x%2 else ix(E,H))
    # canon(s)
    ty=b-h-6
    for c,(bx) in enumerate((7,) if lv<3 else (4,11)):
        m=m_rect(bx,ty,bx+9,ty+4)|m_ell(bx-1,ty-1,bx+3,ty+5)
        sphere(s,m,St if lv<3 else Wd,0.1,lo=1)
        for p in m_ell(bx+8,ty,bx+11,ty+4): s.set(*p,ix(St,O))
        s.set(bx+10,ty+2,BLACK); s.set(bx+1,ty,ix(St,H))
        if lv>=2: s.set(bx+4,ty,GOLD); s.set(bx+4,ty+4,GOLD)
    if k:
        for p in m_ell(18,ty-3,23,ty+3):
            if s.get(*p) is None: s.set(*p,WHITE if (p[0]+p[1])%2 else GOLD)
    return outline(s)
def tower_frost(lv,k=0):
    s=S(24,36); b=35
    sphere(s,m_ell(2,b-6,21,b),St,0.2)
    cyl(s,6,17,b-9,b-3,Pl,rows=3)
    for x in range(5,19): s.set(x,b-10,ix(Pl,H) if x<12 else ix(Pl,L))
    # cristaux
    sizes={1:[(11,b-24,4,14)],2:[(11,b-27,5,17),(6,b-19,3,9),(17,b-18,3,8)],3:[(11,b-33,6,23),(5,b-22,3,12),(18,b-21,3,11),(14,b-26,2,8)]}[lv]
    for (cx,ty,hw,hh) in sizes:
        m=m_poly([(cx,ty),(cx+hw,ty+hh//3),(cx+hw-1,ty+hh),(cx-hw+1,ty+hh),(cx-hw,ty+hh//3)])
        for (x,y) in m:
            v=3.6-((x-(cx-hw))/(2*hw))*2.3+(0.6 if y<ty+hh//3 else 0)
            if x==cx: v+=0.6
            s.set(x,y,ix(Bl,dt(v,x,y,1,4)))
        s.set(cx-1,ty+2,WHITE); s.set(cx-1,ty+3,WHITE)
    s=outline(s)
    if lv>=2:                                               # eclats flottants (scintillent)
        for i,(x,y) in enumerate(((2,10+k),(21,8+(k+1)%2),(3,4),(20,2))[:lv]):
            s.set(x,y,WHITE if (i+k)%2 else ix(Bl,H)); s.set(x+1,y,ix(Bl,L))
    return s
def tower_storm(lv,k=0):
    s=S(24,38); b=37
    sphere(s,m_ell(2,b-6,21,b),St,0.1)
    h={1:14,2:18,3:22}[lv]
    m=m_poly([(6,b-3),(8,b-3-h),(15,b-3-h),(17,b-3)])         # obelisque
    for (x,y) in m:
        kx=(x-6)/11; v=3.4-2.4*kx
        if (y+x)%9==0: v-=0.7
        s.set(x,y,ix(St,dt(v,x,y)))
    for i,y in enumerate(range(b-h+2,b-4,4)):                 # runes lumineuses
        s.set(11,y,ix(Bl,H) if (i+k)%2 else WHITE); s.set(12,y+1,ix(Bl,L))
    if lv>=2:
        for x0 in (4,18):                                      # bobines de cuivre
            for y in range(b-12,b-3): s.set(x0,y,ix(E,L) if y%2 else ix(Tc,B)); s.set(x0+1,y,ix(Tc,S_))
    oy=b-3-h-5
    r={1:3,2:4,3:5}[lv]
    for p in m_ell(11-r,oy-r,12+r,oy+r):                       # orbe
        d=math.hypot(p[0]-11.5,p[1]-oy)
        s.set(*p,WHITE if d<r*0.45 else (GOLD if d<r*0.8 else ix(E,H)))
    s=outline(s)
    for i in range(3+lv):                                      # etincelles
        a=i*(360/(3+lv))+k*30; x=int(11.5+math.cos(math.radians(a))*(r+3)); y=int(oy+math.sin(math.radians(a))*(r+3))
        if s.get(x,y) is None: s.set(x,y,ix(Bl,H) if i%2 else GOLD)
    return s

# ------------------------------------------------------------ ENNEMIS (regardent a droite)
def slime(k,boss=False):
    s=S(18,16); sq=[0,1,2,1][k%4]
    m=m_ell(2,3+sq,15,15)
    sphere(s,m,G,0.3)
    for (x,y) in m:
        if y>12 and (x+y)%2==0: s.set(x,y,ix(G,S_))
    for p in m_ell(4,5+sq,7,8+sq): s.set(*p,ix(G,H))         # reflet gelatine
    s.set(4,5+sq,WHITE)
    for ex in (9,12):
        s.set(ex,8+sq,BLACK); s.set(ex,9+sq,BLACK); s.set(ex,8+sq,WHITE) if ex==9 else None
    s.set(10,11+sq,ix(G,O)); s.set(11,11+sq,ix(G,O))
    return outline(s)
def goblin(k):
    s=S(18,20); lg=[(0,2),(1,1),(2,0),(1,1)][k%4]; bob=[0,-1,0,-1][k%4]
    for i,(x) in enumerate((6,10)):
        for y in range(14,19): s.set(x+(lg[i]-1)*(y-14)//3,y,ix(Wd,B))
        s.set(x+lg[i]-1,19,ix(Wd,O)); s.set(x+lg[i],19,ix(Wd,O))
    body=m_ell(4,9+bob,13,16+bob); sphere(s,body,Wd,0.1)
    head=m_ell(5,1+bob,14,10+bob); sphere(s,head,G,0.4)
    for (x,y) in ((3,3+bob),(2,2+bob),(4,4+bob)): s.set(x,y,ix(G,L))        # oreille pointue
    for (x,y) in ((15,4+bob),(16,3+bob)): s.set(x,y,ix(G,B))
    s.set(11,5+bob,GOLD); s.set(12,5+bob,BLACK); s.set(13,7+bob,ix(G,O)); s.set(12,8+bob,WHITE)
    for j in range(5): s.set(14+j//2,11+bob-j,ix(St,H) if j>1 else ix(Wd,B))     # dague
    return outline(s)
def orc_knight(k):
    s=S(22,24); lg=[(0,2),(1,1),(2,0),(1,1)][k%4]; bob=[0,-1,0,-1][k%4]
    for i,x in enumerate((7,12)):
        for y in range(17,23): s.set(x+(lg[i]-1)*(y-17)//4,y,ix(St,B)); s.set(x+1+(lg[i]-1)*(y-17)//4,y,ix(St,S_))
    body=m_ell(3,9+bob,17,20+bob); sphere(s,body,St,0.2)
    for x in range(4,17): s.set(x,15+bob,ix(Tc,B))                       # ceinture
    head=m_ell(6,1+bob,16,11+bob); sphere(s,head,St,0.4)
    for x in range(8,16): s.set(x,6+bob,BLACK)                           # visiere
    s.set(13,6+bob,ix(Tc,H)); s.set(14,6+bob,ix(Tc,H))
    for j in range(5): s.set(11+(j%2),0+bob-j+4,ix(Tc,H) if j%2 else ix(Tc,B))   # plumet
    sh=m_ell(0,10+bob,7,19+bob); sphere(s,sh,Bl,0.2)                    # bouclier
    s.set(3,13+bob,GOLD); s.set(3,14+bob,GOLD); s.set(2,14+bob,GOLD); s.set(4,14+bob,GOLD)
    s.set(1,11+bob,ix(Bl,H))
    return outline(s)
def bat(k):
    s=S(20,14); cx,cy=10,7; wy=[-4,0,3,0][k%4]
    for side in (-1,1):
        tip=(cx+side*9,cy+wy); poly=[(cx+side*2,cy),(cx+side*5,cy-3+wy//2),tip,(cx+side*6,cy+3),(cx+side*3,cy+2)]
        poly=[(max(0,min(19,a)),max(0,min(13,b_))) for a,b_ in poly]
        for (x,y) in m_poly(poly): s.set(x,y,ix(Tc,dt(2.3-(y-cy)*0.15+(0.4 if side<0 else -0.2),x,y)))
    sphere(s,m_ell(cx-3,cy-3,cx+3,cy+3),Tc,0.2)
    s.set(cx-2,cy-4,ix(Tc,B)); s.set(cx+2,cy-4,ix(Tc,B))
    s.set(cx-1,cy-1,GOLD); s.set(cx+1,cy-1,GOLD); s.set(cx,cy+2,WHITE)
    return outline(s)
def shaman(k,cast=False):
    s=S(20,22); bob=[0,-1,0,-1][k%4]
    robe=m_poly([(5,8+bob),(13,8+bob),(15,21),(3,21)]); sphere(s,robe,Bl,0.0)
    for (x,y) in robe:
        if y>18 and (x+k)%3==0: s.set(x,y,ix(Bl,S_))
    head=m_ell(5,1+bob,13,9+bob); sphere(s,head,G,0.4)
    for x in range(4,15): s.set(x,2+bob,ix(Tc,B))               # bandeau
    s.set(10,5+bob,GOLD); s.set(11,5+bob,BLACK)
    for y in range(3,21): s.set(16,y,ix(Wd,B))                   # baton
    gem=ix(G,H) if not cast else WHITE
    for p in m_ell(14,0,18,4): s.set(*p,gem)
    s=outline(s)
    if cast:
        for a in range(0,360,45): s.set(int(16+math.cos(math.radians(a))*4),int(2+math.sin(math.radians(a))*4),ix(G,H))
    return s
def ogre(k):
    s=S(34,34); lg=[(0,2),(1,1),(2,0),(1,1)][k%4]; bob=[0,-1,0,-1][k%4]
    for i,x in enumerate((10,19)):
        m=m_rect(x+lg[i]-1,24,x+4+lg[i]-1,32); sphere(s,m,Tc,-0.2)
        for xx in range(x+lg[i]-2,x+6+lg[i]-1): s.set(xx,33,ix(Wd,O))
    belly=m_ell(4,9+bob,28,28+bob); sphere(s,belly,Tc,0.0)
    for x in range(6,27): s.set(x,23+bob,ix(Wd,B)); s.set(x,24+bob,ix(Wd,S_))   # pagne
    for x in range(6,27,4): s.set(x,25+bob,ix(Wd,O))
    head=m_ell(10,0+bob,24,13+bob); sphere(s,head,Tc,0.3)
    s.set(19,5+bob,ix(Tc,H)); s.set(20,5+bob,BLACK); s.set(15,5+bob,ix(Tc,H)); s.set(16,5+bob,BLACK)
    for x in range(15,22): s.set(x,4+bob,ix(Tc,O))               # sourcils
    for (x,y) in ((15,10+bob),(21,10+bob)): s.set(x,y,WHITE); s.set(x,y-1,WHITE)   # defenses
    for p in m_ell(1,13+bob,6,20+bob): s.set(*p,ix(Tc,B))      # bras
    club=m_poly([(26,2+bob),(31,0+bob),(33,4+bob),(29,20+bob),(27,20+bob)]); sphere(s,club,Wd,0.2)
    for (x,y) in ((30,4+bob),(28,9+bob),(31,7+bob)): s.set(x,y,ix(St,H))
    for x in range(12,23): s.set(x,0+bob,GOLD) if x%3 else s.set(x,0+bob,ix(Tc,H))   # couronne
    return outline(s)

# ------------------------------------------------------------ PROJECTILES + EFFETS
def arrow():
    s=S(9,3)
    for x in range(1,8): s.set(x,1,ix(Wd,L))
    s.set(8,1,ix(St,H)); s.set(7,0,ix(St,L)); s.set(7,2,ix(St,L)); s.set(0,0,WHITE); s.set(0,2,WHITE)
    return s
def cannonball():
    s=S(7,7); disc(s,3,3,2.5,St,-0.3); s.set(2,2,WHITE); return outline(s)
def frostbolt():
    s=S(8,8)
    for p in m_poly([(4,0),(7,4),(4,7),(1,4)]): s.set(*p,ix(Bl,L))
    s.set(4,3,WHITE); s.set(3,4,ix(Bl,H)); return outline(s)
def explosion(k):
    s=S(30,30); r=[4,8,11,13][k]
    if k<3:
        for p in m_ell(15-r,15-r,15+r,15+r):
            d=math.hypot(p[0]-15,p[1]-15)/r
            s.set(*p,WHITE if d<0.3 and k<2 else (GOLD if d<0.55 else (ix(E,H) if d<0.8 else ix(Tc,H))))
    else:                                              # fumee : petits nuages qui s'ecartent
        for i in range(7):
            a=i*51; cx=15+math.cos(math.radians(a))*9; cy=15+math.sin(math.radians(a))*8-2
            rr=3+(i%2)
            for p in m_ell(int(cx-rr),int(cy-rr),int(cx+rr),int(cy+rr)):
                if 0<=p[0]<30 and 0<=p[1]<30: s.set(*p,ix(St,H) if p[1]<cy-1 else (ix(St,L) if p[1]<cy+1 else ix(St,B)))
        s=outline(s)
    if k>=1:
        rng=random.Random(k)
        for i in range(8):
            a=rng.uniform(0,6.28); d=r+2+k
            s.set(int(15+math.cos(a)*d),int(15+math.sin(a)*d),GOLD if i%2 else ix(Tc,H))
    return s
def frostburst(k):
    s=S(26,26); r=[4,8,11][k]
    for a in range(0,360,30):
        for d in range(r-2,r+1):
            s.set(int(13+math.cos(math.radians(a+k*15))*d),int(13+math.sin(math.radians(a+k*15))*d),WHITE if d==r else ix(Bl,H))
    for a in range(0,360,60):
        x=int(13+math.cos(math.radians(a))*r*0.5); y=int(13+math.sin(math.radians(a))*r*0.5); s.set(x,y,ix(Bl,L))
    return s
def coin(k):
    s=S(9,9); w=[4,3,1,3][k]
    m=m_ell(4-w,0,4+w,8)
    for (x,y) in m:
        d=(x-(4-w))/max(1,2*w)
        s.set(x,y,GOLD if d<0.6 else ix(E,H))
    if w>=3:
        for y in range(2,7): s.set(4,y,ix(E,L))
        s.set(3,1,WHITE)
    return outline(s)
def heart_s2():
    s=S(9,8); m=m_ell(0,0,4,4)|m_ell(4,0,8,4)|m_poly([(0,2),(8,2),(4,7)]); sphere(s,m,Tc,0.4); s.set(2,1,WHITE); return outline(s)
def portal(k):
    s=S(26,30)
    sphere(s,m_rect(1,6,24,29)|m_ell(1,0,24,14),St,0.3)
    for p in m_rect(5,10,20,29)|m_ell(5,4,20,16):
        d=math.hypot((p[0]-12.5)/7.5,(p[1]-14)/12)
        a=math.atan2(p[1]-14,p[0]-12.5)+k*0.6+d*3
        t=int((math.sin(a*3)+1)*1.6)
        s.set(*p,[ix(Bl,S_),ix(Bl,B),ix(Bl,L),ix(Bl,H)][min(3,t)] if d<0.95 else ix(Bl,O))
    for i in range(5): s.set(4+i*4,2+(i%2),GOLD)
    return outline(s)
def castle(k=0):
    s=S(44,46)
    cyl(s,4,39,20,44,Pl,rows=4)                                   # muraille
    for x in range(4,40):
        if (x//4)%2==0: s.set(x,19,ix(Pl,H) if x<20 else ix(Pl,L)); s.set(x,18,ix(Pl,L))
    for tx in (2,32):                                               # tours d'angle
        cyl(s,tx,tx+9,10,44,Pl,rows=4); roof(s,tx+4,0,10,6,Bl); flag(s,tx+4,-1+1,Tc,k)
    door=m_rect(17,30,26,44)|m_ell(17,26,26,34); paint(s,door,Wd,tex='hatch')
    for y in range(28,45): s.set(21,y,ix(Wd,O))
    s.set(19,37,GOLD); s.set(24,37,GOLD)
    for (wx,wy) in ((10,26),(34,26)):
        for p in m_rect(wx,wy,wx+2,wy+4): s.set(*p,BLACK)
        s.set(wx,wy,GOLD)
    return outline(s)
def tree_round(v):
    s=S(22,26)
    trunk(s,9,12,16,24,2,v)
    clumps(s,[(11,7,8,6,0.4),(6,11,6,5,0.0),(16,11,6,5,-0.1),(11,13,8,4,-0.5)],G if v%2 else F,sd=v)
    return outline(s)
def flowers_tile(v):
    s=grass_t(v)
    rng=random.Random(v)
    for _ in range(4):
        x,y=rng.randrange(2,14),rng.randrange(2,14); c=rng.choice((ix(Tc,H),WHITE,GOLD,ix(Bl,L)))
        for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)): s.set(x+dx,y+dy,c)
        s.set(x,y,GOLD)
    return s
def build_menu(sel=0):
    """bulle de construction : 4 icones de tours + prix"""
    s=S(96,34)
    paint(s,m_rect(0,0,95,29),Wd,tex='hatch')
    for p in m_rect(2,2,93,27): s.set(*p,ix(Pl,L))
    for i in range(4):
        x=4+i*23
        paint(s,m_rect(x,4,x+19,25),Pl,bevel=True) if i!=sel else paint(s,m_rect(x,4,x+19,25),E,bevel=True)
    for p in m_poly([(44,29),(52,29),(48,33)]): s.set(*p,ix(Wd,B))
    for (x,y) in ((1,1),(94,1),(1,28),(94,28)): s.set(x,y,GOLD)
    return s
