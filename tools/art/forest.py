# FORET d'Emberwood : tuiles, decor, ennemis, effets (meme moteur/palette que le village)
from village import *

# ------------------------------------------------------------ outils d'ombrage
BAYER=[[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]]
def dt(v,x,y,lo=1,hi=4):
    """ton continu -> ton entier avec tramage ordonne (dithering leger)"""
    v=max(lo,min(hi,v)); b=int(v); fr=v-b
    if b<hi and fr*16>BAYER[y%4][x%4]+0.5: b+=1
    return b

def clumps(s,cl,r,sd=0,leaf=True,lo=1,hi=4):
    """feuillage en touffes: cl=[(cx,cy,rx,ry,biais[,rampe])] dessine du fond vers l'avant.
    lumiere haut-gauche par touffe, bord bas-droit assombri, petites feuilles en relief."""
    own={}
    for i,c in enumerate(cl):
        cx,cy,rx,ry=c[:4]
        for p in m_ell(cx-rx,cy-ry,cx+rx,cy+ry): own[p]=i
    for (x,y),i in own.items():
        c=cl[i]; cx,cy,rx,ry,bias=c[:5]; rr=c[5] if len(c)>5 else r
        dx=(x-cx)/max(1,rx); dy=(y-cy)/max(1,ry)
        v=2.35-(dx*0.75+dy*0.95)*1.05+bias
        if dx*dx+dy*dy>0.7 and dx+dy>0.2: v-=0.55
        t=dt(v,x,y,lo,hi)
        if leaf:
            h=hsh(x,y,sd)
            if h%10==0 and t>=2: t-=1
            elif h%10==5 and t<hi: t+=1
        s.set(x,y,ix(rr,t))
    # petites feuilles: point clair + ombre portee dessous
    if leaf:
        for (x,y),i in own.items():
            if hsh(x,y,sd+7)%23==0 and (x,y+1) in own and (x+1,y) in own:
                rr=cl[i][5] if len(cl[i])>5 else r
                s.set(x,y,ix(rr,H if tone_of(s.get(x,y))>=3 else L)); s.set(x,y+1,ix(rr,S_))
    return own

