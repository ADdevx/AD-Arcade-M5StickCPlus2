import random, math
from PIL import Image, ImageDraw
# ---------------- palette : 9 rampes x 5 tons + 3 speciaux = 48 couleurs ----------------
RAMPS = {
 'grass':      ['1f3b22','2f6b2c','4f9a38','7cc04a','b2e06a'],
 'foliage':    ['143027','1f5a3c','2f7d4a','4fa35a','8cc873'],
 'earth':      ['4a2a1a','8a5a32','b9824a','dcab6e','f0cf94'],
 'wood':       ['33190f','5e3519','8a5226','b4783a','d9a35f'],
 'plaster':    ['5c4a3e','b49a82','d9c3a5','efdfc4','fff4dc'],
 'terracotta': ['4a1420','8c2a2e','c04535','e0694a','f59a6e'],
 'blue':       ['142a52','2a4f8a','3f7fc4','6fb0e6','b4e0f8'],
 'stone':      ['2c2c3a','5a5e72','8588a0','aeb2c4','d4d8e4'],
 'skin':       ['5a2a24','c98a6a','e8ae88','f6caa4','fde4c8'],
}
NAMES=list(RAMPS)
G,F,E,Wd,Pl,Tc,Bl,St,Sk=range(9)
O,S_,B,L,H=range(5)
WHITE,BLACK,GOLD=45,46,47
def hex2rgb(h): return tuple(int(h[i:i+2],16) for i in (0,2,4))
def q565(c):
    r,g,b=c; r5,g6,b5=r>>3,g>>2,b>>3
    return ((r5<<3)|(r5>>2),(g6<<2)|(g6>>4),(b5<<3)|(b5>>2))
PAL=[]
for n in NAMES: PAL+= [q565(hex2rgb(h)) for h in RAMPS[n]]
PAL+=[q565(hex2rgb('fff8e8')),q565(hex2rgb('14101f')),q565(hex2rgb('f2b83a'))]
assert len(PAL)==48
def ix(r,t): return r*5+t
def outline_of(i): return i//5*5 if i<45 else BLACK
def tone_of(i): return i%5 if i<45 else 4
def ramp_of(i): return i//5 if i<45 else -1
def rgb565(i): r,g,b=PAL[i]; return ((r>>3)<<11)|((g>>2)<<5)|(b>>3)
# ---------------- sprite ----------------
class S:
    def __init__(s,w,h): s.w,s.h=w,h; s.p=[[None]*w for _ in range(h)]
    def set(s,x,y,v):
        if 0<=x<s.w and 0<=y<s.h: s.p[y][x]=v
    def get(s,x,y): return s.p[y][x] if 0<=x<s.w and 0<=y<s.h else None
    def copy(s):
        n=S(s.w,s.h); n.p=[r[:] for r in s.p]; return n
    def paste(s,o,ox,oy):
        for y in range(o.h):
            for x in range(o.w):
                v=o.p[y][x]
                if v is not None: s.set(x+ox,y+oy,v)
    def mirror(s):
        n=S(s.w,s.h)
        for y in range(s.h):
            for x in range(s.w): n.p[y][x]=s.p[y][s.w-1-x]
        return n
    def image(s,pal=None,bg=None):
        pal=pal or PAL
        im=Image.new('RGBA',(s.w,s.h),(0,0,0,0))
        for y in range(s.h):
            for x in range(s.w):
                v=s.p[y][x]
                if v is not None: im.putpixel((x,y),tuple(pal[v])+(255,))
        return im
def m_rect(x0,y0,x1,y1): return {(x,y) for y in range(y0,y1+1) for x in range(x0,x1+1)}
def _rast(draw,w=64,h=64,ox=0,oy=0):
    im=Image.new('L',(w,h),0); d=ImageDraw.Draw(im); draw(d); 
    return {(x+ox,y+oy) for y in range(h) for x in range(w) if im.getpixel((x,y))}
