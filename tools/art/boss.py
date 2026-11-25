# BOSS : le GOLEM DE BRAISE (Ember Golem) + arene volcanique
# Golem ARTICULE : pieces separees (tete, torse, bras = epaule + avant-bras + poing, jambes)
# assemblees par pose -> peu de flash, animations fluides. 3 phases.
from crypt import *

ARENA=crypt_pal((1.06,0.86,0.78),0.12,(110,40,24))      # teinte chaude de l'arene
ARENA_DIM=crypt_pal((0.62,0.44,0.46),0.22,(50,14,18))

# ------------------------------------------------------------ magma
def magma_col(level,k,x,y):
    """level 0 = braise eteinte .. 3 = magma blanc"""
    p=(k+x+y)%4==0
    if level<=0: return ix(Tc,O) if (x+y)%2 else ix(St,O)
    if level==1: return ix(Tc,S_) if not p else ix(Tc,B)
    if level==2: return GOLD if p else (ix(E,H) if (x+y)%2 else ix(Tc,H))
    return WHITE if p or (x+y)%2 else GOLD
def cracks(s,mask,level,k,sd,n=4,ln=10):
    rng=random.Random(sd); pts=list(mask)
    if not pts: return
    for i in range(n):
        x,y=rng.choice(pts); dx,dy=rng.choice(((1,1),(1,-1),(-1,1),(-1,-1),(0,1),(1,0)))
        for j in range(ln):
            if (x,y) not in mask: break
            s.set(x,y,magma_col(level,k,x,y))
            if level>=2 and (x+1,y) in mask and j%2==0: s.set(x+1,y,ix(Tc,H) if level==2 else GOLD)
            if rng.random()<0.45: dx,dy=rng.choice(((dx,0),(0,dy),(dx,dy)))
            x+=dx or rng.choice((-1,1)); y+=dy
def moss(s,mask,amount=1.0,sd=0):
    for (x,y) in mask:
        if (x,y-1) not in mask or (x,y-2) not in mask:
            if hsh(x,y,sd)%10<7*amount: s.set(x,y,ix(G,L) if (x,y-1) not in mask else ix(G,B))
            if (x,y-1) not in mask and hsh(x,y,sd+1)%5==0: s.set(x,y-1,ix(G,H))

# ------------------------------------------------------------ pieces du golem
def g_torso(phase,k):
    s=S(40,32)
    m=m_poly([(2,6),(9,0),(30,0),(37,6),(36,20),(29,31),(10,31),(3,20)])
    sphere(s,m,St,-0.1,sd=3,tex=0.6)
    for (a,b) in (((9,9),(19,13)),((30,9),(20,13)),((12,22),(27,22))):     # joints des plaques
        for i in range(12):
            x=int(round(a[0]+(b[0]-a[0])*i/11)); y=int(round(a[1]+(b[1]-a[1])*i/11)); s.set(x,y,ix(St,O)); s.set(x,y-1,ix(St,L))
    core=m_ell(14,10,25,21)
    if phase==1:                                    # plaque de pierre gravee d'une rune
        sphere(s,core,St,0.3)
        for (x,y) in ((19,12),(19,13),(19,14),(19,15),(19,16),(19,17),(17,14),(21,14),(18,18),(20,18)): s.set(x,y,magma_col(1,k,x,y))
    else:
        for p in core: s.set(*p,ix(Tc,O))
        inner=m_ell(15,11,24,20)
        lv=2 if phase==2 else 3
        for (x,y) in inner:
            d=math.hypot((x-19.5)/4.5,(y-15.5)/4.5)
            s.set(x,y,WHITE if d<0.35+0.1*(k%2) else (GOLD if d<0.65 else ix(E,H) if d<0.85 else ix(Tc,H)))
        # cristal facette
        for (x,y) in ((19,12),(20,12),(18,13),(21,13),(17,15),(22,15)): s.set(x,y,ix(E,H))
        if phase==3:
            for (x,y) in ((17,13),(18,14),(18,15),(19,16),(21,17),(22,18)): s.set(x,y,ix(Tc,O))
    cracks(s,m-core,[0,1,2,3][phase] if phase>1 else 1,k,sd=10+phase,n=3+phase*2,ln=8+phase*2)
    if phase==1: moss(s,m,1.0,4)
    if phase==3:                                    # morceaux d'armure manquants
        for p in m_ell(29,2,37,10): s.set(*p,None)
        for p in m_ell(1,15,7,24): s.set(*p,None)
    return outline(s)