def bark(s,mask,r=Wd,sd=0,horiz=False):
    rows={}
    for (x,y) in mask: rows.setdefault(y if not horiz else x,[]).append(x if not horiz else y)
    for (x,y) in mask:
        a,b_=(y,x) if not horiz else (x,y)
        lo,hi_=min(rows[a]),max(rows[a]); w=max(1,hi_-lo)
        k=(b_-lo)/w
        v=3.4-2.3*k
        if not horiz:
            if (x*3+hsh(0,y//3,sd)%4)%5==0: v-=1.1
            if hsh(x,y//2,sd)%17==0: v+=0.9
        else:
            if (y*3+hsh(x//3,0,sd)%4)%5==0: v-=1.1
        s.set(x,y,ix(r,dt(v,x,y)))

def sphere(s,mask,r,bias=0.0,sd=0,tex=0.0,lo=1,hi=4):
    xs=[x for x,_ in mask]; ys=[y for _,y in mask]
    cx=(min(xs)+max(xs))/2; cy=(min(ys)+max(ys))/2; rx=max(1,(max(xs)-min(xs))/2); ry=max(1,(max(ys)-min(ys))/2)
    for (x,y) in mask:
        dx=(x-cx)/rx; dy=(y-cy)/ry
        v=2.4-(dx*0.8+dy*1.0)*1.1+bias
        if tex and hsh(x,y,sd)%7==0: v-=tex
        s.set(x,y,ix(r,dt(v,x,y,lo,hi)))

# ------------------------------------------------------------ bruit periodique 16 px (tuiles raccordables)
_LAT={}
def _pn(x,y,sd,cell):
    n=16//cell; key=(sd,cell)
    if key not in _LAT:
        rng=random.Random(sd*131+cell); _LAT[key]=[[rng.uniform(-1,1) for _ in range(n)] for _ in range(n)]
    lt=_LAT[key]; gx=x/cell; gy=y/cell; x0=math.floor(gx); y0=math.floor(gy); fx=gx-x0; fy=gy-y0
    sx=fx*fx*(3-2*fx); sy=fy*fy*(3-2*fy); g=lambda i,j: lt[j%n][i%n]
    a=g(x0,y0)*(1-sx)+g(x0+1,y0)*sx; b=g(x0,y0+1)*(1-sx)+g(x0+1,y0+1)*sx
    return a*(1-sy)+b*sy
def fnoise(x,y,sd): return 0.62*_pn(x,y,sd,8)+0.38*_pn(x,y,sd,4)
def cfield(mask,x,y,sd,amp=0.24):
    """autotiling par COINS (16 tuiles, bits NO=1 NE=2 SO=4 SE=8): bords organiques continus"""
    u=(x+0.5)/16; v=(y+0.5)/16
    c=[(mask>>i)&1 for i in range(4)]
    f=c[0]*(1-u)*(1-v)+c[1]*u*(1-v)+c[2]*(1-u)*v+c[3]*u*v
    return f+amp*fnoise(x,y,sd)

# ------------------------------------------------------------ sol de foret
def floor_t(v):
    """sous-bois: herbe plus sombre et chaude, litiere de feuilles, brindilles"""
    s=S(16,16); rng=random.Random(v*7+1)
    for y in range(16):
        for x in range(16):
            n=fnoise(x,y,40+v)
            t=dt(1.9+n*0.85,x,y,1,3)
            h=hsh(x,y,v+50)
            if h%9==0: t=max(1,t-1)
            elif h%15==0: t=min(4,t+1)
            s.set(x,y,ix(G,t))
    for _ in range(3+v%2):          # feuilles mortes
        x,y=rng.randrange(1,14),rng.randrange(1,14); c=rng.choice((ix(E,L),ix(Tc,L),ix(E,B),GOLD))
        s.set(x,y,c); s.set(x+1,y,c if rng.random()<0.6 else ix(E,B)); s.set(x,y+1,ix(G,S_))
    if v==2:                         # brindille
        for i in range(5): s.set(4+i,10-i//2,ix(Wd,B if i%2 else L))
        s.set(5,11,ix(G,O)); s.set(7,10,ix(G,O))
    if v==3:                         # trefle
        for (x,y) in ((10,4),(4,11)):
            for dx,dy in ((0,0),(1,0),(0,1)): s.set(x+dx,y+dy,ix(G,L));
            s.set(x,y,ix(G,H)); s.set(x+1,y+1,ix(G,S_))
    return s

def tallgrass(k):
    """hautes herbes (coupables) qui ondulent: 2 frames"""
    s=S(16,16)
    for i,(x0,hgt) in enumerate(((1,9),(3,12),(5,10),(7,13),(9,11),(11,12),(13,9),(14,11),(4,8),(10,7))):
        lean=(1 if (k+i)%2 else 0)*(1 if i%3 else -1)
        for j in range(hgt):
            yy=15-j; xx=x0+(lean if j>hgt*0.55 else 0)+(lean if j>hgt*0.85 else 0)
            t=S_ if j<3 else (B if j<hgt*0.6 else (L if j<hgt-1 else H))
            s.set(xx,yy,ix(G,t))
    return outline(s)

def path_c(mask):
    """chemin de terre naturel (autotiling par coins): bords ondules, touffes d'herbe qui debordent,
    rebord ombre en haut-gauche / eclaire en bas-droite (chemin legerement creuse)"""
    s=floor_t(mask%4)
    inn=lambda x,y: cfield(mask,x,y,11)>=0.5
    for y in range(16):
        for x in range(16):
            f=cfield(mask,x,y,11)
            if f>=0.5:
                t=B; h=hsh(x,y,mask+3)
                if not inn(x,y-1) or not inn(x-1,y): t=S_
                elif not inn(x,y+1) or not inn(x+1,y): t=L
                else:
                    n=fnoise(x,y,77)
                    t=dt(2.35+n*0.55,x,y,2,4)
                    if h%13==0: t=S_
                s.set(x,y,ix(E,t))
                if f>0.62 and h%37==0: s.set(x,y,ix(St,L)); s.set(x+1,y,ix(St,S_)) if inn(x+1,y) else None   # cailloux
                if f<0.56 and h%5==0: s.set(x,y,ix(G,B if (x+y)%2 else L))     # herbe qui deborde
            elif f>0.40:
                s.set(x,y,ix(G,S_) if (x+y)%2 else ix(G,O+1))
    return s

def water_c(mask,k):
    """riviere (autotiling par coins) avec berge de terre, paroi ombree au nord, ecume, reflets animes (4 frames)"""
    s=floor_t((mask+1)%4)
    W_=lambda x,y: cfield(mask,x,y,23)>=0.5
    for y in range(16):
        for x in range(16):
            f=cfield(mask,x,y,23)
            if f<0.5:
                if f>0.36:      # berge
                    if W_(x,y-2) or W_(x,y-1): s.set(x,y,ix(E,L) if (x+y)%2 else ix(E,B))
                    else: s.set(x,y,ix(E,B) if f>0.43 else (ix(G,O) if (x+y)%2 else ix(E,S_)))
                continue
            if not W_(x,y-1): s.set(x,y,ix(E,S_)); continue
            if not W_(x,y-2): s.set(x,y,ix(Bl,O)); continue
            if f<0.57:          # haut-fond + ecume
                foam=(hsh(x,(y-k)//2,5)%3==0)
                s.set(x,y,WHITE if foam and (x+k)%2 else ix(Bl,H if foam else L)); continue
            depth=min(1.0,(f-0.57)/0.4)
            t=dt(2.75-depth*1.25+0.15*fnoise(x,y-k*2,91),x,y,1,3)
            # rides qui descendent avec le courant
            if (y-k*2+int(2.5*math.sin(x*0.8)))%7==0 and hsh(x,y,k)%3: t=3
            if (y-k*2+int(2.5*math.sin(x*0.8)))%7==1 and hsh(x,y,k+9)%5==0: t=4
            s.set(x,y,ix(Bl,t))
            if hsh(x,(y-2*k)//1,61)%97==0: s.set(x,y,WHITE)   # scintillement
    return s

def cliff_t(row,v):
    """falaise: row 0 = haut avec rebord herbeux + racines; row 1 = base avec eboulis. v = variante (lierre)"""
    s=S(16,16)
    for y in range(16):
        for x in range(16):
            yy=y+row*16+int(round(1.7*math.sin(x*0.42+v*1.3)+0.8*math.sin(x*1.1+row)))
            band=(yy+ (hsh(x//5+v,yy//6,8)%3))//6
            k=(yy+(hsh(x//5+v,yy//6,8)%3))%6
            t=B
            if k==0: t=H if hsh(x,band,1)%3 else L
            elif k==1: t=L
            elif k==5: t=S_
            if hsh(x//1,band,v+40)%8==0 and 1<k<5: t=O if k in (2,3) else S_
            elif hsh(x+1,band,v+40)%8==0 and 1<k<5: t=L
            if hsh(x,yy,v)%19==0: t=max(1,t-1)
            s.set(x,y,ix(St,t))
    if row==0:
        for x in range(16):        # rebord d'herbe qui surplombe
            h=2+(hsh(x,0,v+3)%3)
            for y in range(h): s.set(x,y,ix(G,[L,B,B,S_][min(3,y)]))
            s.set(x,h,ix(G,O)); s.set(x,h+1,ix(St,O))
        for rx in ((3,11) if v%2==0 else (7,)):   # racines pendantes
            for j in range(4+v%3): s.set(rx+(j//3),4+j,ix(Wd,B if j%2 else S_))
    else:
        for x in range(16):        # eboulis + ombre au pied
            s.set(x,15,ix(St,O)); s.set(x,14,ix(St,S_) if x%2 else ix(St,O))
        for (x,y) in ((3,12),(10,13),(13,11)):
            for p in m_ell(x-1,y-1,x+1,y): s.set(*p,ix(St,L))
            s.set(x-1,y-1,ix(St,H))
    if v>=2:                       # lierre
        for vx in (2,9,13)[:v-1]:
            for j in range(0,14 if row==0 else 9):
                xx=vx+int(1.3*math.sin(j*0.7)); s.set(xx,j+2*(1-row),ix(F,B if j%2 else L))
                if j%3==0: s.set(xx+1,j+2*(1-row),ix(F,H)); s.set(xx-1,j+3-2*row,ix(F,S_))
    return s

# ------------------------------------------------------------ arbres (4 types) + speciaux
def trunk(s,x0,x1,y0,y1,flare=3,sd=0):
    m=m_rect(x0,y0,x1,y1)|m_poly([(x0-flare,y1+1),(x0,y1-4),(x1,y1-4),(x1+flare,y1+1)])
    bark(s,m,Wd,sd)
    for (rx,dx) in ((x0-flare,-1),(x1+flare,1)): s.set(rx,y1,ix(Wd,S_))
    return m
def oak(hollow=False):
    s=S(40,48)
    trunk(s,16,23,28,45,4,1)
    if hollow:
        for p in m_ell(17,34,22,42): s.set(*p,ix(Wd,O))
        for p in m_ell(18,36,21,42): s.set(*p,BLACK)
        for y in range(35,42): s.set(17,y,ix(Wd,H)) if y%2 else None
        s.set(20,38,GOLD); s.set(19,38,GOLD)       # yeux dans le creux (secret)
    cl=[(20,8,10,7,0.45),(9,14,8,7,0.1),(31,14,8,7,-0.15),(14,8,7,6,0.5),(27,9,7,6,0.2),
        (20,15,10,6,0.0),(8,21,7,6,-0.45),(32,21,7,6,-0.6),(20,23,11,5,-0.7)]
    clumps(s,cl,F,sd=3)
    for (x,y) in ((14,26),(25,27),(19,28)):          # ombre du feuillage sur le tronc
        for dx in range(3): s.set(x+dx,y,ix(Wd,O))
    return outline(s)
def pine():
    s=S(30,50)
    trunk(s,13,16,40,47,2,4)
    for i,(y0,hw) in enumerate(((2,4),(8,7),(15,10),(23,12),(31,14))):
        y1=y0+11; m=set()
        for y in range(y0,y1+1):
            k=(y-y0)/11; w=int(1+hw*k)
            for x in range(15-w,15+w+1): m.add((x,y))
        for x in range(15-hw,15+hw+1,1):       # bord bas en dents de scie
            if (x+i)%3==0: m.discard((x,y1)); m.discard((x,y1-1)) if (x+i)%6==0 else None
            elif (x+i)%3==1: m.add((x,y1+1))
        for (x,y) in m:
            k=(x-15)/max(1,hw); kk=(y-y0)/11
            v=2.6-k*1.2-kk*0.7+(0.25 if i<2 else 0)
            if (x+ y*2)%5==0 and kk>0.3: v-=0.8          # aiguilles
            s.set(x,y,ix(F,dt(v,x,y)))
        for x in range(15-hw+1,15+hw):                   # ombre sous l'etage
            if (x,y1+2) in m or True: s.set(x,min(49,y1+2),ix(F,O)) if s.get(x,y1+2) is not None else None
    s.set(15,1,ix(F,H)); s.set(14,4,ix(F,H)); s.set(10,13,ix(F,H)); s.set(8,21,ix(F,H))
    return outline(s)
def birch():
    s=S(28,48)
    m=m_rect(12,18,15,45)|m_poly([(10,46),(12,41),(15,41),(17,46)])
    for (x,y) in m:
        k=(x-11)/5; v=3.6-2.0*k
        s.set(x,y,ix(Pl,dt(v,x,y,1,4)))
    y=19
    while y<44:                                 # lenticelles sombres irregulieres
        side=hsh(0,y,5)%3; w=1+hsh(1,y,5)%3
        x0=12 if side==0 else (16-w if side==1 else 13)
        for x in range(x0,min(16,x0+w)): s.set(x,y,ix(St,O) if x<15 else ix(St,S_))
        y+=3+hsh(2,y,5)%3
    for (bx,by,d) in ((12,26,-1),(15,22,1)):     # branche
        for i in range(4): s.set(bx+d*(i+1),by-i,ix(Pl,S_))
    cl=[(14,7,7,6,0.5,G),(7,13,6,5,0.1,G),(21,12,6,5,0.0,G),(14,15,7,5,-0.2,G),(9,20,5,4,-0.5,G),(19,20,5,4,-0.6,G)]
    clumps(s,cl,G,sd=9)
    for (x,y) in ((10,10),(16,4),(20,15),(7,17)): s.set(x,y,GOLD) if hsh(x,y,1)%2 else s.set(x,y,ix(G,H))  # chatons
    return outline(s)
def maple():
    """erable d'automne (ambre/rouge) - couleurs chaudes, source des feuilles qui tombent"""
    s=S(38,48)
    trunk(s,16,21,30,45,3,7)
    for (bx,by,d) in ((16,32,-1),(21,31,1)):
        for i in range(5): s.set(bx+d*i,by-i,ix(Wd,B)); s.set(bx+d*i,by-i+1,ix(Wd,S_))
    cl=[(19,8,9,7,0.35),(9,14,8,7,0.0),(29,13,8,7,-0.15),(13,8,6,5,0.55),(25,8,6,5,0.3),
        (19,16,9,6,-0.05),(8,22,7,5,-0.45),(30,22,7,5,-0.55),(19,24,10,5,-0.7)]
    own=clumps(s,cl,Tc,sd=13)
    for (x,y) in own:                      # feuilles dorees eparses (lumiere haut-gauche)
        h=hsh(x,y,21)
        if tone_of(s.get(x,y))>=3 and h%6==0: s.set(x,y,GOLD)
        elif tone_of(s.get(x,y))==2 and h%11==0: s.set(x,y,ix(E,L))
    return outline(s)
def stump():
    s=S(16,16)
    side=m_rect(3,6,12,13)|m_poly([(1,14),(3,10),(12,10),(14,14)])
    bark(s,side,Wd,2)
    top=m_ell(3,3,12,8)
    for (x,y) in top:
        d=math.hypot((x-7.5)/4.5,(y-5.5)/2.5)
        ring=int(d*4)%2
        s.set(x,y,ix(Wd,H if ring==0 and d<0.4 else (L if ring==0 else B)))
    s.set(7,5,ix(Wd,S_)); s.set(8,5,ix(Wd,S_))
    for x in range(3,13): s.set(x,8,ix(Wd,S_)) if (x,9) in side else None
    s.set(4,4,ix(Wd,H)); s.set(5,3,ix(Wd,H))
    for (x,y) in ((11,4),(12,5),(10,4)): s.set(x,y,ix(G,L))    # mousse
    return outline(s)
def hollow_log():
    """tronc creux couche (on peut s'y cacher): ouverture a gauche, mousse + champignon"""
    s=S(36,20)
    body=m_rect(6,4,33,16)|m_ell(29,4,35,16)
    bark(s,body,Wd,4,horiz=True)
    for x in range(8,33):
        if hsh(x,0,3)%3: s.set(x,4,ix(G,L)); s.set(x,5,ix(G,B) if hsh(x,1,3)%2 else ix(Wd,L))
        if hsh(x,2,3)%5==0: s.set(x,3,ix(G,H))
    end=m_ell(1,3,11,17)
    for (x,y) in end:
        d=math.hypot((x-6)/5,(y-10)/7)
        s.set(x,y,ix(Wd,L) if d>0.78 else (ix(Wd,O) if d>0.6 else BLACK))
    s.set(3,6,ix(Wd,H)); s.set(2,8,ix(Wd,H))
    for (x,y) in ((5,12),(7,13)): s.set(x,y,ix(Wd,O))
    # petit champignon sur le dessus
    for p in m_ell(20,0,25,3): s.set(*p,ix(Tc,B))
    s.set(21,1,WHITE); s.set(23,0,ix(Tc,H)); s.set(22,4,ix(Pl,L)); s.set(23,4,ix(Pl,B))
    return outline(s)
def bush(berries=True):
    s=S(20,16)
    cl=[(10,6,6,5,0.3),(5,9,5,5,0.0),(15,9,5,5,-0.2),(10,11,7,4,-0.5)]
    clumps(s,cl,F,sd=17)
    if berries:
        for (x,y) in ((6,8),(12,6),(15,10),(9,11),(4,11)):
            s.set(x,y,ix(Tc,L)); s.set(x+1,y,ix(Tc,B)); s.set(x,y-1,WHITE) if (x+y)%2 else None
    return outline(s)
def mush_red():
    s=S(16,16)
    for (cx,cy,r,st) in ((5,7,4,5),(11,9,3,4),(8,12,2,2)):
        for y in range(cy+1,cy+1+st):
            for x in (cx-1,cx,cx+1): s.set(x,y,ix(Pl,L if x<cx+1 else S_))
        cap=m_ell(cx-r,cy-r+1,cx+r,cy+1)
        sphere(s,cap,Tc,0.2)
        for x in range(cx-r+1,cx+r): s.set(x,cy+1,ix(Pl,S_))
        for (dx,dy) in ((-1,-1),(1,0),(-2,0),(2,-1)):
            if (cx+dx,cy+dy) in cap: s.set(cx+dx,cy+dy,WHITE)
    return outline(s)
def mush_brown():
    s=S(16,16)
    for (cx,cy,r,st) in ((4,9,3,4),(9,8,4,5),(13,11,2,3)):
        for y in range(cy,cy+st+1):
            for x in (cx,cx+1): s.set(x,y,ix(Pl,L if x==cx else B))
        cap=m_ell(cx-r,cy-r+1,cx+r+1,cy+1); sphere(s,cap,E,0.1)
        s.set(cx-r+1,cy-r+2,ix(E,H))
    return outline(s)
def mush_glow(k):
    """champignons lumineux (bleus) - pulsent la nuit"""
    s=S(16,16)
    for (cx,cy,r,st) in ((5,8,3,5),(11,10,2,3),(9,5,2,3)):
        for y in range(cy+1,cy+1+st): s.set(cx,y,ix(Pl,H)); s.set(cx+1,y,ix(Bl,L))
        cap=m_ell(cx-r,cy-r+1,cx+r+1,cy+1); sphere(s,cap,Bl,0.6+0.4*k,lo=2)
        s.set(cx,cy-r+2,WHITE)
        for x in range(cx-r,cx+r+2): s.set(x,cy+1,ix(Bl,H) if k else ix(Bl,L))
    return outline(s)
def fern(k):
    s=S(18,18)
    for i,(ang,ln) in enumerate(((-155,9),(-125,12),(-92,13),(-58,12),(-25,9),(-108,9),(-75,9))):
        a=math.radians(ang+(4 if k else -2)*(1 if i%2 else -1))
        pts=[]
        for j in range(ln+1):
            bend=0.07*j*j*(1 if math.cos(a)>0 else -1)*0.25
            x=9+math.cos(a)*j; y=17+math.sin(a)*j+0.035*j*j
            pts.append((x,y))
        for j,(x,y) in enumerate(pts):
            xi,yi=int(round(x)),int(round(y))
            s.set(xi,yi,ix(F,B))
            if 1<j<len(pts)-1:          # folioles alternees
                nx,ny=-math.sin(a),math.cos(a)
                side=1 if j%2 else -1
                s.set(int(round(x+nx*side)),int(round(y+ny*side)),ix(F,L if ny*side<0 else S_))
                if j<len(pts)-3: s.set(int(round(x-nx*side)),int(round(y-ny*side)),ix(F,H if ny*side>0 else B))
        s.set(*[int(round(c)) for c in pts[-1]],ix(F,H))
    return outline(s)
def rock_s():
    s=S(16,14)
    m=m_ell(1,2,14,13); sphere(s,m,St,0.0,sd=5,tex=0.7)
    for (x,y) in ((6,6),(7,7),(7,8),(8,9)): s.set(x,y,ix(St,O))          # fissure
    for x in range(3,12):                                                 # mousse dessus
        if hsh(x,0,9)%4: s.set(x,2+(1 if x in (3,11) else 0),ix(G,L)); s.set(x,3+(1 if x in (3,11) else 0),ix(G,B) if x%2 else ix(St,L))
    return outline(s)
def rock_b():
    s=S(32,24)
    m1=m_ell(1,6,20,23); m2=m_ell(12,2,30,22)
    sphere(s,m1,St,-0.2,sd=3,tex=0.7); sphere(s,{p for p in m2 if p not in m1 or p[0]>15},St,0.2,sd=4,tex=0.7)
    for y in range(8,18): s.set(16+(y%3==0),y,ix(St,O))
    for x in range(8,26):
        top=min([y for (xx,y) in m1|m2 if xx==x] or [0])
        if hsh(x,1,2)%5: s.set(x,top,ix(G,L)); s.set(x,top+1,ix(G,B))
        if hsh(x,3,2)%4==0: s.set(x,top+2,ix(G,S_))
    s.set(14,4,ix(St,H)); s.set(15,3,ix(St,H))
    return outline(s)
def bridge():
    """pont de bois 64x24: planches transversales, cordes + poteaux, ombre sur l'eau"""
    s=S(64,26)
    for x in range(2,62):
        for y in range(6,19):
            plank=(x-2)//4; k=(x-2)%4
            t=L if k==0 else (S_ if k==3 else B)
            if hsh(plank,y//5,4)%7==0 and k==1: t=S_      # noeuds
            if y==6: t=H if k<3 else L
            if y==18: t=S_
            if plank%5==2 and y in (8,15): t=O            # clous
            s.set(x,y+(1 if plank%7==3 and y==18 else 0),ix(Wd,t))
    for x in range(2,62): s.set(x,19,ix(Wd,O)); s.set(x,20,ix(Bl,O)); s.set(x,21,ix(Bl,O) if x%2 else None) if True else None
    for px_ in (1,59):
        for (y0,y1) in ((0,8),(13,22)):
            for y in range(y0,y1):
                for dx in range(4): s.set(px_+dx,y,ix(Wd,[L,B,B,S_][dx]))
            s.set(px_,y0,ix(Wd,H)); s.set(px_+1,y0,ix(Wd,H))
    for (ry,sag) in ((2,2),(15,2)):          # cordes
        for x in range(5,59):
            yy=ry+int(sag*math.sin(math.pi*(x-5)/54))
            s.set(x,yy,ix(E,L) if x%3 else ix(E,B)); s.set(x,yy+1,ix(E,S_)) if x%3==0 else None
    return outline(s)
def waterfall(k):
    """cascade 32x52, 4 frames: filets d'eau verticaux qui descendent, rebord brillant, bouillon d'ecume"""
    s=S(32,52)
    for y in range(0,44):
        w0=4-(1 if y>6 else 0)-(1 if y>20 else 0); w1=27+(1 if y>6 else 0)+(1 if y>20 else 0)
        for x in range(w0,w1+1):
            if y==0: s.set(x,y,ix(Bl,L)); continue
            if y<3: s.set(x,y,WHITE if (x+k*2)%5==0 else ix(Bl,H)); continue
            col=hsh(x,0,7)%4                         # filet: 0 sombre .. 3 clair
            base=[1.6,2.1,2.6,3.0][col]-0.6*((x-w0)/(w1-w0))+0.5
            ph=(y-k*4+hsh(x,1,7)%12)%12              # segments clairs qui descendent
            if ph<3 and col>=1: base+=1.3
            elif ph<5 and col>=2: base+=0.6
            if x in (w0,w1): base=1.0
            t=int(max(1,min(4,round(base))))
            s.set(x,y,ix(Bl,t) if not (t==4 and ph==0 and col==3) else WHITE)
    for i in range(12):                    # bouillon
        a=i*30+k*17; cx=16+math.cos(math.radians(a))*(10+(i%3)); cy=45+math.sin(math.radians(a))*2.5
        r=2+((i+k)%3==0)
        for p in m_ell(int(cx-r),int(cy-r),int(cx+r),int(cy+r)):
            if p[1]<52: s.set(*p,WHITE if (p[0]+p[1]+k)%4 else ix(Bl,H))
    for (x,y) in ((2,40-k),(29,39-(k+2)%4),(7,36-(k*2)%4),(25,35-(k*3)%4),(14,38-(k+1)%4)): s.set(x,y,WHITE)
    return s
# ------------------------------------------------------------ ennemis de la foret
def sporeling(k,mode='walk'):
    """champignon vivant 16x16 (regarde a droite). walk 4 frames / attack 0-1 (nuage de spores)"""
    s=S(24,24); ox,oy=4,6
    bob=[0,-1,0,-1][k%4] if mode=='walk' else 0
    sq=1 if (mode=='attack' and k==0) else 0
    # pattes
    if mode=='walk':
        lx=[(5,10),(6,9),(5,10),(4,11)][k%4]
    else: lx=(4,11)
    for x in lx:
        s.set(ox+x,oy+15,ix(Pl,S_)); s.set(ox+x+1,oy+15,ix(Pl,S_)); s.set(ox+x,oy+14,ix(Pl,B))
    # corps (pied)
    body=m_ell(ox+4,oy+8+bob,ox+11,oy+15+bob-1)
    sphere(s,body,Pl,0.2)
    # yeux + bouche
    ey=oy+10+bob
    for ex in (ox+8,ox+10):
        s.set(ex,ey,BLACK); s.set(ex,ey+1,BLACK); s.set(ex,ey-1,ix(Pl,H))
    s.set(ox+8,ey,WHITE)
    s.set(ox+9,ey+3,ix(Tc,O)); s.set(ox+10,ey+3,ix(Tc,O))
    # chapeau
    cap=m_ell(ox+0-sq,oy+1+bob+sq*2,ox+15+sq,oy+10+bob)
    cap={p for p in cap if p[1]<=oy+8+bob+sq}
    sphere(s,cap,Tc,0.15)
    for x in range(ox+1-sq,ox+15+sq): s.set(x,oy+8+bob+sq,ix(Pl,S_)); s.set(x,oy+9+bob+sq,ix(Pl,O)) if x%2 else None
    for (dx,dy,r) in ((3,3,1),(9,2,1),(12,5,0),(6,6,0),(1,6,0)):
        for p in m_ell(ox+dx-r,oy+dy+bob+sq,ox+dx+r,oy+dy+bob+r+sq):
            if p in cap: s.set(*p,WHITE if p[0]<=ox+dx else ix(Pl,L))
    outline(s)
    if mode=='attack' and k==1:            # nuage de spores
        rng=random.Random(5)
        for i in range(22):
            a=rng.uniform(-math.pi,0.2); d=rng.uniform(5,11)
            x=int(12+math.cos(a)*d*1.1); y=int(8+math.sin(a)*d*0.8)
            c=GOLD if i%3==0 else (ix(G,H) if i%3==1 else ix(E,H))
            if s.get(x,y) is None: s.set(x,y,c)
            if i%4==0 and s.get(x+1,y) is None: s.set(x+1,y,ix(E,L))
    return s
def thornboar(k,mode='walk'):
    """sanglier-ronce 28x20 (regarde a droite): dos couvert de ronces, defenses, oeil braise"""
    s=S(32,22); ox=2; oy=2
    run=mode=='walk'; ch=mode=='attack'
    hd=2 if ch else 0
    # pattes (cycle de course)
    leg=[(0,2,2,0),(1,1,1,1),(2,0,0,2),(1,1,1,1)][k%4] if run else ((0,2,0,2) if k==0 else (2,0,2,0))
    for i,(lx) in enumerate((5,9,17,21)):
        off=leg[i]
        for y in range(14,19): s.set(ox+lx+(off-1 if y>16 else 0),oy+y,ix(Wd,S_ if y>16 else B))
        s.set(ox+lx+(off-1),oy+19,ix(Wd,O)); s.set(ox+lx+off,oy+19,ix(Wd,O))
    bodyy=oy+([0,-1,0,-1][k%4] if run else 1)
    body=m_ell(ox+1,bodyy+5,ox+22,bodyy+16)
    sphere(s,body,Wd,0.0)
    for (x,y) in body:                     # poil hirsute
        if hsh(x,y,6)%9==0 and (x+1,y+1) in body: s.set(x,y,ix(Wd,S_)); s.set(x+1,y+1,ix(Wd,S_))
    # tete
    hx=ox+18; hy=bodyy+6+hd
    head=m_ell(hx,hy,hx+9,hy+8)
    sphere(s,head,Wd,0.25)
    snout=m_rect(hx+8,hy+3,hx+10,hy+6); sphere(s,snout,E,0.4)
    s.set(hx+10,hy+4,ix(E,O)); s.set(hx+10,hy+5,ix(E,O))
    s.set(hx+5,hy+2,ix(Tc,H)); s.set(hx+6,hy+2,GOLD); s.set(hx+5,hy+1,ix(Wd,O)); s.set(hx+6,hy+1,ix(Wd,O))  # oeil braise + sourcil
    for (x,y) in ((hx+8,hy+7),(hx+9,hy+6),(hx+10,hy+5)): s.set(x,y,WHITE)   # defense
    s.set(hx+11,hy+4,ix(Pl,L))
    s.set(hx+2,hy-1,ix(Wd,B)); s.set(hx+3,hy-2,ix(Wd,L)); s.set(hx+3,hy-1,ix(Wd,S_))   # oreille
    # ronces sur le dos
    for x in range(ox+3,ox+20):
        y=bodyy+5+int(1.8*(1-((x-ox-11)/9)**2))*-1+1
        s.set(x,y,ix(F,B)); s.set(x,y+1,ix(F,S_))
        if x%2==0: s.set(x,y-1,ix(F,L))
        if x%4==1: s.set(x,y-2,ix(Pl,H)); s.set(x,y-1,ix(F,H))       # epines
        if x%6==3: s.set(x,y+2,ix(Tc,L))                                # baie
    outline(s)
    if ch:                                  # poussiere de charge
        for i,(x,y,r) in enumerate(((1,17,2),(4,19,1),(0,13,1))):
            r+=k
            for p in m_ell(x-r,y-r,x+r,y+r):
                if 0<=p[0]<32 and 0<=p[1]<22 and s.get(*p) is None: s.set(*p,ix(E,H) if (p[0]+p[1])%2 else ix(E,L))
    return s
def leafbat(k,mode='fly'):
    """chauve-souris-feuille 20x16: ailes en feuilles nervurees, 4 frames de vol / piqué"""
    s=S(22,18); cx=11; cy=8
    if mode=='fly':
        wy=[-5,-1,3,-1][k%4]; by=[0,1,2,1][k%4]
    else: wy=-6; by=2
    cy+=by
    for side in (-1,1):
        tip=(cx+side*10,cy+wy) if mode=='fly' else (cx+side*5,cy-7)
        root=(cx+side*2,cy)
        poly=[root,(cx+side*5,cy-2+wy//2),tip,(cx+side*7,cy+3+wy//3),(cx+side*3,cy+3)]
        poly=[(max(0,min(21,int(a))),max(0,min(17,int(b)))) for a,b in poly]
        m=m_poly(poly)
        for (x,y) in m:
            v=2.5-(0.6 if side>0 else -0.2)-((y-cy)/6)*0.6
            s.set(x,y,ix(F,dt(v,x,y)))
        for t in range(12):                  # nervure
            x=int(root[0]+(tip[0]-root[0])*t/11); y=int(root[1]+(tip[1]-root[1])*t/11)
            if (x,y) in m: s.set(x,y,ix(F,H) if side<0 else ix(F,L))
    body=m_ell(cx-3,cy-3,cx+3,cy+4); sphere(s,body,Wd,0.1)
    s.set(cx-2,cy-4,ix(Wd,B)); s.set(cx+2,cy-4,ix(Wd,B))           # oreilles
    s.set(cx-1,cy-1,GOLD); s.set(cx+1,cy-1,GOLD); s.set(cx,cy+2,WHITE)
    outline(s)
    if mode=='dive':
        for i in range(5): s.set(cx-6+i,cy-9+i,ix(F,L) if s.get(cx-6+i,cy-9+i) is None else s.get(cx-6+i,cy-9+i))
    return s
def burst(sp,k,n=4):
    """mort: le sprite eclate en particules de ses propres couleurs (k=0 flash .. 3 etincelles)"""
    M=12; W2=sp.w+2*M; H2=sp.h+2*M; s=S(W2,H2)
    if k==0:
        s.paste(flash(sp),M,M); return s
    cx,cy=sp.w/2,sp.h/2
    for y in range(sp.h):
        for x in range(sp.w):
            v=sp.p[y][x]
            if v is None or (x+y)%(1+k)!=0: continue
            h=hsh(x,y,k)
            if k==3 and h%3!=0: continue
            dx,dy=x-cx,y-cy; d=math.hypot(dx,dy)+0.1
            sp_=k*(1.6+(h%5)*0.45)
            nx=int(x+M+dx/d*sp_); ny=int(y+M+dy/d*sp_-k*0.5)
            c=v if k==1 else (ix(ramp_of(v),min(4,tone_of(v)+1)) if v<45 else v)
            if k==3: c=WHITE if h%2 else GOLD
            s.set(nx,ny,c)
            if k==3 and h%3==0:
                for ddx,ddy in ((1,0),(-1,0),(0,1),(0,-1)): s.set(nx+ddx,ny+ddy,ix(E,H))
    return s
# ------------------------------------------------------------ effets
def firefly(k):
    s=S(7,7)
    r=[1,2,2,1][k]
    for (x,y) in m_ell(3-r,3-r,3+r,3+r):
        if (x+y)%2==0 or r==1: s.set(x,y,ix(G,H))
    s.set(3,3,WHITE if k in (1,2) else GOLD)
    return s
def leaf(k,r=E):
    s=S(7,7)
    shapes=[[(1,3),(2,2),(3,2),(4,3),(5,4),(2,3),(3,3),(4,4)],[(3,1),(3,2),(3,3),(3,4),(2,2),(4,3),(3,5)],
            [(1,4),(2,4),(3,3),(4,3),(5,2),(2,3),(4,2)],[(2,3),(3,3),(4,3),(3,2),(3,4)]]
    for i,(x,y) in enumerate(shapes[k]): s.set(x,y,ix(r,[H,L,B,S_][i%4]))
    return s
def spore(k):
    s=S(5,5); s.set(2,2,GOLD);
    if k: s.set(1,2,ix(G,H)); s.set(3,2,ix(G,H))
    return s