def m_ell(x0,y0,x1,y1):
    ox,oy=min(x0,0),min(y0,0)
    return _rast(lambda d:d.ellipse([x0-ox,y0-oy,x1-ox,y1-oy],fill=255),max(x1-ox+2,4),max(y1-oy+2,4),ox,oy)
def m_poly(pts):
    mx=max(p[0] for p in pts)+2; my=max(p[1] for p in pts)+2
    return _rast(lambda d:d.polygon(pts,fill=255),mx,my)
def m_line(x0,y0,x1,y1,wd=1):
    mx=int(max(x0,x1))+3; my=int(max(y0,y1))+3
    return _rast(lambda d:d.line([x0,y0,x1,y1],fill=255,width=wd),max(mx,4),max(my,4))
def hsh(x,y,sd=0): return ((x*73856093)^(y*19349663)^(sd*83492791))&0xffff
def paint(s,mask,r,bevel=True,tex=None,sd=0,tone=B):
    if not mask: return
    ys=[y for _,y in mask]; y0,y1=min(ys),max(ys); hh=max(1,y1-y0)
    for (x,y) in mask:
        t=tone
        if bevel:
            up=(x,y-1) in mask; lf=(x-1,y) in mask; dn=(x,y+1) in mask; rt=(x+1,y) in mask
            tl=(not up) or (not lf); br=(not dn) or (not rt)
            if tl and not br: t=L
            if br and not tl: t=S_
            if (not up) and (not lf) and dn and rt: t=H
        if tex and t==tone:
            k=(y-y0)/hh; h=hsh(x,y,sd)
            if tex=='dither':
                if (x+y)%2==0 and k>0.62: t=S_
                elif (x+y)%2==0 and k<0.25: t=L
            elif tex=='noise':
                if h%11==0: t=S_
                elif h%13==0: t=L
            elif tex=='grass':
                if h%7==0: t=S_
                elif h%9==0: t=L
                elif h%29==0: t=H
            elif tex=='hatch':
                if (x+(y//2))%4==0: t=S_
                elif (x+(y//2))%4==2 and k<0.5: t=L
            elif tex=='rows':
                if y%3==2: t=S_
                elif y%3==0: t=L
        s.set(x,y,ix(r,t) if r<9 else r)
def px(s,x,y,v): s.set(x,y,v)
def outline(s,skip=()):
    adds=[]
    for y in range(s.h):
        for x in range(s.w):
            if s.p[y][x] is not None: continue
            for dx,dy in ((0,1),(1,0),(0,-1),(-1,0)):
                v=s.get(x+dx,y+dy)
                if v is not None:
                    adds.append((x,y,outline_of(v))); break
    for x,y,v in adds: s.set(x,y,v)
    return s
def flash(s,tone=H):
    n=S(s.w,s.h)
    for y in range(s.h):
        for x in range(s.w):
            v=s.p[y][x]
            if v is None: continue
            n.p[y][x]=WHITE if tone_of(v)>0 and v<45 and tone_of(v)>=2 else (ix(ramp_of(v),L) if v<45 and tone_of(v)>0 else v)
    return n
def tint(pal,mul,mix=0.0,mixc=(0,0,0)):
    out=[]
    for r,g,b in pal:
        c=(r*mul[0],g*mul[1],b*mul[2]); c=tuple(int(c[i]*(1-mix)+mixc[i]*mix) for i in range(3)); out.append(tuple(max(0,min(255,v)) for v in c))
    return out
# ---------------- export + taille ----------------
def rle(s):
    out=0; flat=[(v if v is not None else 255) for row in s.p for v in row]
    i=0
    while i<len(flat):
        j=i
        while j<len(flat) and flat[j]==flat[i] and j-i<255: j+=1
        out+=2; i=j
    return out
def packed(s):
    cols={v for row in s.p for v in row if v is not None}
    if len(cols)<=15: return (s.w*s.h+1)//2+16     # 4 bits + palette locale 15 couleurs
    return (s.w*s.h*6+7)//8                      # 6 bits
def best_size(s): return min(rle(s),packed(s))
