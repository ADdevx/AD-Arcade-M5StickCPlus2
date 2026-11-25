from humans import *
from hero_sheet import sheet
def vec(a): r=math.radians(a); return (math.sin(r),math.cos(r))
def attack(d,k):
    """32x32, heros en (8,6). k=0 armer, 1 coup (arc), 2 fin"""
    base='right' if d=='left' else d
    s=S(32,32); hs=human(base,1,HERO)
    s.paste(hs,8,6)
    cfg={'down':((19,22),[165,105,30],1),'up':((12,17),[-165,-110,-40],1),'right':((20,18),[150,95,40],1)}
    (hx,hy),angs,_=cfg[base]; a=angs[k]
    vx,vy=vec(a)
    # bras (epaule -> main)
    sh={'down':(20,18),'up':(19,18),'right':(17,18)}[base]
    paint(s,m_line(sh[0],sh[1],hx,hy,2),Bl)
    px(s,hx,hy,ix(Sk,B)); px(s,hx+1,hy,ix(Sk,L))
    # garde + lame
    gx,gy=hx+vx*2,hy+vy*2
    px_=-vy; py_=vx
    for t in (-2,-1,0,1,2): s.set(int(round(gx+px_*t)),int(round(gy+py_*t)),GOLD if abs(t)<2 else ix(Wd,L))
    blade=m_line(gx+vx*1.5,gy+vy*1.5,hx+vx*14,hy+vy*14,2)
    paint(s,blade,St,bevel=False,tone=L)
    for t in range(3,14):
        s.set(int(round(hx+vx*t)),int(round(hy+vy*t)),WHITE if t%3 else ix(St,H))
    s.set(int(round(hx+vx*14)),int(round(hy+vy*14)),WHITE)
    # arc de coup (trajet entre l'angle precedent et courant)
    if k>=1:
        a0=angs[k-1]; n=14
        for i in range(n+1):
            aa=a0+(a-a0)*i/n; ax_,ay_=vec(aa)
            for rr,col in ((13,WHITE if i>n*0.6 else ix(Bl,H)),(11.5,ix(Bl,L) if i>n*0.3 else ix(Bl,B))):
                x,y=int(round(hx+ax_*rr)),int(round(hy+ay_*rr))
                if k==2 and i<n*0.35: continue
                if s.get(x,y) is None: s.set(x,y,col)
    outline(s)
    return s.mirror() if d=='left' else s
def hurt():
    s=human('down',1,HERO)
    # yeux fermes > <
    h=S(16,24); 
    n=s.copy()
    for (x,y) in ((4,6),(6,6),(5,7),(4,8),(6,8)): pass
    f=flash(n)
    return f
def hurt2():
    s=human('down',1,HERO); 
    # yeux X : remplace pixels noirs 
    for y in range(24):
        for x in range(16):
            if s.p[y][x]==BLACK: s.p[y][x]=ix(Sk,S_)
    for (x,y) in ((4,6),(6,6),(5,7),(4,8),(6,8),(9,6),(11,6),(10,7),(9,8),(11,8)): s.set(x,y+0,BLACK) if False else None
    for (x,y) in ((4,6),(6,6),(5,7),(4,8),(6,8)): s.set(x,y,BLACK)
    for (x,y) in ((9,6),(11,6),(10,7),(9,8),(11,8)): s.set(x,y,BLACK)
    return s
def roll(k):
    s=S(16,24); cx,cy=8,16
    paint(s,m_ell(2,9,13,20),Bl)
    paint(s,m_ell(3,10,8,15),Sk) if k==0 else paint(s,m_ell(8,14,13,19),Sk)
    paint(s,m_poly([(2,12),(6,9),(10,9),(13,13)]) if k==0 else m_poly([(2,16),(5,20),(9,20),(3,13)]),Wd)
    paint(s,m_poly([(10,10),(15,12),(14,17),(12,15)]) if k==0 else m_poly([(0,10),(4,9),(5,14),(1,15)]),Tc,tex='dither')
    paint(s,m_rect(6,18,10,20),Wd) if k==0 else paint(s,m_rect(5,10,9,12),E)
    outline(s); return s
def victory(k):
    s=S(16,28); h=human('down',1,HERO)
    # bras leves : redessine par dessus (efface bras bas)
    s.paste(h,0,4)
    for y in range(12,22):
        for x in (3,4,11,12):
            if s.p[y][x] is not None and ramp_of(s.p[y][x]) in (Bl,): s.p[y][x]=None
    for (x,y) in ((3,15),(4,15),(11,15),(12,15)): pass
    for side in (0,1):
        x=2 if side==0 else 12
        paint(s,m_rect(x,8,x+1,15),Bl); paint(s,m_rect(x,6,x+1,7),Sk)
    # gemme
    gem=[(7,0),(8,0)],
    paint(s,m_poly([(8,0),(11,3),(8,6),(5,3)]),Bl)
    s.set(7,2,WHITE); 
    if k: s.set(3,1,WHITE); s.set(12,2,WHITE); s.set(8,-1,WHITE)
    else: s.set(12,0,WHITE); s.set(3,3,WHITE)
    outline(s); return s
def hero_all():
    rows=[]
    for d in('down','up','right','left'): rows.append([human(d,f,HERO) for f in range(4)])
    att=[[attack(d,k) for k in range(3)] for d in('down','up','right','left')]
    return rows,att
if __name__=='__main__':
    rows,att=hero_all()
    r1=[x for r in att for x in r]
    r2=[hurt(),hurt2(),roll(0),roll(1),victory(0),victory(1)]
    sheet([r1[:6],r1[6:],r2],cw=38,ch=38).convert('RGB').save('/tmp/zel2/t_att.png')
