# CRYPTE d'Emberwood : sol, murs autotiles, piliers, statues, tombes, pieges, torches, ennemis
from forest import *

# ------------------------------------------------------------ palettes de la crypte
WARM=(Tc,E)                  # rampes qui restent chaudes (feu, terre cuite)
def crypt_pal(mul,mix,mixc,keep_warm=True):
    p=tint(PAL,mul,mix,mixc)
    if keep_warm:
        for r in WARM:
            for t in range(5): p[r*5+t]=tint([PAL[r*5+t]],(mul[0]*0.4+0.6,mul[1]*0.4+0.6,mul[2]*0.4+0.6),mix*0.4,mixc)[0]
        p[GOLD]=PAL[GOLD]; p[WHITE]=tint([PAL[WHITE]],(0.92,0.9,1.0))[0]
    return p
LIT =crypt_pal((0.86,0.8,1.06),0.14,(70,46,120))       # sous la torche
MID =crypt_pal((0.5,0.46,0.78),0.24,(34,22,70))         # penombre
DARK=crypt_pal((0.24,0.22,0.46),0.32,(14,10,34),False)  # noir bleu-violet

# ------------------------------------------------------------ flammes (emissives: toujours palette PAL)
def flame(s,cx,by,h,k,w=3):
    """flamme en goutte: coeur blanc/or, corps orange, pointe rouge; k=frame (vacille)"""
    rng=random.Random(k*7+cx)
    sway=[0,1,0,-1][k%4]
    for y in range(h):
        kk=y/h                         # 0 = base, 1 = pointe
        hw=w*(1-kk**1.4)*(0.9+0.2*((y+k)%2))
        xc=cx+sway*kk*1.5
        for x in range(int(xc-hw-0.5),int(xc+hw+1.5)):
            d=abs(x-xc)/max(0.6,hw)
            if d>1.05: continue
            c=WHITE if (d<0.35 and kk<0.45) else (GOLD if d<0.6 and kk<0.7 else (ix(E,H) if kk<0.75 else ix(Tc,H)))
            if kk>0.85: c=ix(Tc,L)
            s.set(x,by-y,c)
    for i in range(2):                 # escarbilles
        ex=int(round(cx))+rng.randint(-3,3); ey=int(by)-h-1-rng.randint(0,4)-k%3
        s.set(ex,ey,GOLD if i else ix(Tc,H))

