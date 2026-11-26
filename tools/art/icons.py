# Icones 64x64 du menu, style Emberwood (palette 48 couleurs, biseau haut-gauche, contours colores)
from td_worlds import *
from crypt import chest
from scene import heart_s

def bg_grad(s,ramp,top,bot,dither=False):
    for y in range(64):
        v=top+(bot-top)*y/63
        fr=v-int(v)
        for x in range(64):
            t=int(v)+(1 if (fr>0.5 and (fr-0.5)*16>BAYER[y%4][x%4]*0.5 and abs(fr-0.5)<0.25) else (1 if fr>0.75 else 0))
            s.set(x,y,ix(ramp,max(0,min(4,t))))
def stars_bg(s,n=18,sd=1):
    rng=random.Random(sd)
    for _ in range(n):
        x,y=rng.randrange(64),rng.randrange(40); s.set(x,y,WHITE if rng.random()<0.3 else ix(Bl,H))
def frame(s):
    """liseré interieur (reste lisible dans le cadre du menu)"""
    for i in range(64):
        for (x,y) in ((i,0),(0,i),(i,63),(63,i)): s.set(x,y,ix(Wd,O))
    return s
def paste_c(s,sp,cx,by):
    s.paste(sp,cx-sp.w//2,by-sp.h)

# ------------------------------------------------------------------ jeux
def ic_meteors():
    s=S(64,64); bg_grad(s,Bl,0.6,1.8); stars_bg(s,22,3)
    for (cx,cy,r,k) in ((40,20,9,0),(18,34,6,1)):
        for i in range(14):                                   # trainee de feu
            x=int(cx+i*1.6); y=int(cy-i*1.1); rr=max(1,int(r*(1-i/14)*0.9))
            for p in m_ell(x-rr,y-rr,x+rr,y+rr):
                if s.get(*p) is not None and ramp_of(s.get(*p))==Tc: continue
                s.set(*p,[WHITE,GOLD,ix(E,H),ix(Tc,H),ix(Tc,B),ix(Tc,S_)][min(5,i//2)])
        m=m_ell(cx-r,cy-r,cx+r,cy+r); sphere(s,m,St,-0.1,tex=0.8)
        for (dx,dy) in ((-2,-2),(3,1),(-1,4)):
            for p in m_ell(cx+dx-1,cy+dy-1,cx+dx+1,cy+dy+1): s.set(*p,ix(St,S_))
        s.set(cx-r//2,cy-r//2,ix(St,H))
    ship=S(16,16)
    paint(ship,m_poly([(8,0),(12,10),(15,14),(1,14),(4,10)]),St); paint(ship,m_ell(6,4,9,9),Bl,tone=L)
    ship.set(7,5,WHITE); ship=outline(ship)
    for y in range(15,19): ship.set(6,y,GOLD) if y<17 else None
    s.paste(ship,26,46)
    for y in range(61,64): s.set(33,y,ix(Tc,H))
    return frame(s)
def ic_maze():
    s=S(64,64)
    for y in range(64):
        for x in range(64): s.set(x,y,ix(G,dt(2.2+0.4*fnoise(x,y,5),x,y,1,3)))
    walls=[(0,0,63,5),(0,58,63,63),(0,0,5,63),(58,0,63,63),(14,14,49,19),(14,14,19,40),(30,30,35,58),(44,26,49,46),(14,44,26,49)]
    for (x0,y0,x1,y1) in walls:
        m=m_rect(x0,y0,x1,y1)
        for (x,y) in m:
            t=B
            if y==y0: t=H
            elif y==y0+1: t=L
            elif y==y1: t=O
            elif (x+(y//3)*2)%6==0: t=S_
            s.set(x,y,ix(St,t))
        for x in range(x0,x1+1):
            if y1+1<64: s.set(x,y1+1,ix(G,O))
    for p in m_ell(48,48,56,56):
        d=math.hypot(p[0]-52,p[1]-52); s.set(*p,ix(G,H) if d<2 else (ix(G,L) if (p[0]+p[1])%2 else WHITE))
    ball=m_ell(22,24,29,31); sphere(ball and s,ball,St,0.6)
    s.set(23,25,WHITE); s.set(24,25,WHITE); s.set(23,26,WHITE)
    for p in m_ell(23,31,30,33):
        v=s.get(*p)
        if v is not None and ramp_of(v)==G: s.set(*p,ix(G,O))
    return frame(s)
def ic_breakout():
    s=S(64,64); bg_grad(s,Bl,0.6,1.4)
    cols=[Tc,E,G,Bl]
    for r,c in enumerate(cols):
        for i in range(5):
            x0=3+i*12-(6 if r%2 else 0); y0=6+r*7
            m=m_rect(max(1,x0),y0,min(62,x0+10),y0+5)
            if (r,i) in ((1,2),(2,3)): continue
            for (x,y) in m:
                t=B
                if y==y0 or x==max(1,x0): t=L
                if y==y0 and x==max(1,x0): t=H
                if y==y0+5 or x==min(62,x0+10): t=S_
                s.set(x,y,ix(c,t))
    # eclats de la brique cassee
    for (x,y,c) in ((26,16,ix(E,H)),(30,19,GOLD),(36,24,ix(G,L)),(41,22,WHITE)): s.set(x,y,c); s.set(x+1,y,c)
    m=m_ell(29,36,35,42); sphere(s,m,Pl,0.6,lo=2); s.set(30,37,WHITE)
    for i in range(8): s.set(32-i,43+i,ix(Bl,H) if i%2 else ix(Bl,L))
    pad=m_rect(16,54,47,58)|m_ell(12,54,20,58)|m_ell(43,54,51,58)
    sphere(s,pad,St,0.4)
    for x in range(20,44): s.set(x,54,ix(St,H))
    for x in (24,31,38): s.set(x,56,GOLD)
    return frame(outline_keep(s))
def outline_keep(s): return s
def ic_invaders():
    s=S(64,64); bg_grad(s,Bl,0.4,1.6); stars_bg(s,14,7)
    AL=["..O.....O..","...O...O...","..OOOOOOO..",".OO.OOO.OO.","OOOOOOOOOOO","O.OOOOOOO.O","O.O.....O.O","...OO.OO..."]
    for k,(ox,oy,r) in enumerate(((4,8,G),(26,6,Tc),(48,8,G))):
        for j,row in enumerate(AL):
            for i,ch in enumerate(row):
                if ch=='O':
                    t=L if j<3 else (B if j<6 else S_)
                    if i<3 and j<5: t=H if j<2 else L
                    s.set(ox+i,oy+j+((k%2)*2),ix(r,t))
        s.set(ox+3,oy+3+((k%2)*2),BLACK); s.set(ox+7,oy+3+((k%2)*2),BLACK)
    for y in range(26,48,2): s.set(32,y,ix(G,H) if y%4 else WHITE)          # laser
    ship=S(20,12)
    paint(ship,m_rect(1,6,18,11),G); paint(ship,m_rect(7,2,12,6),G); paint(ship,m_rect(9,0,10,2),G,tone=H,bevel=False)
    ship=outline(ship); s.paste(ship,22,48)
    for x in range(4,60): s.set(x,62,ix(G,S_)) if x%3 else None
    return frame(s)
def ic_slalom():
    s=S(64,64)
    for y in range(64):
        for x in range(64):
            n=fnoise(x,y,11); s.set(x,y,WHITE if dt(3.3+n*0.8+(x-y)*0.01,x,y,2,4)>=4 else ix(Bl,H))
    for (x,y) in ((4,40),(52,6)):
        p=snowy_pine(); sm=S(15,25)
        for yy in range(0,p.h,2):
            for xx in range(0,p.w,2):
                v=p.get(xx,yy)
                if v is not None: sm.set(xx//2,yy//2,v)
        s.paste(sm,x,y)
    for (x,y,c) in ((14,14,Tc),(40,30,Bl),(20,50,Tc)):
        for j in range(10): s.set(x,y+j,ix(St,B))
        for j in range(4):
            for i in range(5): s.set(x+1+i,y+j,ix(c,L if j==0 else B))
    for i in range(30): s.set(18+i//1,22+int(i*0.9),ix(Bl,L)) if i%3 else None    # trace de ski
    sk=S(18,22)
    paint(sk,m_ell(6,0,11,5),Sk); paint(sk,m_rect(5,0,12,1),Tc)
    paint(sk,m_poly([(4,6),(13,6),(14,14),(3,14)]),Tc)
    paint(sk,m_rect(4,14,7,18),Bl); paint(sk,m_rect(10,14,13,18),Bl)
    for i in range(16): sk.set(1+i,19+i//8,ix(St,B))
    for i in range(10): sk.set(15+i//6,6+i,ix(St,L))
    sk.set(8,2,BLACK); sk=outline(sk)
    s.paste(sk,30,34)
    return frame(s)
def ic_stack():
    s=S(64,64); bg_grad(s,Bl,3.2,1.6)
    for (x,y) in ((8,10),(44,16)):
        for p in m_ell(x,y,x+12,y+5): s.set(*p,WHITE if p[1]<y+3 else ix(Bl,H))
    cols=[Tc,E,G,Bl,Tc,E]
    x=14; w=36
    for i,c in enumerate(cols):
        y0=56-i*8; off=(1 if i%2 else -1)*(i%3)
        m=m_rect(x+off,y0,x+off+w-1,y0+6)
        for (xx,yy) in m:
            t=B
            if yy==y0: t=H if xx<x+off+6 else L
            elif yy==y0+6: t=S_
            elif xx==x+off+w-1: t=S_
            s.set(xx,yy,ix(c,t))
        for xx in range(x+off+2,x+off+w-2,6): s.set(xx,y0+3,ix(c,S_))
    m=m_rect(20,4,49,10)                                          # bloc qui tombe
    for (xx,yy) in m: s.set(xx,yy,ix(G,H if yy==4 else (S_ if yy==10 else L)))
    for xx in (18,52):
        for yy in range(5,10,2): s.set(xx,yy,WHITE)
    return frame(s)
def ic_racing():
    s=S(64,64)
    for y in range(64):
        for x in range(64):
            if y<20: s.set(x,y,ix(Bl,dt(3.5-y/20,x,y,2,4)))
            else:
                k=(y-20)/44; half=6+k*30
                if abs(x-32)<half:
                    t=dt(1.6+k*0.6,x,y,1,2); s.set(x,y,ix(St,t))
                    if abs(x-32)<1+k*1.5 and ((y-20)//4)%2==0: s.set(x,y,WHITE)
                    if abs(abs(x-32)-half)<1.5+k: s.set(x,y,ix(Tc,B) if ((y-20)//3)%2 else WHITE)
                else: s.set(x,y,ix(G,dt(2.0+((y//3)%2)*0.6,x,y,1,3)))
    for (x,h) in ((6,8),(14,5),(50,7),(58,9)):
        for p in m_ell(x-5,20-h,x+5,20): s.set(*p,ix(F,dt(2.3-(p[0]-x)*0.15,p[0],p[1])))
    car=S(30,22)
    body=m_rect(3,8,26,18)|m_ell(1,10,28,20)
    sphere(car,body,Tc,0.3)
    paint(car,m_rect(7,2,22,9),Tc); paint(car,m_rect(9,3,20,8),Bl,tone=L)
    car.set(10,4,WHITE); car.set(11,4,WHITE)
    for x in (3,4,25,26): car.set(x,12,GOLD); car.set(x,13,GOLD)
    paint(car,m_rect(1,17,6,21),St,tone=O,bevel=False); paint(car,m_rect(23,17,28,21),St,tone=O,bevel=False)
    for x in range(8,22): car.set(x,15,ix(Tc,S_))
    car=outline(car); s.paste(car,17,40)
    for (x,y) in ((8,46),(4,52),(54,48),(58,55)):
        for i in range(5): s.set(x+(1 if x>32 else -1)*i//2,y+i,WHITE) if i%2 else None
    return frame(s)
def ic_lander():
    s=S(64,64); bg_grad(s,Bl,0.3,1.0); stars_bg(s,20,9)
    m=m_ell(44,4,58,18);
    for (x,y) in m: s.set(x,y,ix(G,dt(2.6-(x-44)*0.08,x,y)) if fnoise(x,y,3)>0.05 else ix(Bl,dt(3.2-(x-44)*0.1,x,y)))
    s.set(47,7,WHITE)
    for x in range(64):
        top=50+int(3*math.sin(x*0.25)+2*math.sin(x*0.7))
        if 22<=x<=42: top=52
        for y in range(top,64): s.set(x,y,ix(St,dt(3.0-(y-top)*0.2+0.3*fnoise(x,y,8),x,y,1,4)))
    for x in range(22,43): s.set(x,52,GOLD if x%4<2 else ix(Tc,H))
    for p in m_ell(6,56,14,60): s.set(*p,ix(St,S_))
    ld=S(22,24)
    body=m_poly([(5,4),(16,4),(19,13),(2,13)]); sphere(ld,body,Pl,0.3)
    for x in range(3,19): ld.set(x,13,GOLD); ld.set(x,14,ix(E,B))
    for p in m_ell(7,5,14,11): ld.set(*p,ix(Bl,L))
    ld.set(9,6,WHITE); ld.set(10,6,WHITE)
    for (a,b_) in (((4,15),(0,21)),((17,15),(21,21))):
        for i in range(7): ld.set(a[0]+(b_[0]-a[0])*i//6,a[1]+(b_[1]-a[1])*i//6,ix(St,L))
    ld=outline(ld)
    for j in range(7):
        w=3-j//2
        for i in range(-w,w+1): ld.set(11+i,15+j,[WHITE,GOLD,ix(E,H),ix(Tc,H)][min(3,j//2)])
    s.paste(ld,21,22)
    return frame(s)
# ------------------------------------------------------------------ menus / applis
def ic_daily():
    s=S(64,64); bg_grad(s,E,3.4,2.4)
    page=m_rect(10,12,53,57); sphere(s,page,Pl,0.5,lo=2)
    for p in m_rect(10,12,53,24): s.set(*p,ix(Tc,B if p[1]>13 else L))
    for x in range(10,54): s.set(x,24,ix(Tc,O))
    for x0 in (18,30,42):
        for y in range(8,16): s.set(x0,y,ix(St,L)); s.set(x0+1,y,ix(St,S_))
    for gy in range(3):
        for gx in range(5):
            x=14+gx*8; y=29+gy*9
            for p in m_rect(x,y,x+5,y+5): s.set(*p,ix(Pl,S_) if (gx+gy)%2 else ix(Pl,B))
    st=star_icon(True); big=S(18,18)
    for y in range(9):
        for x in range(9):
            v=st.get(x,y)
            if v is not None:
                for dy in (0,1):
                    for dx in (0,1): big.set(x*2+dx,y*2+dy,v)
    s.paste(big,32,34)
    s=outline(s)
    return frame(s)
def ic_duo():
    s=S(64,64); bg_grad(s,Bl,1.2,2.6)
    for y in range(44,64):
        for x in range(64): s.set(x,y,ix(G,dt(2.6-(y-44)*0.05,x,y)))
    a=human('right',0,HERO); b2=human('left',0,dict(HERO,top=Tc,cape=Bl,scarf=Bl,hair=E))
    def big(sp):
        o=S(sp.w*2,sp.h*2)
        for y in range(sp.h):
            for x in range(sp.w):
                v=sp.get(x,y)
                if v is not None:
                    for dy in (0,1):
                        for dx in (0,1): o.set(x*2+dx,y*2+dy,v)
        return o
    A=big(a); Bb=big(b2)
    s.paste(A,-4,16); s.paste(Bb,36,16)
    bolt=[(34,4),(28,18),(33,18),(27,34),(38,15),(32,15),(37,4)]
    m=m_poly(bolt)
    for p in m: s.set(*p,GOLD if (p[0]+p[1])%3 else WHITE)
    return frame(s)
def ic_trophies():
    s=S(64,64); bg_grad(s,Tc,1.4,2.4)
    for i in range(12):                                     # rayons de gloire
        a=math.radians(i*30)
        for d in range(10,40,2):
            x=int(32+math.cos(a)*d); y=int(28+math.sin(a)*d)
            if 0<=x<64 and 0<=y<64 and i%2==0: s.set(x,y,ix(Tc,L))
    cup=m_ell(16,8,47,32)&m_rect(16,8,47,30)
    cup|=m_rect(16,8,47,12)
    for (x,y) in cup:
        k=(x-16)/31; v=4.0-2.4*k
        if x in (21,22): s.set(x,y,WHITE if y%5 else GOLD); continue
        s.set(x,y,GOLD if v>2.9 else (ix(E,H) if v>2.3 else (ix(E,L) if v>1.9 else ix(E,B))))
    for (cx,dir_) in ((14,-1),(49,1)):
        for a in range(0,181,15):
            r=math.radians(a); x=int(cx+dir_*math.sin(r)*6); y=int(16+(1-math.cos(r))*5)
            s.set(x,y,ix(E,H)); s.set(x+dir_,y,ix(E,B))
    for p in m_rect(29,32,34,42): s.set(*p,ix(E,L) if p[0]<32 else ix(E,S_))
    base=m_rect(20,42,43,50); sphere(s,base,Wd,0.4)
    for p in m_rect(24,44,39,48): s.set(*p,GOLD if p[1]==44 else ix(E,B))
    for p in ((21,14),(20,15),(21,15),(22,15),(21,16)): s.set(*p,WHITE)
    for (mx,c) in ((8,St),(50,Tc)):
        m=m_ell(mx,48,mx+9,57); sphere(s,m,c,0.5); s.set(mx+2,50,WHITE)
        for y in range(40,48): s.set(mx+4,y,ix(Bl,B)); s.set(mx+5,y,ix(Tc,B))
    return frame(outline(s))
def ic_stats():
    s=S(64,64); bg_grad(s,Pl,3.6,3.0)
    for y in range(12,58,9):
        for x in range(8,60,2): s.set(x,y,ix(Pl,S_))
    for i,(h,c) in enumerate(((18,Bl),(30,G),(24,E),(40,Tc))):
        x0=10+i*12; y0=56-h
        for y in range(y0,57):
            for x in range(x0,x0+9):
                t=B
                if x==x0: t=L
                if y==y0: t=H
                if x==x0+8: t=S_
                s.set(x,y,ix(c,t))
    pts=[(12,40),(24,30),(36,34),(52,12)]
    for a,b_ in zip(pts,pts[1:]):
        for i in range(21):
            x=int(a[0]+(b_[0]-a[0])*i/20); y=int(a[1]+(b_[1]-a[1])*i/20)
            s.set(x,y,WHITE); s.set(x,y+1,ix(St,O))
    for p in m_poly([(52,8),(58,14),(50,16)]): s.set(*p,WHITE)
    for x in range(6,60): s.set(x,57,ix(St,O))
    return frame(s)
def ic_music():
    s=S(64,64); bg_grad(s,Bl,0.8,2.4)
    for y in (18,25,32,39,46):
        for x in range(4,60): s.set(x,y,ix(Bl,L) if x%2 else ix(Bl,B))
    heads=[(19,47),(43,41)]
    for (cx,cy) in heads:                                   # notes : tete ovale penchee + hampe
        m=set(p for p in m_ell(cx-7,cy-5,cx+6,cy+5) if ((p[0]-cx)*0.8+(p[1]-cy)*0.6)**2/36+((p[0]-cx)*0.6-(p[1]-cy)*0.8)**2/14<=1)
        for (x,y) in m: s.set(x,y,BLACK if (x-cx)+(y-cy)>-3 else ix(St,O))
        s.set(cx-3,cy-2,ix(St,B)); s.set(cx-2,cy-3,WHITE)
        for y in range(cy-32,cy+1): s.set(cx+5,y,ix(St,O)); s.set(cx+6,y,ix(St,S_))
    for k in range(5):                                      # barre de liaison epaisse
        for x in range(24,50):
            y=int(15-(x-24)*6/26)+k; s.set(x,y,ix(St,O) if k<4 else ix(St,S_))
    for x in range(24,50,3): s.set(x,int(15-(x-24)*6/26),ix(St,B))
    for (x,y) in ((54,10),(8,12),(57,30)):                  # etincelles
        for d in (-1,0,1): s.set(x+d,y,GOLD); s.set(x,y+d,GOLD)
        s.set(x,y,WHITE)
    return frame(outline(s))
def ic_skins():
    s=S(64,64); bg_grad(s,Pl,3.4,2.6)
    pal_=m_ell(4,10,58,54)-m_ell(36,38,46,48)
    sphere(s,pal_,Wd,0.3)
    for (x,y,c) in ((16,18,Tc),(30,15,E),(44,20,G),(14,32,Bl),(26,40,ix(Pl,H)),(46,32,Tc)):
        m=m_ell(x-5,y-4,x+5,y+4)
        if isinstance(c,int) and c>=45:
            for p in m: s.set(*p,c)
        elif c==ix(Pl,H): sphere(s,m,Pl,0.6,lo=2)
        else: sphere(s,m,c,0.4)
        s.set(x-2,y-2,WHITE)
    for i in range(26):                                         # pinceau
        x=34+i; y=58-i
        s.set(x,y,ix(Wd,L)); s.set(x+1,y,ix(Wd,S_))
    for p in m_poly([(30,62),(34,56),(38,60)]): s.set(*p,ix(Bl,B))
    for p in ((35,56),(36,57),(37,58)): s.set(*p,ix(St,H))
    return frame(outline(s))
def gear(s,cx,cy,r,teeth,ramp,hole=True,rot=0):
    m=set()
    for (x,y) in m_ell(cx-r,cy-r,cx+r,cy+r): m.add((x,y))
    for i in range(teeth):
        a=rot+i*2*math.pi/teeth
        for d in range(r-1,r+4):
            for w in (-2,-1,0,1,2):
                x=int(round(cx+math.cos(a)*d-math.sin(a)*w*0.8)); y=int(round(cy+math.sin(a)*d+math.cos(a)*w*0.8)); m.add((x,y))
    if hole: m-=set(m_ell(cx-r//3,cy-r//3,cx+r//3,cy+r//3))
    sphere(s,m,ramp,0.3)
    for (x,y) in m_ell(cx-r//2-1,cy-r//2-1,cx+r//2+1,cy+r//2+1):
        if (x,y) in m and math.hypot(x-cx,y-cy)>r//3+1: s.set(x,y,ix(ramp,S_) if (x-cx)+(y-cy)>0 else ix(ramp,L))
    return m
def ic_settings():
    s=S(64,64); bg_grad(s,St,1.4,2.2)
    gear(s,26,28,14,8,St)
    gear(s,46,46,8,6,E,rot=0.3)
    for p in m_ell(22,24,30,32):
        if s.get(*p)==ix(St,S_) or s.get(*p) is None: pass
    for i in range(20):                                          # cle
        x=8+i; y=58-i//2
        s.set(x,y,ix(St,H)); s.set(x,y+1,ix(St,B))
    for p in m_ell(4,54,10,60): s.set(*p,ix(St,L))
    for p in m_ell(5,55,8,58): s.set(*p,None)
    return frame(outline(s))

ICONS={2:ic_meteors,3:ic_maze,4:ic_breakout,5:ic_invaders,6:ic_slalom,7:ic_stack,8:ic_racing,14:ic_lander,
       17:ic_daily,18:ic_duo,19:ic_trophies,20:ic_stats,21:ic_music,22:ic_skins,23:ic_settings}

def quantize15(s):
    """limite a 15 couleurs (4 bits) : les couleurs rares prennent la plus proche de la meme rampe"""
    from collections import Counter
    cnt=Counter(v for row in s.p for v in row if v is not None)
    if len(cnt)<=15: return s
    keep=[c for c,_ in cnt.most_common(15)]
    def near(v):
        best=None; bd=1e9
        for k in keep:
            a=PAL[v]; b_=PAL[k]; d=sum((a[i]-b_[i])**2 for i in range(3))
            if d<bd: bd=d; best=k
        return best
    m={c:(c if c in keep else near(c)) for c in cnt}
    for y in range(s.h):
        for x in range(s.w):
            v=s.p[y][x]
            if v is not None: s.p[y][x]=m[v]
    return s
