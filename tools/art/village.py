from humans import *
from hero_more import *
# ------------------------------------------------------------ PNJ
NPCS={
 'forgeron':dict(skin=Sk,hair=Wd,hairstyle='bald',beard=Wd,top=E,pants=Wd,boots=Wd,wd=1,bare=True,apron=St,prop='hammer',belt=False),
 'vieille': dict(skin=Sk,hair=Pl,hairstyle='bun',top=Pl,pants=Tc,boots=Wd,scarf=Bl,yo=1,prop='cane',lh=5),
 'enfant':  dict(skin=Sk,hair=E,hairstyle='cap',capcol=Tc,top=G,pants=Wd,boots=Wd,yo=4,th=4,lh=4),
 'marchand':dict(skin=Sk,hair=Wd,hairstyle='hat',hatcol=E,stache=Wd,top=F,pants=St,boots=Wd,yo=2,lh=4,pack=E,belt=True),
 'garde':   dict(skin=Sk,hair=Wd,hairstyle='helm',top=St,apron=Bl,pants=Bl,boots=St,yo=2,lh=4,prop='spear'),
}
def npc(name,d,f): return human(d,f,NPCS[name])
# ------------------------------------------------------------ outils batiments
def shingles(s,mask,r,band=3,sd=0):
    ys=[y for _,y in mask]; y0=min(ys)
    for (x,y) in mask:
        k=(y-y0)%band; row=(y-y0)//band
        up=(x,y-1) in mask; lf=(x-1,y) in mask; dn=(x,y+1) in mask; rt=(x+1,y) in mask
        t=B
        if k==band-1: t=S_
        elif k==0: t=L
        if (x+row*2)%4==0 and k!=0: t=S_ if t==B else t
        if not up and not lf: t=H
        elif not up: t=L if t!=H else t
        if not dn and not (t==H): t=S_
        if not rt and k!=band-1: t=S_
        s.set(x,y,ix(r,t))
def thatch(s,mask,r):
    for (x,y) in mask:
        h=hsh(x,y,3); t=B
        if (x*2+y)%5==0: t=S_
        elif h%7==0: t=L
        elif h%17==0: t=H
        if (x,y-1) not in mask: t=L
        if (x,y+1) not in mask: t=S_
        s.set(x,y,ix(r,t))