def g_head(phase,k,awake=True):
    s=S(18,16)
    m=m_poly([(2,3),(5,0),(12,0),(15,3),(15,12),(12,15),(5,15),(2,12)])
    sphere(s,m,St,0.2,sd=8,tex=0.5)
    for x in range(3,15): s.set(x,5,ix(St,O)); s.set(x,4,ix(St,H) if x<9 else ix(St,L))      # arcade sourciliere
    for x in range(4,14):                                                                  # fente de l'oeil
        if not awake: c=ix(St,O)
        elif phase==1: c=GOLD if x in (8,9) else ix(Tc,H)
        else: c=WHITE if 6<=x<=11 and (k%2 or x in (8,9)) else GOLD
        s.set(x,7,c); s.set(x,8,c if awake and phase>1 else ix(St,O))
    for x in range(6,12,2): s.set(x,12,ix(St,O))                                           # machoire
    if phase==1: moss(s,m,1.0,9)
    if phase>=2:
        for (x,y) in ((3,2),(4,3),(4,4)): s.set(x,y,magma_col(phase,k,x,y))
    if phase==3: s.set(13,1,None); s.set(14,2,None); s.set(12,0,None)
    s=outline(s)
    if awake and phase>=2:                                                                 # traine de lumiere
        for i in range(2): s.set(15+i,7,GOLD if i==0 else ix(E,H))
    return s
def g_shoulder(phase,k,sd=0):
    s=S(16,16); m=m_ell(1,1,14,14)
    sphere(s,m,St,0.3,sd=sd,tex=0.6)
    cracks(s,m,1 if phase==1 else phase,k,sd=20+sd,n=1+phase,ln=6)
    if phase==1: moss(s,m,1.0,sd)
    return outline(s)
def g_fist(phase,k,sd=0):
    s=S(18,16)
    m=m_rect(1,2,16,14)|m_ell(0,0,17,8)
    sphere(s,m,St,0.1,sd=sd,tex=0.6)
    for x in (5,9,13):                                                  # doigts
        for y in range(8,15): s.set(x,y,ix(St,O))
        s.set(x-1,8,ix(St,H))
    for x in range(1,17): s.set(x,8,ix(St,S_)) if x not in (5,9,13) else None
    cracks(s,m,1 if phase==1 else phase,k,sd=30+sd,n=phase,ln=6)
    return outline(s)
def g_leg(phase,k,sd=0):
    s=S(14,16); m=m_rect(2,0,11,10)|m_rect(0,10,13,15)
    sphere(s,m,St,-0.1,sd=sd,tex=0.6)
    for x in range(0,14): s.set(x,10,ix(St,O))
    for x in (3,7,10): s.set(x,15,ix(St,O)); s.set(x,14,ix(St,O))
    cracks(s,m,1 if phase==1 else phase,k,sd=40+sd,n=1,ln=7)
    return outline(s)
