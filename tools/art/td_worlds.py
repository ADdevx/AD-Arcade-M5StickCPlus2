# POCKET SIEGE : nouveau portail + 4 mondes (prairie, desert, neige, volcan) + carte du monde + boutique
from td import *
from boss import basalt_floor, lava_c
from crypt import bones

# ------------------------------------------------------------ nouveau portail : arche runique + faille de braise
def rift_portal(k):
    s=S(30,34)
    arch=m_rect(1,10,8,33)|m_rect(21,10,28,33)|m_ell(1,0,28,20)
    inner=m_rect(8,11,21,33)|m_ell(8,6,21,24)
    for (x,y) in arch:
        if (x,y) in inner: continue
        v=3.3-((x-1)/27)*2.2+(0.5 if y<8 else 0)
        if (x*3+y)%7==0: v-=0.8
        s.set(x,y,ix(St,dt(v,x,y)))
    for y in range(12,34,5):                                    # joints des pierres
        for x in list(range(1,9))+list(range(21,29)): s.set(x,y,ix(St,O))
    # faille : tourbillon sombre aux bords incandescents
    for (x,y) in inner:
        dx,dy=(x-14.5)/7,(y-18)/13; d=math.hypot(dx,dy)
        a=math.atan2(dy,dx)+k*0.8-d*4
        sw=(math.sin(a*2)+1)/2
        if d>0.85: c=ix(Tc,H) if (x+y+k)%2 else GOLD
        elif d>0.65: c=ix(Tc,B) if sw>0.5 else ix(Tc,S_)
        else: c=BLACK if sw<0.55 else (ix(Tc,O) if d>0.3 else ix(Tc,S_))
        if d<0.18: c=ix(Tc,H) if k%2 else GOLD
        s.set(x,y,c)
    for i,(x,y) in enumerate(((4,14),(4,22),(4,29),(25,14),(25,22),(25,29),(14,2))):   # runes qui s'allument tour a tour
        on=(i+k)%3==0
        s.set(x,y,GOLD if on else ix(Tc,S_)); s.set(x+1,y+1,ix(E,H) if on else ix(St,S_))
    s=outline(s)
    for i in range(4):                                           # cailloux qui levitent + braises
        a=i*90+k*25; x=int(15+math.cos(math.radians(a))*13); y=int(20+math.sin(math.radians(a))*5)-((k+i)%3)
        if 0<=x<30 and 0<=y<34 and s.get(x,y) is None: s.set(x,y,ix(St,L)); s.set(x+1,y,ix(St,S_)) if s.get(x+1,y) is None else None
    for i in range(3):
        x=10+i*5; y=4-((k*2+i*3)%5)
        if 0<=y: s.set(x,y,GOLD if i%2 else ix(Tc,H))
    return s

# ------------------------------------------------------------ sols par monde
def sand_t(v):
    s=S(16,16)
    for y in range(16):
        for x in range(16):
            n=fnoise(x,y,120+v); t=dt(2.9+n*0.8+0.4*math.sin((x+y*2+v*5)*0.5),x,y,2,4)
            s.set(x,y,ix(E,t))
    rng=random.Random(v)
    for _ in range(2):
        x,y=rng.randrange(2,14),rng.randrange(2,14); s.set(x,y,ix(Tc,B)); s.set(x+1,y,ix(E,S_))
    return s
def snow_t(v):
    s=S(16,16)
    for y in range(16):
        for x in range(16):
            n=fnoise(x,y,140+v); t=dt(3.3+n*0.9,x,y,2,4)
            s.set(x,y,WHITE if t>=4 else (ix(Bl,H) if t==3 else ix(Bl,L)))
    rng=random.Random(v+9)
    for _ in range(3):
        x,y=rng.randrange(1,15),rng.randrange(1,15); s.set(x,y,ix(Bl,H)); s.set(x+1,y+1,WHITE)
    return s