def logs(s,mask,r):
    ys=[y for _,y in mask]; y0=min(ys)
    for (x,y) in mask:
        k=(y-y0)%4; t=B
        if k==0: t=L
        elif k==3: t=S_
        elif (x*3+(y-y0)//4*5)%9==0: t=S_
        s.set(x,y,ix(r,t))
def window(s,x,y,w,h,shut=None,box=True,lit=False):
    paint(s,m_rect(x-1,y-1,x+w,y+h),Wd)
    paint(s,m_rect(x,y,x+w-1,y+h-1),Bl,bevel=False,tone=L if not lit else L)
    for yy in range(y,y+h):
        for xx in range(x,x+w):
            t=L if (xx-x+ (yy-y))%5 else H
            s.set(xx,yy,ix(Bl,B if (yy-y)>h//2 else L) if not lit else (ix(E,H) if (xx+yy)%3 else GOLD))
    for xx in range(x,x+w): 
        if (xx-x)==w//2: 
            for yy in range(y,y+h): s.set(xx,yy,ix(Wd,B))
    for yy in range(y,y+h):
        if (yy-y)==h//2:
            for xx in range(x,x+w): s.set(xx,yy,ix(Wd,B))
    if not lit: s.set(x,y,WHITE)
    if shut is not None:
        paint(s,m_rect(x-3,y-1,x-2,y+h),shut,tex='rows'); paint(s,m_rect(x+w+1,y-1,x+w+2,y+h),shut,tex='rows')
    if box:
        paint(s,m_rect(x-2,y+h+1,x+w+1,y+h+2),Wd)
        for i,xx in enumerate(range(x-1,x+w+1)):
            s.set(xx,y+h,ix(G,S_) if i%2 else ix(G,B))
            s.set(xx,y+h-1 if i%2 else y+h,[ix(Tc,H),WHITE,GOLD,ix(Tc,L)][i%4])
def door(s,x,y,w,h,r=Wd,round_=True):
    m=m_rect(x,y,x+w-1,y+h-1)
    if round_: m-={(x,y),(x+w-1,y)}
    paint(s,m,r,tex='hatch')
    for yy in range(y+2,y+h): s.set(x+w//2,yy,ix(r,S_))
    s.set(x+w-3,y+h//2,GOLD); 
    paint(s,m_rect(x-1,y+h,x+w,y+h),St)
def chimney(s,x,y,h=8,w=4):
    paint(s,m_rect(x,y,x+w-1,y+h-1),St,tex='noise'); paint(s,m_rect(x-1,y,x+w,y+1),St)
def wall(s,x0,y0,x1,y1,r=Pl,beams=True):
    paint(s,m_rect(x0,y0,x1,y1),r,tex='noise')
    if beams:
        for xx in (x0,x1-1): paint(s,m_rect(xx,y0,xx+1,y1),Wd,tex='hatch')
        paint(s,m_rect(x0,y0+(y1-y0)//2-1,x1,y0+(y1-y0)//2),Wd,tex='hatch')
    paint(s,m_rect(x0,y1-1,x1,y1),St,tex='noise')
def eave(s,x0,x1,y): 
    for x in range(x0,x1+1): s.set(x,y,ix(Pl,S_)); s.set(x,y+1,ix(Pl,S_) if x%2 else ix(Pl,B))
def house(roofr,shut,beams=False,chim=True):
    s=S(32,36)
    if chim: chimney(s,22,2,10)
    wall(s,2,18,29,35,beams=beams)
    paint(s,m_rect(4,19,27,19),Pl,tone=S_,bevel=False)
    paint(s,m_poly([(0,19),(6,6),(25,6),(31,19)]),roofr)
    shingles(s,m_poly([(0,19),(6,6),(25,6),(31,19)]),roofr)
    for x in range(1,31): s.set(x,19,ix(roofr,S_))
    eave(s,2,29,20)
    window(s,5,23,5,5,shut); window(s,22,23,5,5,shut)
    door(s,13,25,7,10)
    return outline(s)
def thatch_house():
    s=S(32,36); chimney(s,22,4,9)
    wall(s,3,21,28,35,beams=True)
    m=m_ell(-1,5,32,32)&m_rect(0,5,31,22)|m_rect(1,16,30,22)
    m={p for p in m if p[1]<=22}
    thatch(s,m,E)
    for x in range(3,29): s.set(x,22,ix(E,S_)); s.set(x,23,ix(Pl,S_))
    for (x,y) in ((8,18),(12,15),(20,17),(24,20),(15,20)): s.set(x,y,ix(E,H))
    window(s,6,25,4,4,Tc); window(s,22,25,4,4,Tc)
    door(s,13,27,6,8)
    return outline(s)
def cabin():
    s=S(32,36)
    paint(s,m_rect(3,19,28,35),Wd); logs(s,m_rect(3,19,28,35),Wd)
    for y in range(19,36,4):
        for x in (2,3,28,29): s.set(x,y,ix(Wd,L)); s.set(x,y+1,ix(Wd,L)); s.set(x,y+2,ix(Wd,S_))
    m=m_poly([(0,20),(7,7),(24,7),(31,20)]); paint(s,m,Wd)
    shingles(s,m,Wd,band=4)
    for (x,y) in ((12,10),(20,13)): s.set(x,y,ix(Wd,H))
    for x in range(1,31): s.set(x,20,ix(Wd,S_))
    window(s,6,24,5,5,G); door(s,19,26,7,9)
    # tas de bois
    paint(s,m_rect(3,32,10,35),Wd,tex='rows') if False else None
    return outline(s)
def forge():
    s=S(32,36); chimney(s,20,0,14,6)
    paint(s,m_rect(2,18,29,35),St,tex='noise')
    for y in range(18,36,4):
        for x in range(2,30):
            if (x+ (y//4)*3)%8==0: s.set(x,y,ix(St,S_)); s.set(x,y+1,ix(St,S_))
        for x in range(2,30): s.set(x,y,ix(St,L)) if (x+y)%3 else None
    m=m_poly([(0,19),(5,8),(26,8),(31,19)]); paint(s,m,St); shingles(s,m,St,band=3)
    for x in range(1,31): s.set(x,19,ix(St,S_))
    # fournaise
    paint(s,m_rect(6,23,15,35),St); paint(s,m_rect(8,26,13,34),BLACK if False else ix(St,O))
    paint(s,m_rect(9,28,12,34),Tc,tex='dither'); paint(s,m_rect(10,30,11,34),E,tone=H,bevel=False); s.set(10,31,WHITE)
    s.set(8,26,ix(Tc,H)); s.set(13,27,ix(Tc,L))
    # enclume + enseigne
    paint(s,m_rect(19,29,26,31),St); paint(s,m_rect(21,32,24,35),St); s.set(19,29,ix(St,H))
    paint(s,m_rect(26,23,28,24),Wd); paint(s,m_rect(26,24,27,27),St); s.set(27,26,ix(St,H))
    window(s,23,22,3,3,None,box=False)
    return outline(s)
def inn():
    s=S(48,40); chimney(s,6,0,10,5); chimney(s,36,2,8,5)
    wall(s,2,20,45,39,beams=True)
    m=m_poly([(0,21),(9,8),(38,8),(47,21)]); paint(s,m,Bl); shingles(s,m,Bl)
    for x in range(1,47): s.set(x,21,ix(Bl,S_))
    eave(s,2,45,22)
    for x0 in (6,16,32,40): window(s,x0,26,4,5,Tc if x0<20 else Bl,box=True)
    door(s,21,27,9,12); 
    # lucarne
    paint(s,m_poly([(20,14),(25,8),(30,14)]),Bl); shingles(s,m_poly([(20,14),(25,8),(30,14)]),Bl,band=2); window(s,23,11,3,3,None,box=False)
    # enseigne chope
    paint(s,m_rect(34,23,35,23),Wd); paint(s,m_rect(35,23,37,23),Wd)
    paint(s,m_rect(37,25,41,31),Wd) if False else None
    paint(s,m_rect(11,32,13,38),Wd,tex='rows') if False else None
    # lanternes
    for lx in (19,31): paint(s,m_rect(lx,24,lx+1,25),GOLD) ; s.set(lx,23,ix(St,O))
    return outline(s)
def shop():
    s=S(32,36)
    wall(s,2,17,29,35,beams=False)
    m=m_poly([(1,18),(5,8),(26,8),(30,18)]); paint(s,m,Wd); shingles(s,m,Wd,band=3)
    # auvent raye
    for i,x in enumerate(range(0,32)):
        r=Tc if (x//3)%2==0 else Pl
        for y in range(19,25):
            yy=y+(1 if (x%3==1) and y==24 else 0)
            t=L if y==19 else (S_ if y>=24 else B)
            s.set(x,y,ix(r,t))
    for x in range(0,32): s.set(x,25,ix(Wd,O))
    # vitrine + etal
    paint(s,m_rect(4,27,16,32),Bl,bevel=False,tone=L); 
    for x in range(5,16): 
        for y in range(28,32): s.set(x,y,ix(Bl,L if (x+y)%7 else H))
    for (x,y,c) in ((6,31,ix(Tc,B)),(8,31,GOLD),(10,30,ix(G,L)),(12,31,ix(Tc,H)),(14,30,GOLD)): s.set(x,y,c); s.set(x+1,y,c); s.set(x,y+1,ix(Wd,B)) if False else None
    paint(s,m_rect(3,33,17,34),Wd)
    door(s,21,27,7,8)
    # enseigne sac
    paint(s,m_rect(18,16,19,16),Wd); paint(s,m_ell(18,9,22,13),E); s.set(20,9,ix(E,H)); s.set(20,13,ix(E,S_))
    return outline(s)
def mill(k):
    s=S(40,52)
    # tour
    paint(s,m_poly([(8,52),(11,22),(29,22),(32,52)]),St,tex='noise')
    for y in range(24,52,4):
        for x in range(8,33):
            if (x+(y//4)*3)%7==0: s.set(x,y,ix(St,S_))
    paint(s,m_poly([(11,22),(8,52),(10,52),(13,22)]),St,tone=L,bevel=False) if False else None
    paint(s,m_rect(11,20,29,23),Wd,tex='rows')
    # toit conique
    m=m_poly([(7,21),(20,6),(33,21)]); paint(s,m,Tc); shingles(s,m,Tc,band=3)
    for x in range(8,33): s.set(x,21,ix(Tc,S_))
    door(s,17,42,7,10); window(s,18,30,4,5,Wd,box=False)
    # pales
    cx,cy=20,13
    for i in range(4):
        a=math.radians(45*k+90*i+20)
        ex,ey=cx+math.cos(a)*15,cy+math.sin(a)*15
        paint(s,m_line(cx,cy,ex,ey,1),Wd,bevel=False,tone=B)
        # toile
        ax=a+math.radians(90); 
        px0,py0=cx+math.cos(a)*7,cy+math.sin(a)*7
        poly=[(px0,py0),(ex,ey),(ex+math.cos(ax)*5,ey+math.sin(ax)*5),(px0+math.cos(ax)*5,py0+math.sin(ax)*5)]
        mm={(int(x),int(y)) for (x,y) in [(0,0)]}
        mp=m_poly([(max(0,int(round(a_))),max(0,int(round(b_)))) for a_,b_ in poly])
        paint(s,mp,Pl,tex='hatch',bevel=True)
    paint(s,m_ell(cx-2,cy-2,cx+2,cy+2),Wd); s.set(cx,cy,GOLD)
    return outline(s)
def smoke(k):
    s=S(10,14)
    for i in range(4):
        t=(k+i)%4; y=11-i*3-(t%2); x=4+[0,1,0,-1][ (k+i)%4]+ (i//2); r=1+i//2
        for (px_,py_) in m_ell(x-r,y-r,x+r,y+r):
            s.set(px_,py_,ix(Pl,[H,L,B,S_][min(3,i)]) if i<3 else ix(St,L))
    return s
# ------------------------------------------------------------ props
def tile16(): return S(16,16)
def grass_t(v):
    s=S(16,16); paint(s,m_rect(0,0,15,15),G,bevel=False,tex='grass',sd=v)
    rng=random.Random(v*11)
    for _ in range(3):
        x,y=rng.randrange(2,14),rng.randrange(3,14)
        for dx,dy,t in ((0,0,L),(1,-1,H),(-1,-1,L),(0,1,S_)): s.set(x+dx,y+dy,ix(G,t))
    return s
def grass_sway(k):
    s=grass_t(2)
    for (x,y) in ((3,8),(7,5),(11,9),(13,4),(5,12)):
        o=[0,1][k]
        for i in range(4): s.set(x+(o if i>=2 else 0)*1+(1 if i==3 and o else 0),y-i,ix(G,[B,L,L,H][i]))
        s.set(x,y+1,ix(G,S_))
    return s
def cobble():
    s=S(16,16); paint(s,m_rect(0,0,15,15),St,bevel=False,tone=S_)
    for (x0,y0,w,h) in ((0,0,5,4),(5,0,6,4),(11,0,5,4),(0,4,3,4),(3,4,6,4),(9,4,7,4),(0,8,6,4),(6,8,5,4),(11,8,5,4),(0,12,4,4),(4,12,7,4),(11,12,5,4)):
        m=m_rect(x0,y0,x0+w-2,y0+h-2); paint(s,m,St,tex='noise',sd=x0*3+y0)
    return s
def path_auto(mask):
    n,e,so,w=[(mask>>i)&1 for i in range(4)]
    s=S(16,16); paint(s,m_rect(0,0,15,15),G,bevel=False,tex='grass',sd=5)
    area=set()
    def jit(a): return 0 if a in (0,15) else (1 if hsh(a,mask,9)%3==0 else 0)
    area|=m_rect(3,3,12,12)
    if n: area|=m_rect(3,0,12,3)
    if so: area|=m_rect(3,12,12,15)
    if w: area|=m_rect(0,3,3,12)
    if e: area|=m_rect(12,3,15,12)
    # arrondir coins
    for (cx,cy,a,b) in ((3,3,w,n),(12,3,e,n),(3,12,w,so),(12,12,e,so)):
        if not (a and b): area-={(cx,cy)}
    # bords irreguliers
    out=set(area)
    for (x,y) in list(area):
        edge=False
        for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
            if (x+dx,y+dy) not in area and 0<=x+dx<16 and 0<=y+dy<16: edge=True
        if edge and 0<x<15 and 0<y<15 and hsh(x,y,mask)%5==0: out.discard((x,y))
    for (x,y) in out: s.set(x,y,ix(E,B))
    for (x,y) in out:
        t=B; h=hsh(x,y,2)
        if (x,y-1) not in out or (x-1,y) not in out: t=L
        if (x,y+1) not in out or (x+1,y) not in out: t=S_
        if t==B:
            if h%6==0: t=S_
            elif h%9==0: t=L
            elif h%31==0: t=H
        s.set(x,y,ix(E,t))
    # franges d'herbe fonce autour
    for y in range(16):
        for x in range(16):
            if (x,y) in out: continue
            if any((x+dx,y+dy) in out for dx,dy in ((1,0),(-1,0),(0,1),(0,-1))): s.set(x,y,ix(G,S_) if (x+y)%2 else ix(G,B))
    return s
def flowers(c):
    s=grass_t(c+3)
    for i,(x,y) in enumerate(((4,5),(10,9),(7,12),(12,4))):
        col=[ix(Tc,H),WHITE,GOLD,ix(Bl,L)][(i+c)%4]
        s.set(x,y,GOLD if i%2 else WHITE); 
        for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)): s.set(x+dx,y+dy,col)
        s.set(x,y+2,ix(G,S_))
    return s
def garden(k):
    s=S(16,16); paint(s,m_rect(0,0,15,15),E,bevel=False,tex='noise',sd=k)
    for r in (3,8,13):
        for x in range(0,16): s.set(x,r,ix(E,S_)); s.set(x,r+1,ix(E,O)) if r<13 else None
    for r,xs in ((2,(2,7,12)),(7,(4,9,14)),(12,(2,7,12))):
        for x in xs:
            if k==0:  # choux
                paint(s,m_ell(x-2,r-2,x+2,r+2),G,tex='noise'); s.set(x-1,r-1,ix(G,H))
            else:     # carottes
                s.set(x,r-1,ix(G,B)); s.set(x-1,r-2,ix(G,L)); s.set(x+1,r-2,ix(G,L)); s.set(x,r,ix(Tc,H)); s.set(x,r+1,ix(Tc,B))
    return outline_inplace(s) if False else s
def fence(kind):
    s=S(16,16)
    if kind=='h':
        for x0 in (1,12): paint(s,m_rect(x0,5,x0+2,15),Wd,tex='hatch')
        paint(s,m_rect(0,7,15,8),Wd); paint(s,m_rect(0,11,15,12),Wd)
        for x0 in (1,12): s.set(x0,5,ix(Wd,H))
    elif kind=='v':
        paint(s,m_rect(6,0,9,15),Wd,tex='hatch'); paint(s,m_rect(6,3,9,3),Wd,tone=L,bevel=False)
        paint(s,m_rect(5,0,5,15),Wd) if False else None
        paint(s,m_rect(7,0,8,15),Wd,tex='hatch')
        paint(s,m_rect(5,2,10,3),Wd); paint(s,m_rect(5,9,10,10),Wd)
    else:
        paint(s,m_rect(6,3,9,15),Wd,tex='hatch'); paint(s,m_rect(6,3,9,3),Wd,tone=L,bevel=False)
        paint(s,m_rect(9,7,15,8),Wd); paint(s,m_rect(9,11,15,12),Wd)
    return outline(s)
def barrel():
    s=S(16,16); paint(s,m_ell(2,3,13,15),Wd,tex='hatch')
    for y in (6,12): paint(s,m_rect(3,y,12,y),St,tone=B)
    paint(s,m_ell(3,3,12,7),Wd,tone=L); s.set(7,5,ix(Wd,H))
    return outline(s)
def crate():
    s=S(16,16); paint(s,m_rect(2,4,13,15),Wd,tex='hatch'); 
    for i in range(12): s.set(2+i,4+i//1 if i<12 else 0,ix(Wd,S_)) if False else None
    paint(s,m_rect(2,4,13,5),Wd); paint(s,m_rect(2,14,13,15),Wd); paint(s,m_rect(2,4,3,15),Wd); paint(s,m_rect(12,4,13,15),Wd)
    for (x,y,c) in ((6,8,ix(Tc,B)),(8,9,GOLD),(10,8,ix(G,L)),(7,11,ix(Tc,H))): s.set(x,y,c)
    return outline(s)
def haystack():
    s=S(16,16); m=m_ell(1,3,14,15); thatch(s,m,E)
    for (x,y) in ((5,6),(9,9),(4,11),(11,5)): s.set(x,y,ix(E,H))
    return outline(s)
def bench():
    s=S(16,16); paint(s,m_rect(1,6,14,8),Wd,tex='hatch'); paint(s,m_rect(1,9,14,10),Wd)
    for x in (2,12): paint(s,m_rect(x,10,x+1,14),Wd)
    paint(s,m_rect(1,3,14,4),Wd)
    return outline(s)
def signpost(txt=0):
    s=S(16,16); paint(s,m_rect(7,6,8,15),Wd,tex='hatch')
    paint(s,m_rect(2,2,13,7),Wd,tex='rows'); paint(s,m_poly([(13,2),(15,4),(13,7)]),Wd)
    for x in (4,6,9): s.set(x,4,ix(Wd,O))
    s.set(3,3,GOLD); 
    return outline(s)
def well():
    s=S(16,24)
    paint(s,m_rect(2,0,13,5),Tc); shingles(s,m_rect(2,0,13,5),Tc,band=2); paint(s,m_poly([(1,6),(8,-1),(14,6)]),Tc) if False else None
    for x in (3,12): paint(s,m_rect(x,5,x+1,15),Wd,tex='hatch')
    paint(s,m_rect(6,8,9,9),Wd); s.set(7,10,ix(Wd,L)); s.set(7,11,ix(Wd,L)); paint(s,m_rect(6,12,9,13),E,tone=B) if False else None
    paint(s,m_ell(1,13,14,23),St,tex='noise')
    paint(s,m_ell(3,14,12,20),Bl,tex='dither'); s.set(5,16,WHITE); s.set(6,16,ix(Bl,H))
    return outline(s)
def lantern(k):
    s=S(16,24)
    paint(s,m_rect(7,6,8,23),St,tex='hatch'); paint(s,m_rect(4,2,11,3),St)
    paint(s,m_rect(5,4,10,9),GOLD if False else E,tone=H,bevel=False)
    for y in range(4,10):
        for x in range(5,11): s.set(x,y,ix(E,H if (x+y+k)%3 else L))
    s.set(7,6,WHITE); s.set(8,6+k,GOLD)
    paint(s,m_rect(5,10,10,10),St); paint(s,m_poly([(4,2),(8,-1),(11,2)]),St) if False else None
    paint(s,m_rect(5,1,10,2),St)
    paint(s,m_rect(5,22,10,23),St)
    return outline(s)
def lavoir(k):
    s=S(32,16)
    paint(s,m_rect(0,3,31,15),St,tex='noise'); 
    paint(s,m_rect(2,5,29,12),Bl,tex='dither')
    for i,(x,y) in enumerate(((5,7),(14,9),(22,6),(26,10))): 
        s.set(x+(k*2)%3,y,ix(Bl,H)); s.set(x+1+(k*2)%3,y,ix(Bl,L))
    paint(s,m_rect(0,3,31,4),St,tone=L,bevel=False)
    # linge
    for x in (6,18): paint(s,m_rect(x,5,x+3,6),Pl,tex='dither')
    return outline(s)
def market():
    s=S(32,28)
    for x in (2,28): paint(s,m_rect(x,8,x+1,27),Wd,tex='hatch')
    for x in range(0,32):
        r=Tc if (x//4)%2==0 else Pl
        for y in range(0,9):
            t=L if y==0 else (S_ if y>=8 else B)
            yy=y+(1 if (x%4 in (1,2)) and y==8 else 0)
            s.set(x,yy,ix(r,t))
    paint(s,m_rect(1,17,30,21),Wd,tex='hatch')
    for (x,c,t) in ((4,Tc,H),(8,G,L),(12,E,H),(16,Tc,B),(20,G,H),(24,E,L)):
        paint(s,m_ell(x,13,x+3,17),c); s.set(x+1,13,ix(c,H))
    paint(s,m_rect(2,22,29,27),Wd,tex='rows'); 
    return outline(s)
if __name__=='__main__':
    pass