def forearm(s,a,b,phase,k,w=5):
    m=m_line(a[0],a[1],b[0],b[1],w)
    m={p for p in m if p[0]>=0 and p[1]>=0}
    for (x,y) in m:
        dx,dy=b[0]-a[0],b[1]-a[1]; L_=math.hypot(dx,dy) or 1
        side=((x-a[0])*(-dy)+(y-a[1])*dx)/L_
        v=2.5-side*0.45
        s.set(x,y,ix(St,dt(v,x,y)))
    for i in range(3,int(math.hypot(b[0]-a[0],b[1]-a[1]))-2,4):     # bandes de magma au coude
        t=i/max(1,math.hypot(b[0]-a[0],b[1]-a[1]))
        x=int(a[0]+(b[0]-a[0])*t); y=int(a[1]+(b[1]-a[1])*t)
        s.set(x,y,magma_col(max(1,phase),k,x,y)); s.set(x+1,y,magma_col(max(1,phase),k,x+1,y))
    return m

# ------------------------------------------------------------ poses (assemblage)
GW,GH=84,90
def golem(pose='idle',k=0,phase=1):
    """pose: idle, walk, windup, slam, throw0, throw1, stagger, hurt; k = frame"""
    s=S(GW,GH); bx,by=22,26           # coin haut-gauche du torse
    awake=not (pose=='idle' and phase==0)
    ph=max(1,phase)
    tdy=0; tdx=0; hdy=0
    L_sh=(bx-8,by+2); R_sh=(bx+32,by+2)
    Lf=(bx-12,by+26); Rf=(bx+34,by+26)
    legs=[(bx+6,by+28,0),(bx+21,by+28,0)]
    if pose=='idle':
        tdy=[0,1,1,0][k%4]; Lf=(Lf[0],Lf[1]+[0,1,2,1][k%4]); Rf=(Rf[0],Rf[1]+[0,1,2,1][k%4])
    elif pose=='walk':
        st=[(0,-3),(0,0),(-3,0),(0,0)][k%4]
        legs=[(bx+6,by+28+st[0],0),(bx+21,by+28+st[1],0)]
        tdx=[1,0,-1,0][k%4]; tdy=[0,1,0,1][k%4]
        Lf=(Lf[0]+[2,0,-2,0][k%4],Lf[1]); Rf=(Rf[0]-[2,0,-2,0][k%4],Rf[1])
    elif pose=='windup':
        tdy=-2; hdy=-1; Lf=(bx-2,by-22+k); Rf=(bx+24,by-22+k)
    elif pose=='slam':
        tdy=4; hdy=3; Lf=(bx+1,by+40); Rf=(bx+19,by+41)
    elif pose=='throw0':
        Rf=(bx+36,by-8); tdx=-1
    elif pose=='throw1':
        Rf=(bx+44,by+8); tdx=2
    elif pose=='stagger':
        tdy=5; hdy=4; Lf=(bx-10,by+38); Rf=(bx+32,by+38)
    elif pose=='hurt':
        tdx=[2,-2][k%2]
    L_sh=(L_sh[0]+tdx,L_sh[1]+tdy); R_sh=(R_sh[0]+tdx,R_sh[1]+tdy)
    # couches: jambes, bras arriere (gauche), torse, tete, bras avant (droit)
    for i,(lx,ly,_) in enumerate(legs): s.paste(g_leg(ph,k,i),lx,ly)
    tor=g_torso(ph,k); hd=g_head(ph,k,awake)
    def arm(sh,f,sd):
        forearm(s,(sh[0]+8,sh[1]+9),(f[0]+9,f[1]+6),ph,k,6)
        s.paste(g_shoulder(ph,k,sd),sh[0],sh[1]); s.paste(g_fist(ph,k,sd),f[0],f[1])
    front=pose in ('windup','slam')
    if not front: arm(L_sh,Lf,1)
    s.paste(tor,bx-2+tdx,by+tdy)
    s.paste(hd,bx+9+tdx,by-11+tdy+hdy)
    if front: arm(L_sh,Lf,1)
    arm(R_sh,Rf,2)
    if pose=='throw0':                         # rocher brandi
        s.paste(boulder(k,ph),Rf[0]+1,Rf[1]-13)
    if phase==3:                               # fragments en orbite
        for i in range(4):
            a=math.radians(i*90+k*22); fx=int(GW/2+math.cos(a)*34)-3; fy=int(by+12+math.sin(a)*10)-3
            s.paste(fragment(i,k),fx,fy)
    if pose=='hurt' and k==0: s=flash(s)
    return s