def ash_t(v):
    s=S(16,16)
    for y in range(16):
        for x in range(16):
            n=fnoise(x,y,160+v); t=dt(1.9+n*0.9,x,y,1,3)
            s.set(x,y,ix(Tc,t) if hsh(x//2,y//2,v)%5 else ix(Wd,t))
    rng=random.Random(v+3)
    for _ in range(2):                                   # fissures rougeoyantes
        x,y=rng.randrange(2,12),rng.randrange(2,14)
        for i in range(4): s.set(x+i,y+(i%2),GOLD if i%2 else ix(E,H))
    return s
GROUNDS={'meadow':grass_t,'desert':sand_t,'snow':snow_t,'volcano':ash_t}
def world_path(world,mask):
    base=GROUNDS[world](mask%4)
    inn=lambda x,y: cfield(mask,x,y,11)>=0.5
    R_,lo,mid={'meadow':(E,2,2.6),'desert':(Tc,1,2.2),'snow':(Bl,2,3.1),'volcano':(St,2,3.0)}[world]
    for y in range(16):
        for x in range(16):
            f=cfield(mask,x,y,11)
            if f>=0.5:
                if not inn(x,y-1) or not inn(x-1,y): t=lo
                elif not inn(x,y+1) or not inn(x+1,y): t=4
                else: t=dt(mid+fnoise(x,y,77)*0.6,x,y,lo,4)
                c=ix(R_,t)
                if world=='volcano' and hsh(x,y,mask)%23==0: c=ix(Tc,H)        # braises dans la cendre
                if world=='snow' and t>=4 and hsh(x,y,5)%3==0: c=WHITE
                base.set(x,y,c)
                if world=='desert' and hsh(x,y,mask)%37==0: base.set(x,y,ix(E,H))
            elif f>0.42:
                edge={'meadow':ix(G,S_),'desert':ix(E,B),'snow':ix(Bl,L),'volcano':ix(Tc,S_)}[world]
                if (x+y)%2: base.set(x,y,edge)
    return base

# ------------------------------------------------------------ decor par monde
def cactus(v):
    s=S(16,26)
    trunk_=m_rect(6,4,10,25)|m_ell(6,2,10,7)
    arms=[m_rect(1,10,3,17)|m_rect(1,16,6,18),m_rect(13,7,15,14)|m_rect(10,13,15,15)][:1+v]
    for m in [trunk_]+arms:
        for (x,y) in m:
            kx=(x-min(p[0] for p in m))/max(1,(max(p[0] for p in m)-min(p[0] for p in m)))
            v_=3.3-kx*2;
            if x%3==1: v_-=0.7
            s.set(x,y,ix(G,dt(v_,x,y)))
    for y in range(5,24,3): s.set(5,y,ix(Pl,H)); s.set(11,y+1,ix(Pl,H))     # epines
    s.set(8,1,ix(Tc,H)); s.set(7,1,ix(Tc,L)); s.set(9,1,ix(Tc,L))           # fleur
    return outline(s)
def mesa_rock(v):
    s=S(26,18)
    m=m_poly([(1,17),(4,5),(10,2),(18,3),(24,8),(25,17)])
    for (x,y) in m:
        v_=3.2-(x/25)*1.8+(0.6 if y<6 else 0)
        if (y+v)%4==0: v_-=0.6
        s.set(x,y,ix(Tc if (y//4)%2 else E,dt(v_,x,y)))
    return outline(s)
def skull_bones():
    s=bones(); return s
def palm():
    s=S(28,36)
    for i in range(24):
        x=int(13+math.sin(i*0.12)*3); y=35-i
        s.set(x,y,ix(Wd,L) if i%3 else ix(Wd,S_)); s.set(x+1,y,ix(Wd,B)); s.set(x+2,y,ix(Wd,S_))
    cx,cy=int(13+math.sin(23*0.12)*3)+1,11
    for a in (200,240,290,330,20,150):
        for d in range(13):
            x=int(cx+math.cos(math.radians(a))*d); y=int(cy+math.sin(math.radians(a))*d*0.6+0.03*d*d)
            s.set(x,y,ix(G,B)); s.set(x,y+1,ix(G,S_));
            if d%2: s.set(x,y-1,ix(G,L))
    for p in ((cx-1,cy+1),(cx+1,cy+2)): s.set(*p,ix(Wd,O))
    return outline(s)
def snowy_pine():
    src=pine(); s=src.copy()
    for x in range(s.w):
        for y in range(s.h):
            v=src.get(x,y)
            if v is None or ramp_of(v)!=F: continue
            if src.get(x,y-1) is None or ramp_of(src.get(x,y-1))!=F: s.set(x,y,WHITE)
            elif (src.get(x,y-2) is None or ramp_of(src.get(x,y-2))!=F) and hsh(x,y,3)%3: s.set(x,y,ix(Bl,H))
    return s
def snowman():
    s=S(18,24)
    sphere(s,m_ell(2,11,15,23),Pl,0.4,lo=2); sphere(s,m_ell(4,4,13,13),Pl,0.5,lo=2)
    for p in ((7,7),(10,7)): s.set(*p,BLACK)
    s.set(9,9,ix(Tc,H)); s.set(10,9,ix(Tc,B)); s.set(11,9,ix(E,B))
    for x in range(4,14): s.set(x,12,ix(Tc,B))
    for p in m_rect(5,0,12,4): s.set(*p,ix(St,O))
    for x in range(3,15): s.set(x,4,ix(St,S_))
    for y in (15,18,21): s.set(8,y,ix(St,O))
    return outline(s)
def ice_rock():
    s=S(18,14)
    m=m_poly([(1,13),(3,4),(8,1),(14,3),(17,13)]); sphere(s,m,Bl,0.6,lo=2)
    s.set(6,4,WHITE); s.set(7,3,WHITE)
    return outline(s)
def dead_tree():
    s=S(22,28)
    for i in range(20): s.set(10+(i//7),27-i,ix(St,B)); s.set(11+(i//7),27-i,ix(St,O))
    for (x0,y0,dx) in ((11,14,-1),(12,10,1),(12,18,1)):
        for i in range(7): s.set(x0+dx*i,y0-i//2,ix(St,B))
    return outline(s)
def vent(k):
    s=S(16,22)
    sphere(s,m_ell(1,15,14,21),St,-0.2)
    for p in m_ell(5,16,10,19): s.set(*p,ix(Tc,H) if k%2 else GOLD)
    for i in range(3):
        y=13-i*4-(k%2)*2; x=7+[0,1,-1][(i+k)%3]
        for p in m_ell(x-1-i//2,y-1,x+1+i//2,y+1): s.set(*p,ix(St,L) if i<2 else ix(St,H))
    return s
WORLD_DECOR={
 'meadow':[('TREE',tree_round(0)),('TREE 2',tree_round(1)),('BUSH',bush()),('ROCK',rock_s())],
 'desert':[('CACTUS',cactus(0)),('CACTUS 2',cactus(1)),('MESA',mesa_rock(0)),('PALM',palm()),('BONES',skull_bones())],
 'snow':[('PINE',snowy_pine()),('SNOWMAN',snowman()),('ICE',ice_rock()),('ROCK',rock_s())],
 'volcano':[('DEAD TREE',dead_tree()),('VENT A',vent(0)),('VENT B',vent(1)),('ROCK',rock_b())],
}

# ------------------------------------------------------------ carte du monde (selection des niveaux)
def level_node(state):
    """0 verrouille, 1 ouvert, 2..4 = 1 a 3 etoiles"""
    s=S(18,18)
    if state==0: sphere(s,m_ell(1,1,16,16),St,-0.3);
    else: sphere(s,m_ell(1,1,16,16),Tc if state==1 else E,0.4)
    for p in m_ell(4,4,13,13): s.set(*p,ix(St,S_) if state==0 else ix(Pl,H))
    if state==0:
        for p in m_rect(6,8,11,12): s.set(*p,ix(St,B))
        for x in (7,10): s.set(x,6,ix(St,B)); s.set(x,7,ix(St,B))
        s.set(7,5,ix(St,B)); s.set(8,5,ix(St,B)); s.set(9,5,ix(St,B)); s.set(10,5,ix(St,B))
    return outline(s)
def star_icon(on=True):
    s=S(9,9); pts=[]
    for i in range(10):
        a=math.radians(-90+i*36); r=4.4 if i%2==0 else 1.9; pts.append((4+math.cos(a)*r,4+math.sin(a)*r))
    m=m_poly([(max(0,int(round(x))),max(0,int(round(y)))) for x,y in pts])
    for p in m: s.set(*p,GOLD if on else ix(St,S_))
    if on: s.set(3,3,WHITE)
    return outline(s)
# ------------------------------------------------------------ boutique d'ameliorations permanentes
def shop_icon(kind):
    s=S(20,20)
    paint(s,m_rect(0,0,19,19),Pl,bevel=True)
    if kind=='damage':
        for i in range(12): s.set(4+i,15-i,ix(St,H) if i%2 else ix(St,L)); s.set(5+i,15-i,ix(St,B))
        for p in m_rect(3,13,7,14): s.set(*p,GOLD)
    elif kind=='range':
        sphere(s,m_ell(3,5,16,14),Bl,0.4); sphere(s,m_ell(7,7,12,12),St,-0.5); s.set(8,8,WHITE)
    elif kind=='gold':
        sphere(s,m_ell(3,6,16,18),E,0.3); s.set(9,5,ix(E,O)); s.set(10,5,ix(E,O)); s.set(8,4,ix(E,B)); s.set(11,4,ix(E,B))
        for p in m_rect(8,10,11,14): s.set(*p,GOLD)
    elif kind=='lives':
        s.paste(heart_s2(),5,6)
    elif kind=='speed':
        for i in range(3):
            for p in m_poly([(4+i*4,5),(9+i*4,10),(4+i*4,15)]): s.set(*p,ix(G,L) if i<2 else ix(G,H))
    return outline(s)