# ------------------------------------------------------------ sol
def slab_floor(v):
    """dalles 8x8 biseautees, joints sombres; v: 0 lisse 1 fissure 2 fissure+eclats 3 humide/mousse 4 os"""
    s=S(16,16)
    for y in range(16):
        for x in range(16):
            sx,sy=x%8,y%8; slab=(x//8)+(y//8)*2
            sh=(hsh(slab,v,5)%3)*0.25-0.25
            if sx==7 or sy==7: t=O if (sx==7 and sy==7) else (S_ if hsh(x,y,v)%3 else O)
            elif sx==0 or sy==0: t=L if hsh(x,y,v+1)%4 else B
            elif sx==6 or sy==6: t=S_
            else: t=dt(2.1+sh+0.35*fnoise(x,y,60+v),x,y,1,3)
            if t==B and hsh(x,y,v+9)%23==0: t=L
            s.set(x,y,ix(St,t))
    if v in (1,2):
        pts=[(2,1),(5,5),(4,8),(8,11),(11,15)] if v==1 else [(15,2),(11,5),(12,9),(7,12),(5,15)]
        for (a,b) in zip(pts,pts[1:]):
            for i in range(6):
                x=int(round(a[0]+(b[0]-a[0])*i/5)); y=int(round(a[1]+(b[1]-a[1])*i/5))
                s.set(x,y,ix(St,O)); s.set(x+1,y,ix(St,L)) if s.get(x+1,y)!=ix(St,O) else None
        if v==2:
            for (x,y) in ((9,6),(10,6),(13,11),(3,12)): s.set(x,y,ix(St,H)); s.set(x+1,y+1,ix(St,O))
    if v==3:
        for y in range(16):
            for x in range(16):
                if (x%8==7 or y%8==7) and hsh(x,y,3)%3==0: s.set(x,y,ix(G,S_) if hsh(x,y,4)%2 else ix(F,S_))
        for (x,y) in ((3,3),(11,12),(12,4)): s.set(x,y,ix(Bl,L)); s.set(x+1,y,ix(Bl,B))
    if v==4:
        for i in range(4): s.set(3+i,10+(i%2),ix(Pl,H if i<2 else L))
        s.set(3,9,ix(Pl,L)); s.set(7,11,ix(Pl,L)); s.set(6,9,ix(Pl,B))
        for (x,y) in ((11,4),(12,4),(11,5),(12,5),(13,5)): s.set(x,y,ix(Pl,L if y==4 else B))
        s.set(11,5,BLACK); s.set(13,5,BLACK)
    return s

# ------------------------------------------------------------ murs : autotiling 4 voisins (dessus) + face
def wall_top(mask):
    """dessus de mur vu d'en haut (16 variantes): bits N=1 E=2 S=4 O=8 = voisin est un mur.
    Bord de pierres de couronnement la ou le voisin n'est pas un mur."""
    n,e,so,w=[(mask>>i)&1 for i in range(4)]
    s=S(16,16)
    for y in range(16):
        for x in range(16):
            h=hsh(x,y,71)
            s.set(x,y,ix(St,S_) if h%11==0 else (BLACK if h%7==0 else ix(St,O)))
    def rim(cond,cells,tone_out,tone_in):
        if cond: return
        for (x,y,d) in cells:
            s.set(x,y,ix(St,tone_out if d==0 else (tone_in if d==1 else S_)))
    for i in range(16):
        for d in range(3):
            if not n: s.set(i,d,ix(St,[L,B,S_][d]) if not ((i+ d)%6==5 and d==0) else ix(St,S_))
            if not so: s.set(i,15-d,ix(St,[S_,B,S_][d]))
            if not w: s.set(d,i,ix(St,[L,B,S_][d]) if s.get(d,i)!=ix(St,L) or d else ix(St,H))
            if not e: s.set(15-d,i,ix(St,[O,S_,S_][d]))
    if not n and not w: s.set(0,0,ix(St,H)); s.set(1,0,ix(St,H))
    for i in range(0,16,6):          # joints des pierres de couronnement
        if not n: s.set(i,0,ix(St,O)); s.set(i,1,ix(St,O))
        if not w: s.set(0,i,ix(St,O)); s.set(1,i,ix(St,O))
        if not so: s.set(i,15,ix(St,O)); s.set(i,14,ix(St,O))
        if not e: s.set(15,i,ix(St,O))
    return s
def wall_face(v=0):
    """face sud d'un mur (16x16): briques decalees biseautees, corniche en haut, plinthe en bas.
    v: 0 brique, 1 fissure, 2 lierre mort/racines, 3 niche avec cranes"""
    s=S(16,16)
    for y in range(16):
        for x in range(16):
            row=(y-3)//4; bx=(x+(4 if row%2 else 0))%8; by=(y-3)%4
            if y<3: t=[H,L,S_][y] if not (x%8==7 and y<2) else O
            elif y>=14: t=S_ if y==14 else O
            elif bx==7 or by==3: t=O if (bx==7 and by==3) or hsh(x,y,v)%3==0 else S_
            elif bx==0 or by==0: t=L
            else: t=dt(2.1+0.3*fnoise(x,y,80+v)+(hsh(row,(x+4*(row%2))//8,2)%3-1)*0.2,x,y,1,3)
            s.set(x,y,ix(St,t))
    if v==1:
        for i,(x,y) in enumerate(((9,3),(9,4),(8,5),(8,6),(9,7),(10,8),(10,9),(9,10),(9,11),(10,12))):
            s.set(x,y,ix(St,O)); s.set(x-1,y,ix(St,H)) if i%2 else None
    if v==2:
        for rx in (3,11):
            for j in range(3,13): s.set(rx+int(1.2*math.sin(j*0.9+rx)),j,ix(Wd,S_ if j%2 else O))
            s.set(rx+1,6,ix(Wd,B)); s.set(rx-1,9,ix(Wd,B))
    if v==3:
        for p in m_rect(3,5,12,12): s.set(*p,BLACK)
        for p in m_rect(3,4,12,4): s.set(*p,ix(St,O))
        for x in range(3,13): s.set(x,13,ix(St,H))
        for cx in (5,10):
            for p in m_ell(cx-2,7,cx+2,11): s.set(*p,ix(Pl,B))
            s.set(cx-1,7,ix(Pl,H)); s.set(cx-2,8,ix(Pl,L)); s.set(cx-1,9,BLACK); s.set(cx+1,9,BLACK); s.set(cx,11,ix(Pl,S_))
    return s

# ------------------------------------------------------------ gros elements
def pillar(broken=False):
    s=S(18,44)
    top=8 if not broken else 16
    # socle
    for p in m_rect(1,36,16,43): s.set(*p,None)
    sphere(s,m_rect(1,37,16,43),St,0.2)
    for x in range(1,17): s.set(x,37,ix(St,H) if x<9 else ix(St,L))
    sphere(s,m_rect(2,33,15,36),St,0.3)
    # fut cannele (cylindre)
    for y in range(top+5,33):
        for x in range(3,15):
            k=(x-3)/11; v=3.5-2.6*k
            if (x-3)%3==2: v-=0.9
            if hsh(x,y,3)%29==0: v-=1
            s.set(x,y,ix(St,dt(v,x,y)))
    if not broken:
        sphere(s,m_rect(1,top,16,top+4),St,0.4)              # chapiteau
        for x in range(1,17): s.set(x,top,ix(St,H) if x<10 else ix(St,L))
        for x in (2,15): s.set(x,top+2,ix(St,S_))
        sphere(s,m_rect(0,top-3,17,top-1),St,0.3)
        for x in (4,8,12): s.set(x,top+3,ix(St,O))
    else:
        for x in range(3,15):                                 # cassure irreguliere
            cut=top+5+(hsh(x,0,7)%4)
            for y in range(top+5,cut): s.set(x,y,None)
            s.set(x,cut,ix(St,H) if x<10 else ix(St,L))
        for (x,y) in ((2,40),(15,41),(16,38)): s.set(x,y,ix(St,L))
    for (x,y) in ((6,20),(7,21),(7,22),(6,23),(6,24)): s.set(x,y,ix(St,O))   # fissure
    return outline(s)
def statue(broken=False):
    """gardien encapuchonne, mains sur le pommeau d'une epee pointee au sol, sur socle grave (runes)"""
    s=S(26,46)
    # socle
    sphere(s,m_rect(1,34,24,45),St,0.1)
    for x in range(1,25): s.set(x,34,ix(St,H) if x<14 else ix(St,L))
    for p in m_rect(6,38,19,42): s.set(*p,ix(St,O))
    for i,x in enumerate(range(7,19,3)):                      # runes (lueur ajoutee en emissif)
        s.set(x,39,ix(Bl,H)); s.set(x+1,40,ix(Bl,L)); s.set(x,41,ix(Bl,H)) if i%2 else s.set(x+1,39,ix(Bl,L))
    # cape (corps)
    cape=m_poly([(5,33),(8,12),(17,12),(20,33)])
    sphere(s,cape,Pl,0.0)
    for (x,y) in cape:                                        # plis verticaux
        if (x-5)%4==0 and y>16: s.set(x,y,ix(Pl,S_))
        if (x-5)%4==1 and y>18: s.set(x,y,ix(Pl,L)) if x<13 else None
    # epaules + capuche
    if not broken:
        hood=m_ell(7,2,18,15); sphere(s,hood,Pl,0.3)
        for p in m_ell(9,6,16,14): s.set(*p,ix(Pl,O))
        for p in m_ell(10,8,15,13): s.set(*p,BLACK)
        s.set(11,10,ix(Bl,H)); s.set(14,10,ix(Bl,H))         # yeux luisants
        s.set(9,4,ix(Pl,H)); s.set(10,3,ix(Pl,H))
    else:
        for x in range(8,18): s.set(x,12+(hsh(x,1,4)%3),ix(Pl,H) if x<13 else ix(Pl,L))
        for (x,y) in ((3,44),(22,44),(21,43)): s.set(x,y,ix(Pl,L))
    sphere(s,m_ell(4,11,21,17),Pl,0.2) if not broken else None
    # epee: lame vers le bas, garde, pommeau sous les mains
    for y in range(18,34): s.set(12,y,ix(St,H)); s.set(13,y,ix(St,B))
    s.set(12,33,ix(St,L)); s.set(13,33,None) if False else None
    for x in range(9,17): s.set(x,18,ix(St,L) if x<13 else ix(St,S_))
    for p in m_rect(10,16,15,17): s.set(*p,ix(Pl,L))         # mains
    s.set(12,15,ix(St,H)); s.set(13,15,ix(St,B))
    for (x,y) in ((17,22),(18,23),(18,24),(17,26),(7,28),(8,29)): s.set(x,y,ix(Pl,O))   # fissures
    for (x,y) in ((6,31),(7,32),(18,30),(19,32)): s.set(x,y,ix(G,S_))                   # mousse humide
    return outline(s)
def sarcophagus():
    """sarcophage 36x28 en 3/4: couvercle avec gisant grave + liseres dores, face avant sculptee"""
    s=S(36,30)
    lid=m_rect(1,1,34,17)
    sphere(s,lid,St,0.4)
    for x in range(1,35): s.set(x,1,ix(St,H)); s.set(x,17,ix(St,S_))
    for y in range(1,18): s.set(1,y,ix(St,H)); s.set(34,y,ix(St,S_))
    for x in range(3,33): s.set(x,3,GOLD if x%4 else ix(E,B)); s.set(x,15,ix(E,B))
    for y in range(3,16): s.set(3,y,GOLD if y%4 else ix(E,B)); s.set(32,y,ix(E,B))
    # gisant (figure allongee, bras croises)
    fig=m_ell(6,6,12,12)|m_rect(11,6,29,12)|m_ell(26,6,31,12)
    sphere(s,fig,Pl,0.3)
    for x in range(12,29): s.set(x,6,ix(Pl,H)) if x%3 else None
    s.set(8,8,ix(Pl,O)); s.set(8,10,ix(Pl,O)); s.set(10,9,ix(Pl,S_))         # visage
    for i in range(5): s.set(14+i,7+i,ix(Pl,S_)); s.set(14+i,11-i,ix(Pl,S_))  # bras croises
    for x in range(20,29): s.set(x,9,ix(St,H))                                # epee du gisant
    s.set(20,8,GOLD); s.set(20,10,GOLD)
    # face avant
    front=m_rect(2,18,33,29)
    sphere(s,front,St,-0.4)
    for x in range(2,34): s.set(x,18,ix(St,O)); s.set(x,29,ix(St,O))
    for i,x0 in enumerate((5,15,25)):                                         # panneaux sculptes
        for p in m_rect(x0,20,x0+6,27): s.set(*p,ix(St,S_))
        for x in range(x0,x0+7): s.set(x,20,ix(St,O))
        for y in range(20,28): s.set(x0,y,ix(St,O)); s.set(x0+6,y,ix(St,L))
        cx=x0+3
        for y in range(22,26): s.set(cx,y,ix(St,L))
        s.set(cx-1,23,ix(St,L)); s.set(cx+1,23,ix(St,L))
    return outline(s)
def tombstone(v=0):
    s=S(16,18)
    m=m_rect(3,6,12,15)|m_ell(3,1,12,11)
    sphere(s,m,St,0.2,sd=v,tex=0.6)
    if v==0:
        for y in range(5,12): s.set(7,y,ix(St,O)); s.set(8,y,ix(St,L))
        for x in range(5,11): s.set(x,7,ix(St,O));
        for x in range(5,11): s.set(x,8,ix(St,L)) if x not in (7,8) else None
    else:
        for (x,y) in ((5,6),(6,6),(9,6),(10,6),(5,9),(7,9),(8,9),(10,9),(6,12),(9,12)): s.set(x,y,ix(St,O))
        for x in range(4,11): s.set(x,3+(x%3==0),ix(St,O)) if x in (4,5,9) else None     # ebrechure
    for x in range(2,14): s.set(x,16,ix(St,O)); s.set(x,17,ix(St,O) if x%2 else None)
    for (x,y) in ((4,14),(11,13)): s.set(x,y,ix(G,S_))
    return outline(s)
def bones():
    s=S(16,12)
    for (x0,y0,x1,y1) in ((1,8,9,5),(6,10,14,7),(3,4,11,9)):
        for i in range(9):
            x=int(round(x0+(x1-x0)*i/8)); y=int(round(y0+(y1-y0)*i/8)); s.set(x,y,ix(Pl,L if i<5 else B)); s.set(x,y+1,ix(Pl,S_))
        for (x,y) in ((x0,y0),(x1,y1)): s.set(x-1,y,ix(Pl,H)); s.set(x,y-1,ix(Pl,H))
    sk=m_ell(9,0,15,6); sphere(s,sk,Pl,0.3)
    s.set(11,3,BLACK); s.set(13,3,BLACK); s.set(12,5,ix(Pl,O)); s.set(10,1,ix(Pl,H))
    return outline(s)
def urn(k=0):
    s=S(14,18)
    body=m_ell(1,4,12,17)|m_rect(4,1,9,5)
    sphere(s,body,Tc,0.1)
    for x in range(3,11): s.set(x,9,ix(E,H) if x%2 else ix(Tc,S_)); s.set(x,12,ix(Tc,S_))
    for x in range(4,10): s.set(x,1,ix(Tc,H)); s.set(x,2,ix(Tc,O))
    s.set(3,6,ix(Tc,H)); s.set(3,7,ix(Tc,H))
    if k:
        for (x,y) in ((9,6),(10,7),(10,8),(9,9),(10,10)): s.set(x,y,ix(Tc,O))
    return outline(s)
def chest(opened=False):
    s=S(18,16)
    sphere(s,m_rect(1,6,16,15),Wd,0.0)
    for y in range(6,16): s.set(4,y,ix(St,B)); s.set(13,y,ix(St,B))
    for x in range(1,17): s.set(x,15,ix(Wd,O))
    if not opened:
        lid=m_rect(1,1,16,6)|m_ell(1,0,16,4)
        sphere(s,lid,Wd,0.4)
        for y in range(0,7): s.set(4,y,ix(St,L)); s.set(13,y,ix(St,S_))
        for x in range(1,17): s.set(x,6,ix(Wd,S_))
        for p in m_rect(7,5,10,8): s.set(*p,GOLD)
        s.set(8,7,BLACK); s.set(7,5,WHITE)
    else:
        for p in m_rect(2,4,15,7): s.set(*p,BLACK)
        for p in m_rect(5,5,12,7): s.set(*p,GOLD if (p[0]+p[1])%2 else ix(E,H))
        s.set(7,5,WHITE); s.set(10,6,WHITE)
        sphere(s,m_rect(1,0,16,3),Wd,0.6)
    return outline(s)
def stairs_down():
    s=S(16,16)
    for i in range(5):
        y0=i*3
        for y in range(y0,y0+3):
            for x in range(1+i//2,15-i//2):
                t=[3,2,1][y-y0]-(i*0.45)
                s.set(x,y,ix(St,max(1,int(round(t)))) if t>=0.6 else BLACK)
    for y in range(15,16):
        for x in range(3,13): s.set(x,y,BLACK)
    for y in range(16): s.set(0,y,ix(St,L)); s.set(15,y,ix(St,S_))
    return s
def crypt_door(locked=True):
    """porte en arc 32x32 dans la face du mur: battants de fer cloutes, serrure doree"""
    s=S(32,32)
    arch=m_rect(2,10,29,31)|m_ell(2,0,29,20)
    sphere(s,arch,St,0.5)
    inner=m_rect(6,12,25,31)|m_ell(6,4,25,20)
    for (x,y) in inner:
        k=(x-6)/19; v=2.6-1.4*k
        if (x-6)%5==0: v=1
        s.set(x,y,ix(Wd,dt(v,x,y)))
    for y in range(5,32): s.set(15,y,ix(Wd,O)); s.set(16,y,ix(Wd,O))
    for yy in (14,24):
        for x in range(6,26): s.set(x,yy,ix(St,S_)); s.set(x,yy-1,ix(St,L))
        for x in (8,12,19,23): s.set(x,yy,ix(St,H))
    for i in range(7):                                        # claveaux de l'arc
        a=math.radians(180+i*30); x=int(15.5+math.cos(a)*12); y=int(11+math.sin(a)*10)
        s.set(x,y,ix(St,O))
    if locked:
        for p in m_rect(13,17,18,22): s.set(*p,GOLD)
        s.set(13,17,WHITE); s.set(15,19,BLACK); s.set(16,19,BLACK); s.set(15,20,BLACK); s.set(16,20,BLACK); s.set(15,21,BLACK)
    return outline(s)
# ------------------------------------------------------------ petits elements
def cobweb(corner='tl'):
    s=S(16,16)
    for a in range(0,91,15):                                  # rayons
        r=math.radians(a)
        for d in range(16):
            x=int(round(math.cos(r)*d)); y=int(round(math.sin(r)*d))
            if 0<=x<16 and 0<=y<16 and (d<14 or a in (30,60)): s.set(x,y,ix(Pl,L) if d%3 else ix(Pl,H))
    for rr in (4,8,12):                                       # fils concentriques qui pendent
        for a in range(0,91,3):
            r=math.radians(a); sag=1.4*math.sin(math.radians((a%15)*12))
            x=int(round(math.cos(r)*(rr-sag))); y=int(round(math.sin(r)*(rr-sag)))
            if 0<=x<16 and 0<=y<16 and s.get(x,y) is None and (x+y)%2==0: s.set(x,y,ix(Pl,B))
    s.set(5,7,BLACK); s.set(6,7,BLACK); s.set(5,8,BLACK); s.set(4,9,ix(Pl,S_)); s.set(7,9,ix(Pl,S_))   # petite araignee
    if corner=='tr': return s.mirror()
    return s
def puddle(k,big=False):
    w,h=(28,12) if big else (16,8)
    s=S(w,h); m=m_ell(0,0,w-1,h-1)
    for (x,y) in m:
        t=B if y>h//2 else S_
        if y<=1: t=O
        s.set(x,y,ix(Bl,t))
    for i in range(3 if big else 2):                          # reflet qui ondule
        x0=3+i*7+k; y=h//2+(i%2)
        for x in range(x0,min(w-2,x0+3)):
            if (x,y) in m: s.set(x,y,ix(Bl,H if x==x0 else L))
    if k%2 and big: s.set(w//2,h//2-1,WHITE)
    return s
def drip(k):
    """goutte qui tombe du plafond -> anneau dans la flaque (4 frames)"""
    s=S(12,24)
    if k<2:
        y=4+k*9; s.set(6,y,ix(Bl,H)); s.set(6,y+1,ix(Bl,L)); s.set(6,y-1,ix(Bl,B)) if k else None
    else:
        r=2+(k-2)*2
        for a in range(0,360,20):
            x=int(round(6+math.cos(math.radians(a))*r)); y=int(round(21+math.sin(math.radians(a))*r*0.45))
            s.set(x,y,ix(Bl,H) if k==2 else ix(Bl,L))
    return s
def chain(k):
    s=S(10,30)
    for i in range(7):
        sw=int(round(math.sin((i/6)*math.pi/2)*[0,1,0,-1][k%4]*1.5))
        y=i*4; x=4+sw
        if i%2==0:
            for p in ((x,y),(x+1,y),(x-1,y+1),(x+2,y+1),(x-1,y+2),(x+2,y+2),(x,y+3),(x+1,y+3)): s.set(*p,ix(St,L))
            s.set(x-1,y+1,ix(St,H))
        else:
            for yy in range(y,y+4): s.set(x,yy,ix(St,B)); s.set(x+1,yy,ix(St,S_))
    x=4+[0,1,0,-1][k%4]
    for p in m_ell(x-3,26,x+4,29): s.set(*p,ix(St,B))         # manille
    for p in m_ell(x-1,27,x+2,28): s.set(*p,None)
    return outline(s)
def spikes(k):
    """piege a piques 16x16, 4 frames: 0 trous, 1 pointes, 2 sorties, 3 a moitie"""
    s=S(16,16)
    for p in m_rect(0,0,15,15): s.set(*p,ix(St,S_))
    for x in range(16): s.set(x,0,ix(St,L)); s.set(x,15,ix(St,O))
    for y in range(16): s.set(0,y,ix(St,L)); s.set(15,y,ix(St,O))
    h=[0,2,6,4][k%4]
    for gy in range(3):
        for gx in range(3):
            cx=3+gx*5; by=4+gy*5
            s.set(cx,by,BLACK); s.set(cx+1,by,BLACK); s.set(cx,by+1,ix(St,O)); s.set(cx+1,by+1,ix(St,O))
            for j in range(h):
                y=by-j
                s.set(cx,y,ix(St,H) if j<h-1 else WHITE); s.set(cx+1,y,ix(St,B) if j<h-1 else ix(St,L))
            if h>=4 and k==2: s.set(cx+1,by-h+1,ix(Tc,S_))          # rouille / sang seche
    return s
def wall_torch(k):
    s=S(12,22)
    for p in m_rect(4,14,7,15): s.set(*p,ix(St,S_))           # support de fer
    for y in range(12,20): s.set(5,y,ix(St,B)); s.set(6,y,ix(St,O))
    for p in m_rect(3,10,8,12): s.set(*p,ix(St,L))
    for y in range(6,11): s.set(4,y,ix(Wd,L)); s.set(5,y,ix(Wd,B)); s.set(6,y,ix(Wd,B)); s.set(7,y,ix(Wd,S_))
    outline(s)
    flame(s,5.5,6,7,k,2.4)
    return s
def brazier(k):
    s=S(18,26)
    for (x0,x1) in ((3,6),(14,11)):                           # trepied
        for i in range(9):
            x=int(round(x0+(x1-x0)*i/8)); s.set(x,25-i,ix(St,B)); s.set(x+1,25-i,ix(St,O))
    for y in range(16,26): s.set(8,y,ix(St,B)); s.set(9,y,ix(St,S_))
    bowl=m_ell(1,11,16,18)&m_rect(1,13,16,18)
    sphere(s,bowl,St,0.2)
    for x in range(1,17): s.set(x,13,ix(St,H) if x<9 else ix(St,L))
    for x in range(3,15): s.set(x,12,ix(Tc,O) if x%2 else ix(E,S_))          # braises
    outline(s)
    flame(s,6,12,9,k,3); flame(s,11,12,8,(k+2)%4,2.5)
    return s
# ------------------------------------------------------------ ennemis de la crypte
def bonewalker(k,mode='walk'):
    """squelette encapuchonne avec bougie fondue sur le crane, cape bleue dechiree, gourdin d'os"""
    s=S(26,34); ox,oy=5,9
    bob=[0,-1,0,-1][k%4] if mode=='walk' else 0
    # jambes (os)
    sw=[(-2,2),(0,0),(2,-2),(0,0)][k%4] if mode=='walk' else (-1,2)
    for i,(lx) in enumerate((6,9)):
        o=sw[i]
        for y in range(16,23): s.set(ox+lx+(o*(y-16)//6),oy+y,ix(Pl,L if y<19 else B))
        s.set(ox+lx+o-1,oy+23,ix(Pl,S_)); s.set(ox+lx+o,oy+23,ix(Pl,B)); s.set(ox+lx+o+1,oy+23,ix(Pl,B))
    # cape (derriere)
    cape=m_poly([(ox+3,oy+8+bob),(ox+8,oy+8+bob),(ox+6,oy+22),(ox+0,oy+21)])
    for (x,y) in cape:
        tatter=(y>=oy+19 and (x+k)%3==0)
        if not tatter: s.set(x,y,ix(Bl,dt(2.2-(x-ox)*0.12+(y-oy-8)*0.05,x,y,1,3)))
    # bassin + colonne + cotes
    for p in m_rect(ox+6,oy+15+bob,ox+10,oy+16+bob): s.set(*p,ix(Pl,B))
    for y in range(oy+9+bob,oy+15+bob): s.set(ox+8,y,ix(Pl,S_))
    for i,y in enumerate(range(oy+9+bob,oy+14+bob,2)):
        for x in range(ox+6,ox+11): s.set(x,y,ix(Pl,H if x<ox+8 else L))
        s.set(ox+5,y+1,ix(Pl,S_)) if i==0 else None
    # bras + gourdin
    if mode=='walk':
        hx,hy=ox+12,oy+13+bob
        for i in range(4): s.set(ox+10+i//2,oy+9+bob+i,ix(Pl,L))
        for i in range(6): s.set(hx+1+i//3,hy-i,ix(Pl,B if i%2 else L));
        for p in m_ell(hx+1,hy-8,hx+4,hy-5): s.set(*p,ix(Pl,H))
    else:
        up_=k==0
        if up_:
            for i in range(5): s.set(ox+10+i//2,oy+9-i,ix(Pl,L))
            for i in range(7): s.set(ox+12-i//3,oy+4-i,ix(Pl,B if i%2 else L))
            for p in m_ell(ox+8,oy-4,ox+11,oy-1): s.set(*p,ix(Pl,H))
        else:
            for i in range(5): s.set(ox+10+i,oy+10+i//2,ix(Pl,L))
            for i in range(7): s.set(ox+15+i,oy+12+i//3,ix(Pl,B if i%2 else L))
            for p in m_ell(ox+18,oy+14,ox+21,oy+17): s.set(*p,ix(Pl,H))
    # crane
    sk=m_ell(ox+4,oy+1+bob,ox+12,oy+8+bob); sphere(s,sk,Pl,0.4)
    for p in m_rect(ox+8,oy+7+bob,ox+12,oy+9+bob): s.set(*p,ix(Pl,B))
    for x in range(ox+8,ox+13,2): s.set(x,oy+8+bob,ix(Pl,O))
    s.set(ox+9,oy+4+bob,BLACK); s.set(ox+10,oy+4+bob,BLACK); s.set(ox+9,oy+5+bob,BLACK); s.set(ox+10,oy+5+bob,GOLD)
    s.set(ox+12,oy+5+bob,BLACK)
    # bougie fondue sur le crane
    for y in range(oy-3+bob,oy+2+bob): s.set(ox+6,y,ix(Pl,H)); s.set(ox+7,y,ix(Pl,L))
    s.set(ox+5,oy+1+bob,ix(Pl,H)); s.set(ox+5,oy+2+bob,ix(Pl,L)); s.set(ox+8,oy+2+bob,ix(Pl,L))
    outline(s)
    flame(s,ox+6.5,oy-4+bob,4,k,1.3)
    if mode=='attack' and k==1:
        for (x,y) in ((24,12),(25,15),(23,19),(20,21)): s.set(x,y,WHITE); s.set(x-1,y,ix(Pl,L))
    return s
def shroudling(k,mode='float'):
    """linceul flottant: capuche vide, yeux braise, bas en lambeaux qui ondulent, chaines aux poignets"""
    s=S(24,26); ox=4; oy=2
    fy=[0,-1,-2,-1][k%4]; yy=oy+fy
    lunge=mode=='attack'
    m=m_ell(ox+1,yy,ox+15,yy+12)|m_poly([(ox+1,yy+7),(ox+15,yy+7),(ox+16,yy+20),(ox+0,yy+20)])
    if lunge: m|=m_poly([(ox+10,yy+6),(ox+19,yy+9),(ox+19,yy+14),(ox+10,yy+16)])
    for x in range(ox,ox+17):                         # lambeaux ondulants
        cut=yy+18+int(2.2*math.sin(x*1.3+k*1.6))
        for y in range(cut,yy+21): m.discard((x,y))
    for (x,y) in m:
        k_=(x-ox)/16; v=3.4-k_*1.6-(y-yy)/24
        if (x+y*2)%7==0: v-=0.7
        if y>yy+14 and (x+y)%2: v-=0.4
        s.set(x,y,ix(Pl,dt(v,x,y)))
    hood=m_ell(ox+4,yy+3,ox+13,yy+11)
    for p in hood: s.set(*p,ix(Pl,O))
    for p in m_ell(ox+5,yy+4,ox+12,yy+10): s.set(*p,BLACK)
    ex=ox+8 if not lunge else ox+9
    s.set(ex,yy+6,ix(Tc,H)); s.set(ex+3,yy+6,ix(Tc,H)); s.set(ex,yy+7,ix(Tc,B)); s.set(ex+3,yy+7,ix(Tc,B))
    if lunge and k==1:
        for p in m_ell(ex,yy+8,ex+3,yy+10): s.set(*p,ix(Tc,O))   # bouche qui hurle
    outline(s)
    # chaine qui traine
    for i in range(6):
        x=ox+2-i//2; y=yy+12+i*2+(1 if (i+k)%2 else 0)
        if 0<=x: s.set(x,y,ix(St,L) if i%2 else ix(St,B))
    if lunge and k==1:
        for i in range(3):                             # ondes du cri
            for a in range(-40,41,10):
                r=math.radians(a); d=5+i*3
                s.set(int(ex+5+math.cos(r)*d),int(yy+9+math.sin(r)*d),ix(Bl,H) if i==0 else ix(Bl,L))
    return s
def gravespinner(k,mode='walk'):
    """araignee des tombes: abdomen marque d'un crane, 8 pattes animees, grappe d'yeux rouges"""
    s=S(28,20); cx,cy=13,10
    rear=mode=='attack'
    ab=m_ell(cx-9,cy-5,cx+1,cy+5) if not rear else m_ell(cx-10,cy-2,cx,cy+7)
    sphere(s,ab,St,-0.3)
    ax=cx-5 if not rear else cx-6; ay=cy-1 if not rear else cy+2
    for p in ((ax-1,ay-1),(ax,ay-1),(ax+1,ay-1),(ax-2,ay),(ax-1,ay),(ax+1,ay),(ax+2,ay),(ax-1,ay+1),(ax,ay+1),(ax+1,ay+1)): s.set(*p,ix(Pl,L))
    s.set(ax-1,ay,BLACK); s.set(ax+1,ay,BLACK); s.set(ax,ay+2,ix(Pl,B))
    head=m_ell(cx+1,cy-3,cx+8,cy+3) if not rear else m_ell(cx+1,cy-6,cx+8,cy)
    sphere(s,head,St,0.0)
    hy=cy-1 if not rear else cy-4
    for (x,y) in ((cx+5,hy),(cx+7,hy),(cx+6,hy-1),(cx+6,hy+1)): s.set(x,y,ix(Tc,H))
    s.set(cx+5,hy-1,WHITE)
    if rear:
        s.set(cx+9,hy+2,WHITE); s.set(cx+9,hy+3,ix(Pl,L)); s.set(cx+8,hy+3,WHITE)
    for side in (-1,1):                         # pattes
        for i in range(4):
            ph=(k+i+(0 if side<0 else 2))%4
            lift=[0,-1,-2,-1][ph]
            bx=cx-2+i*2; by=cy+side*2
            kx=bx+(i-1.5)*2.2; ky=by+side*5+lift*(1 if side<0 else 1)
            fx=kx+(i-1.5)*1.6; fy=ky+side*3-lift
            if rear and side<0 and i>=2: ky-=4; fy-=6
            for (a,b) in (((bx,by),(kx,ky)),((kx,ky),(fx,fy))):
                for j in range(6):
                    x=int(round(a[0]+(b[0]-a[0])*j/5)); y=int(round(a[1]+(b[1]-a[1])*j/5))
                    if s.get(x,y) is None: s.set(x,y,ix(St,B) if j<3 else ix(St,S_))
            s.set(int(round(kx)),int(round(ky)),ix(St,L))
    outline(s)
    return s
def webshot(k):
    s=S(14,14)
    r=2+k*2
    for a in range(0,360,45):
        for d in range(r+1):
            s.set(int(round(7+math.cos(math.radians(a))*d)),int(round(7+math.sin(math.radians(a))*d)),ix(Pl,H) if d==r else ix(Pl,L))
    for a in range(0,360,15):
        s.set(int(round(7+math.cos(math.radians(a))*r*0.6)),int(round(7+math.sin(math.radians(a))*r*0.6)),ix(Pl,B))
    return s