def fragment(i,k):
    s=S(8,8); m=m_poly([(1,2),(4,0),(7,3),(5,7),(1,6)]) if i%2 else m_poly([(0,3),(3,0),(7,1),(6,6),(2,7)])
    sphere(s,m,St,0.2)
    for (x,y) in list(m)[:2]: s.set(x,y,GOLD)
    s.set(3,4,ix(Tc,H))
    return outline(s)
def boulder(k,phase=2):
    s=S(16,16); m=m_ell(1,1,14,14)
    sphere(s,m,St,0.1,sd=k,tex=0.6)
    a=k*math.pi/2
    for t in range(-5,6):                     # fissure de magma qui tourne
        x=int(round(7.5+math.cos(a)*t)); y=int(round(7.5+math.sin(a)*t))
        if (x,y) in m: s.set(x,y,magma_col(phase,k,x,y))
    return outline(s)
def fire_trail(k):
    s=S(20,10)
    for i in range(7):
        x=18-i*3+(k%2); y=5+int(1.5*math.sin(i+k))
        r=max(1,3-i//2)
        for p in m_ell(x-r,y-r,x+r,y+r): s.set(*p,[WHITE,GOLD,ix(E,H),ix(Tc,H),ix(Tc,B),ix(St,S_),ix(St,O)][i])
    return s
def death(k,phase=3):
    """effondrement (4 frames): fissures blanches -> eclatement -> tas de gravats + coeur de braise"""
    if k==0:
        s=golem('stagger',0,3)
        for y in range(s.h):
            for x in range(s.w):
                v=s.p[y][x]
                if v is not None and hsh(x,y,77)%5==0: s.p[y][x]=WHITE
        return s
    if k==1: return burst(golem('stagger',1,3),2)
    s=S(GW,GH)
    rng=random.Random(9)
    pile=m_ell(18,60,66,84)
    sphere(s,pile,St,-0.2,sd=3,tex=0.8)
    for i in range(14):
        x=rng.randrange(20,64); y=rng.randrange(58,82); r=rng.randint(2,5)
        sphere(s,m_ell(x-r,y-r,x+r,y+r),St,rng.uniform(-0.3,0.4))
    cracks(s,pile,1 if k==3 else 2,k,5,n=5,ln=8)
    s.paste(g_head(3,0,False),33,60)
    if k==3:                                   # coeur de braise qui flotte (recompense)
        for p in m_ell(37,40,47,50): s.set(*p,ix(Tc,H))
        for p in m_ell(39,42,45,48): s.set(*p,GOLD)
        s.set(41,43,WHITE); s.set(42,43,WHITE)
    return outline(s)

# ------------------------------------------------------------ effets du combat
def shockwave(k):
    s=S(96,32); rx=10+k*12; ry=4+k*3
    for a in range(0,360,3):
        r=math.radians(a)
        for dr,c in ((0,WHITE if k<2 else GOLD),(-1,ix(E,H)),(-2,ix(Tc,H) if k<3 else ix(Tc,B))):
            x=int(round(48+math.cos(r)*(rx+dr))); y=int(round(16+math.sin(r)*(ry+dr*0.4)))
            if (x+y+k)%(1+k//2)==0: s.set(x,y,c)
    rng=random.Random(k)
    for i in range(8):                         # cailloux projetes
        a=rng.uniform(math.pi,2*math.pi); d=rx*rng.uniform(0.5,1.0)
        x=int(48+math.cos(a)*d); y=int(16+math.sin(a)*ry*0.8-k*2)
        s.set(x,y,ix(St,L)); s.set(x+1,y,ix(St,S_))
    return s
def eruption(k):
    """colonne de feu qui sort d'une fissure du sol (telegraphie: k=0 lueur, 1-3 jet)"""
    s=S(16,40)
    for p in m_ell(2,34,13,39): s.set(*p,ix(Tc,O))
    if k==0:
        for p in m_ell(4,35,11,38): s.set(*p,ix(Tc,H) if (p[0]+p[1])%2 else GOLD)
        return s
    h=[0,30,36,20][k]
    for y in range(h):
        kk=y/36; w=5-kk*3+(1 if (y+k)%3==0 else 0)
        for x in range(int(7.5-w),int(8.5+w)):
            d=abs(x-7.5)/max(1,w)
            s.set(x,37-y,WHITE if d<0.3 and kk<0.6 else (GOLD if d<0.6 else (ix(E,H) if kk<0.7 else ix(Tc,H))))
    if k==3:
        for i in range(6): s.set(3+i*2,16-((i*5)%7),ix(St,O)); s.set(4+i*2,17-((i*5)%7),ix(Tc,S_))
    return s
def ember(k):
    s=S(3,3); s.set(1,1,[GOLD,ix(E,H),ix(Tc,H),ix(Tc,B)][k]); return s

# ------------------------------------------------------------ tuiles de l'arene
def basalt_floor(v):
    """dalles de basalte (prismes vus de dessus, octogones decales), joints parfois rougeoyants"""
    s=S(16,16)
    for y in range(16):
        for x in range(16):
            row=y//8; xx=(x+(4 if row%2 else 0))%8; yy=y%8
            corner=(xx+yy<2) or (7-xx+yy<2) or (xx+7-yy<2) or (14-xx-yy<2)
            if xx==7 or yy==7 or corner:
                t=O; s.set(x,y,ix(St,t))
                if v==1 and hsh(x,y,3)%3: s.set(x,y,ix(Tc,S_) if hsh(x,y,4)%2 else ix(Tc,B))
                continue
            if xx==0 or yy==0: t=L
            elif xx==6 or yy==6: t=S_
            else: t=dt(1.8+0.4*fnoise(x,y,90+v)+((hsh(row,(x+4*(row%2))//8,v)%3)-1)*0.25,x,y,1,3)
            s.set(x,y,ix(St,t))
    if v==2:                                   # roussi
        for p in m_ell(3,4,12,12):
            if hsh(*p,5)%2: s.set(*p,ix(St,O))
    if v==3:                                   # fissure de braise
        pts=[(1,3),(5,6),(8,5),(11,9),(15,11)]
        for (a,b) in zip(pts,pts[1:]):
            for i in range(5):
                x=int(round(a[0]+(b[0]-a[0])*i/4)); y=int(round(a[1]+(b[1]-a[1])*i/4))
                s.set(x,y,GOLD if i%2 else ix(E,H)); s.set(x,y+1,ix(Tc,B))
    return s
def lava_c(mask,k):
    """lave (autotiling par coins): croute qui derive, bulles, berge de basalte chauffee au rouge"""
    s=basalt_floor((mask+k*0)%3 if mask%3!=1 else 0)
    Lw=lambda x,y: cfield(mask,x,y,37)>=0.5
    for y in range(16):
        for x in range(16):
            f=cfield(mask,x,y,37)
            if f<0.5:
                if f>0.38: s.set(x,y,ix(Tc,B) if (x+y)%2 else ix(St,O))
                elif f>0.3 and (x+y)%2==0: s.set(x,y,ix(Tc,S_))
                continue
            if not Lw(x,y-1): s.set(x,y,ix(St,O)); continue
            if f<0.56: s.set(x,y,ix(E,H) if (x+k)%3==0 else ix(Tc,H)); continue
            n=fnoise(x+k*2,y+k,55); n2=fnoise(x-k,y+k*2,56)
            if n>0.32:                                              # plaques de croute
                c=ix(Tc,O) if n>0.45 else ix(Tc,S_)
                if n<=0.45 and not (fnoise(x+k*2,y+k-1,55)>0.32): c=ix(Tc,B)
            elif n>0.24: c=ix(Tc,B)
            else:
                v=2.0+(0.32-abs(n2))*4.0                           # veines claires
                t=dt(v,x,y,2,4)
                c=[None,None,ix(Tc,B),ix(Tc,H),GOLD][t]
                if t==4 and abs(n2)<0.05: c=ix(E,H)
            s.set(x,y,c)
    if mask==15:                               # bulle
        bx,by=4+(k*3)%8,5+(k*5)%7
        if k%2==0:
            for p in m_ell(bx-1,by-1,bx+1,by+1): s.set(*p,ix(E,H))
            s.set(bx,by-1,WHITE)
    return s
def basalt_face(v=0):
    """face de mur en orgues de basalte: colonnes verticales hexagonales, sommets irreguliers"""
    s=S(16,16)
    for x in range(16):
        col=x//4; k=x%4; top=hsh(col,v,3)%4
        for y in range(16):
            if y<top: s.set(x,y,ix(St,O)); continue
            if y==top: t=H if k<2 else L
            else: t=[L,B,S_,O][k]
            if y==top+1 and k<3: t=L
            if hsh(x,y,v+5)%17==0 and k in (1,2): t=S_
            s.set(x,y,ix(St,t))
        if v==1 and col==2:
            for y in range(4,14,2): s.set(x,y,magma_col(2,0,x,y)) if k==1 else None
    for x in range(16): s.set(x,15,ix(St,O)); s.set(x,14,ix(St,S_) if x%2 else ix(St,O))
    return s
def rune_circle(k):
    s=S(64,32)
    for rr,c in ((30,ix(Tc,B)),(27,ix(Tc,H)),(20,ix(Tc,B))):
        for a in range(0,360,2):
            x=int(round(32+math.cos(math.radians(a))*rr)); y=int(round(16+math.sin(math.radians(a))*rr*0.48))
            s.set(x,y,c)
    for i in range(8):                         # runes qui s'allument en tournant
        a=math.radians(i*45+11); x=int(32+math.cos(a)*23.5); y=int(16+math.sin(a)*23.5*0.48)
        on=(i-k*2)%8<3
        c=GOLD if on else ix(Tc,S_)
        for (dx,dy) in ((0,-1),(0,0),(0,1),(-1,0) if i%2 else (1,1)): s.set(x+dx,y+dy,c)
    return s
def heart_container(k):
    s=S(16,16)
    m=m_ell(1,2,8,9)|m_ell(7,2,14,9)|m_poly([(1,6),(14,6),(8,14)])
    sphere(s,m,Tc,0.3+0.2*(k%2))
    for (x,y) in ((4,4),(5,4),(4,5)): s.set(x,y,WHITE)
    for x in range(2,14): s.set(x,6,GOLD) if x%3==0 else None
    s=outline(s)
    if k%2: s.set(15,0,WHITE); s.set(0,13,GOLD)
    return s
def boss_bar(hp,w=104,h=9):
    """barre de vie du boss (cadre orne, graduations de phase) - affichee dans le HUD"""
    s=S(w,h)
    paint(s,m_rect(0,0,w-1,h-1),Wd,tex='hatch')
    for p in m_rect(2,2,w-3,h-3): s.set(*p,ix(St,O))
    fill=int((w-6)*hp)
    for x in range(3,3+fill):
        for y in range(2,h-2): s.set(x,y,ix(Tc,[H,L,B,S_,O,O,O][min(6,y-2)]) if x<2+fill else GOLD)
    for (cx,cy) in ((1,1),(w-2,1),(1,h-2),(w-2,h-2)): s.set(cx,cy,GOLD)
    for i in (1,2):
        x=3+int((w-6)*i/3)
        for y in range(2,h-2): s.set(x,y,ix(Wd,O))
    return s
