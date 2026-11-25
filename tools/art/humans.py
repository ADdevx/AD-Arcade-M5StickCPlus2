from engine import *
def clipmask(m,x0,y0,x1,y1): return {(x,y) for (x,y) in m if x0<=x<=x1 and y0<=y<=y1}
HERO=dict(skin=Sk,hair=Wd,top=Bl,pants=E,boots=Wd,cape=Tc,belt=True,hairstyle='short',scarf=Tc)
def human(d,f,o):
    s=S(16,24); b=[0,-1,0,-1][f]; sw=[1,0,-1,0][f]
    yo=o.get('yo',0); th=o.get('th',7); lh=o.get('lh',5); wd=o.get('wd',0)
    hy=1+yo+b; tt=11+yo+b; te=10+yo+th; lt=te+1
    sk=o['skin']; hair=o['hair']; top=o['top']; hs=o.get('hairstyle','short')
    flip=False
    if d=='left': d='right'; flip=True
    def legs():
        if d=='right':
            sd=[2,0,-2,0][f]
            for (lx,dy,fr) in ((5-sd//1,0,False),(7+sd,0,True)):
                x0=max(4,min(10,lx)); 
                m=m_rect(x0,lt+(0 if fr else 0),x0+2,lt+lh-1-(1 if (sd>0)!=fr and sd!=0 else 0))
                paint(s,{p for p in m if p[1]<lt+lh-2},o['pants'])
                paint(s,{p for p in m if p[1]>=lt+lh-2},o['boots'])
            return
        for (x0,dy) in ((5,sw),(8,-sw)):
            m=m_rect(x0,lt+dy,x0+2,lt+dy+lh-1)
            paint(s,{p for p in m if p[1]<lt+dy+lh-2},o['pants'])
            paint(s,{p for p in m if p[1]>=lt+dy+lh-2},o['boots'])
    def headmask(x0=3,x1=12): return m_ell(x0,hy,x1,hy+9)
    cape=o.get('cape')
    def cape_m(x0,x1,top_y,rows):
        m=set()
        for x in range(x0,x1+1):
            hem=top_y+rows+[0,1,1,0][(x+f)%4]-(1 if (x==x0 or x==x1) else 0)
            for y in range(top_y,hem+1): m.add((x,y))
        return m
    # ---------- DOWN ----------
    if d=='down':
        if cape: paint(s,cape_m(3-wd,12+wd,tt,th+1),cape,tex='dither')
        legs()
        paint(s,m_rect(5-wd,tt,10+wd,te),top,tex=o.get('toptex'))
        if o.get('apron'): 
            paint(s,m_rect(6,tt+2,9,te+2),o['apron'],tex='hatch'); 
        if o.get('belt'): 
            paint(s,m_rect(5-wd,te-1,10+wd,te-1),Wd); px(s,7,te-1,GOLD); px(s,8,te-1,GOLD)
        if o.get('vest'): paint(s,m_rect(5-wd,tt,6,te-1),o['vest']); paint(s,m_rect(9+wd,tt,10+wd,te-1),o['vest'])
        for (ax,ay) in ((3-wd,sw),(11+wd,-sw)):
            arm=m_rect(ax,tt+1+ay,ax+1,tt+4+ay)
            if o.get('bare'): paint(s,arm,sk)
            else: paint(s,arm,top)
            paint(s,m_rect(ax,tt+5+ay,ax+1,tt+5+ay),sk)
        if o.get('scarf') : paint(s,m_rect(5,tt-1,10,tt),o['scarf']); 
        # head
        paint(s,headmask(),sk)
        px(s,2,hy+5,ix(sk,B)); px(s,13,hy+5,ix(sk,B))
        hairmask(s,'down',hy,hs,hair,f,o)
        # face
        ey=hy+5
        px(s,5,ey,BLACK); px(s,5,ey+1,BLACK); px(s,10,ey,BLACK); px(s,10,ey+1,BLACK)
        px(s,5,ey,ix(Bl,S_) if o.get('eyecol') else BLACK)
        px(s,4,ey+2,ix(Tc,L)); px(s,11,ey+2,ix(Tc,L))
        px(s,7,hy+8,ix(sk,S_)); px(s,8,hy+8,ix(sk,S_))
        if o.get('beard'): 
            paint(s,{p for p in m_ell(4,hy+5,11,hy+11) if p[1]>=hy+6 and not (p[1]<=hy+7 and 6<=p[0]<=9)},o['beard'],tex='dither')
            px(s,7,hy+8,ix(o['beard'],L)); 
        if o.get('stache'): paint(s,m_rect(5,hy+7,10,hy+7),o['stache'])
        prop(s,'down',o,f,sw,tt)
    # ---------- UP ----------
    elif d=='up':
        legs()
        if o.get('pack'): paint(s,m_rect(3,tt,12,te+1),o['pack'],tex='hatch')
        paint(s,m_rect(5-wd,tt,10+wd,te),top)
        if cape: paint(s,cape_m(4-wd,11+wd,tt-1,th+2),cape,tex='dither')
        for (ax,ay) in ((3-wd,-sw),(11+wd,sw)):
            paint(s,m_rect(ax,tt+1+ay,ax+1,tt+4+ay),top if not o.get('bare') else sk)
            paint(s,m_rect(ax,tt+5+ay,ax+1,tt+5+ay),sk)
        if o.get('scarf'): paint(s,m_rect(5,tt-1,10,tt),o['scarf'])
        paint(s,headmask(),hair if hs!='bald' else sk,tex='dither')
        if hs=='bun': paint(s,m_ell(6,hy-3,9,hy),hair)
        hairmask(s,'up',hy,hs,hair,f,o)
        prop(s,'up',o,f,sw,tt)
    # ---------- RIGHT ----------
    else:
        sd=[2,0,-2,0][f]
        if o.get('pack'): paint(s,m_rect(3,tt+1,6,te+1),o['pack'],tex='hatch')
        if cape:
            m=set()
            for y in range(tt,te+3):
                k=(y-tt)/(th+2); xx=int(5-2*k-sd*0.5*k)
                for x in range(xx-1,7): m.add((x,y))
            paint(s,m,cape,tex='dither')
        legs()
        paint(s,m_rect(5,tt,10,te),top)
        if o.get('apron'): paint(s,m_rect(9,tt+2,11,te+2),o['apron'],tex='hatch')
        if o.get('belt'): paint(s,m_rect(5,te-1,10,te-1),Wd)
        px(s,8,te-1,GOLD) if o.get('belt') else None
        ax=7+sd//2
        paint(s,m_rect(ax,tt+1,ax+2,tt+4),top if not o.get('bare') else sk); paint(s,m_rect(ax,tt+5,ax+2,tt+5),sk)
        if o.get('scarf'): paint(s,m_rect(5,tt-1,10,tt),o['scarf'])
        paint(s,m_ell(4,hy,12,hy+9),sk); px(s,13,hy+6,ix(sk,L)); px(s,13,hy+7,ix(sk,B))
        hairmask(s,'right',hy,hs,hair,f,o)
        px(s,10,hy+5,BLACK); px(s,10,hy+6,BLACK); px(s,11,hy+8,ix(Tc,L)) if False else None
        px(s,9,hy+7,ix(Tc,L))
        if o.get('beard'): paint(s,{p for p in m_ell(7,hy+5,13,hy+11) if p[1]>=hy+7},o['beard'],tex='dither')
        prop(s,'right',o,f,sd,tt)
    outline(s)
    return s.mirror() if flip else s
def hairmask(s,d,hy,hs,hair,f,o):
    if hs=='bald': return
    sway=[0,1,0,-1][f]
    if d=='down':
        if hs in('short','bun','cap','curly'):
            cap=clipmask(m_ell(3,hy,12,hy+9),3,hy,12,hy+3)|m_rect(3,hy+4,4,hy+6)|m_rect(11,hy+4,12,hy+6)|m_rect(5,hy+4,6,hy+4)|m_rect(9,hy+4,10,hy+4)|{(7,hy+4),(8,hy+4)}
            cap-={(7,hy+4)}
            paint(s,cap,hair,tex='dither')
            if hs=='short': px(s,12+(1 if f%2 else 0),hy+1,ix(hair,L)); px(s,12,hy,ix(hair,L))
            if hs=='bun': paint(s,m_ell(6,hy-3,9,hy),hair)
            if hs=='cap':
                paint(s,m_rect(3,hy,12,hy+3),o['capcol'],tex='dither'); paint(s,m_rect(4,hy+4,11,hy+4),o['capcol'])
        if hs=='hat':
            paint(s,m_rect(4,hy-3,11,hy),o['hatcol'],tex='dither')
            paint(s,m_ell(0,hy-1,15,hy+4),o['hatcol'],tex='dither'); 
            px(s,12,hy-2,ix(Tc,L)); px(s,13,hy-3,ix(Tc,H)); px(s,13,hy-4,ix(Tc,L)) if hy-4>=0 else None
        if hs=='helm':
            paint(s,clipmask(m_ell(2,hy-1,13,hy+9),2,hy-1,13,hy+4),St,tex='dither')
            paint(s,m_rect(7,hy+4,8,hy+7),St)  # nasal
            paint(s,m_rect(7,hy-3,8,hy-1),Tc); px(s,6,hy-2+sway,ix(Tc,L)) if False else None
    elif d=='up':
        if hs=='hat':
            paint(s,m_rect(4,hy-3,11,hy),o['hatcol'],tex='dither'); paint(s,m_ell(0,hy-1,15,hy+4),o['hatcol'],tex='dither')
        if hs=='helm':
            paint(s,clipmask(m_ell(2,hy-1,13,hy+9),2,hy-1,13,hy+9),St,tex='dither'); paint(s,m_rect(7,hy-3,8,hy-1),Tc)
        if hs=='cap': paint(s,m_rect(3,hy,12,hy+4),o['capcol'],tex='dither')
        if hs in('short','cap'): px(s,12+sway,hy+8,ix(hair,L)) if hs=='short' else None
    else:
        if hs in('short','bun','cap','curly'):
            cap=clipmask(m_ell(4,hy,12,hy+9),4,hy,12,hy+3)|m_rect(4,hy+4,6,hy+8)|{(7,hy+4),(8,hy+4)}
            paint(s,cap,hair,tex='dither')
            if hs=='short':
                for k in range(3): px(s,3-k,hy+5+k+(sway>0),ix(hair,[B,S_,S_][k]))
                px(s,3,hy+4,ix(hair,B))
            if hs=='bun': paint(s,m_ell(3,hy-3,7,hy),hair)
            if hs=='cap':
                paint(s,m_rect(4,hy,12,hy+3),o['capcol'],tex='dither'); paint(s,m_rect(11,hy+3,14,hy+4),o['capcol'])
        if hs=='hat':
            paint(s,m_rect(5,hy-3,11,hy),o['hatcol'],tex='dither'); paint(s,m_ell(1,hy-1,15,hy+4),o['hatcol'],tex='dither'); px(s,3,hy-2,ix(Tc,L)); px(s,2,hy-3,ix(Tc,H))
        if hs=='helm':
            paint(s,clipmask(m_ell(3,hy-1,13,hy+9),3,hy-1,13,hy+5),St,tex='dither'); paint(s,m_rect(7,hy-3,8,hy-1),Tc); px(s,6,hy-2,ix(Tc,L))
def prop(s,d,o,f,sw,tt):
    p=o.get('prop')
    if not p: return
    if p=='hammer' and d in('down','right'):
        x=13 if d=='down' else 11; 
        paint(s,m_rect(x,tt+3+sw,x,tt+9+sw),Wd); paint(s,m_rect(x-1,tt+0+sw,x+1,tt+3+sw),St)
    if p=='cane':
        x=13 if d!='up' else 2
        paint(s,m_rect(x,tt+4,x,tt+12),Wd); px(s,x-1,tt+4,ix(Wd,L))
    if p=='spear':
        x=14 if d!='right' else 12
        paint(s,m_rect(x,2,x,22),Wd); paint(s,m_poly([(x-1,3),(x,-1),(x+1,3)]),St)
