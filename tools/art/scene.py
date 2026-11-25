import sys; import os; sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','cover'))
import mk
from sheets import *
W,Hh,HUD=240,135,23
def shade_ell(sc,cx,cy,w,h=2):
    for y in range(cy-h,cy+h+1):
        for x in range(cx-w,cx+w+1):
            if ((x-cx)/(w+0.5))**2+((y-cy)/(h+0.5))**2<=1 and 0<=x<sc.w and 0<=y<sc.h:
                v=sc.p[y][x]
                if v is not None and v<45 and v%5>=2 and (x+y)%2==0: sc.p[y][x]=v-1 if v%5>2 else v-1
                elif v is not None and v<45 and v%5>=2: sc.p[y][x]=v-1
def heart_s(state='full',k=0):
    s=S(12,11); g=k
    m=m_ell(1-g,1-g,5,5)|m_ell(5,1-g,9+g,5)|m_poly([(1-g if g==0 else 0,4),(9+g,4),(5,9+g)])
    if state=='full': paint(s,m,Tc); s.set(3,3,ix(Tc,H)); s.set(2,3,ix(Tc,L)); s.set(4,2,WHITE)
    elif state=='empty': paint(s,m,St,bevel=False,tone=S_); 
    else:
        paint(s,{p for p in m if p[0]<=5},Tc); paint(s,{p for p in m if p[0]>5},St,bevel=False,tone=S_); s.set(3,3,ix(Tc,H))
    return outline(s)
def gem_s():
    s=S(9,9); paint(s,m_poly([(4,0),(8,3),(4,8),(0,3)]),Bl); s.set(3,2,WHITE); s.set(4,2,ix(Bl,H)); s.set(2,3,ix(Bl,H)); return outline(s)
def key_s():
    s=S(11,7); paint(s,m_ell(0,1,4,5),GOLD if False else E); s.set(2,3,BLACK) ; 
    for x in range(4,11): s.set(x,3,GOLD)
    s.set(8,4,GOLD); s.set(8,5,GOLD); s.set(10,4,GOLD); s.set(1,2,WHITE); return outline(s)
def sword_icon():
    s=S(12,12)
    for i in range(8): s.set(9-i,2+i,WHITE if i%2 else ix(St,L)); s.set(10-i,2+i,ix(St,B))
    paint(s,m_rect(1,8,4,9),GOLD); s.set(3,9,ix(Wd,B)); s.set(2,10,ix(Wd,S_)); s.set(1,11,ix(Wd,S_)); s.set(3,7,GOLD)
    return outline(s)
def boot_icon():
    s=S(12,12); paint(s,m_rect(3,1,6,7),Wd); paint(s,m_rect(3,7,10,10),Wd); s.set(4,2,ix(Wd,H)); paint(s,m_rect(3,3,6,3),GOLD)
    return outline(s)
def frame_box(s,x,y,w,h,inner=Pl):
    paint(s,m_rect(x,y,x+w-1,y+h-1),Wd,tex='hatch')
    paint(s,m_rect(x+2,y+2,x+w-3,y+h-3),inner,tex='noise',bevel=True)
    for (cx,cy) in ((x+1,y+1),(x+w-2,y+1),(x+1,y+h-2),(x+w-2,y+h-2)): s.set(cx,cy,GOLD)
def hud_s(t,hearts=(3,5),gems=27,keys=1):
    s=S(W,HUD)
    paint(s,m_rect(0,0,W-1,HUD-1),Wd,tex='hatch'); 
    for x in range(W): s.set(x,HUD-1,ix(Wd,O)); s.set(x,HUD-2,GOLD) if x%2==0 else s.set(x,HUD-2,ix(E,B)); s.set(x,0,ix(Wd,L))
    for x in range(2,W,8): s.set(x,HUD-3,ix(Wd,S_))
    beat=(t//2)%6==0
    for i in range(hearts[1]):
        st='full' if i<hearts[0] else 'empty'
        s.paste(heart_s(st,1 if (beat and st=='full') else 0),5+i*12,4)
    s.paste(gem_s(),6,15)
    s.paste(key_s(),50,15)
    # slots A/B
    for i,ic in enumerate((sword_icon(),boot_icon())):
        x=W-52+i*26; frame_box(s,x,2,22,18); s.paste(ic,x+5,5); outline_none=1
    return s
def draw_text(im,txt,x,y,col=(20,16,31),sc=1): mk.text(im,txt,x,y,sc,col)
def ground():
    sc=S(W,Hh); 
    for r in range(7):
        for c in range(15):
            sc.paste(grass_t((r*3+c*5)%4),c*16,HUD+r*16)
    P=lambda r,c: r==4 or (r==5 and 6<=c<=8) or (r==3 and c==7)
    for r in range(7):
        for c in range(15):
            if r==4 and 6<=c<=8 or (r==5 and 6<=c<=8): sc.paste(cobble(),c*16,HUD+r*16); continue
            if P(r,c):
                m=0
                for i,(dr,dc) in enumerate(((-1,0),(0,1),(1,0),(0,-1))):
                    rr,cc=r+dr,c+dc
                    if (0<=cc<15 and P(rr,cc)) or cc<0 or cc>=15: m|=1<<i
                sc.paste(path_auto(m),c*16,HUD+r*16)
    for (r,c,k) in ((5,1,0),(6,12,1),(5,3,2),(6,9,0),(6,14,2),(5,13,1),(6,2,1)): sc.paste(flowers(k),c*16,HUD+r*16)
    for (r,c) in ((5,12),(5,13),(6,13)): pass
    for c in (11,12): sc.paste(garden(c%2),c*16,HUD+5*16)
    for c in range(0,5): sc.paste(fence('h'),c*16,HUD+6*16)
    for c in range(9,11): sc.paste(fence('h'),c*16,HUD+6*16)
    return sc
def compose(t=0,mode='day',dialog=None,hero_x=None):
    sc=ground(); Y=HUD
    items=[]   # (bottom y, x, y, sprite, shadow)
    def add(x,y,sp,sh=True): items.append((y+sp.h,x,y,sp,sh))
    base=62+Y
    add(4,base-36,house(Tc,Tc),False); add(40,base-36,house(Bl,Bl,beams=True),False)
    add(78,base-40,inn(),False); add(130,base-36,shop(),False)
    add(168,base-52,mill((t//4)%2),False); add(206,base-36,cabin(),False)
    for sx in (4+21,40+21,78+34+0):
        pass
    sm=lambda x,y: add(x,y,smoke((t//2)%4),False)
    sm(4+19,base-36-9); sm(40+19,base-36-9); sm(78+3,base-40-10)
    add(112,Y+72,well(),True); add(16,Y+88,lavoir((t//4)%2),False); add(150,Y+82,market(),False)
    add(48,Y+82,bench(),True); add(190,Y+90,barrel(),True); add(204,Y+92,crate(),True); add(220,Y+92,haystack(),True)
    add(84,Y+74,lantern((t//3)%2),False); add(196,Y+70,lantern((t//3+1)%2),False)
    add(92,Y+48+16,signpost(),True)
    # PNJ
    add(166,Y+60,npc('marchand','down',(t//4)%2*1),True)           # derriere l'etal
    add(30,Y+66,npc('vieille','right',(t//3)%4),True) if False else add(52,Y+66,npc('vieille','down',(t//5)%2),True)
    ex=(10+t*3)%260-10; add(ex,Y+98,npc('enfant','right',t%4),True)
    add(112+30,Y+68,npc('garde','left',0),True) if False else add(72,Y+64,npc('garde','down',0),True)
    hx=hero_x if hero_x is not None else 118+t
    add(hx,Y+72,human('right',t%4,HERO),True)
    add(10,Y+92,npc('forgeron','right',(t//2)%4),True) if False else None
    items.sort()
    for b,x,y,sp,sh in items:
        if sh: shade_ell(sc,x+sp.w//2,y+sp.h-1,sp.w//2-1,2)
        sc.paste(sp,x,y)
    sc.paste(hud_s(t,(4,5)),0,0)
    pal=PAL if mode=='day' else (tint(PAL,(1.05,0.78,0.7),0.12,(200,80,60)) if mode=='dusk' else tint(PAL,(0.45,0.55,0.95),0.18,(20,30,90)))
    im=sc.image(pal,None); bg=Image.new('RGBA',(W,Hh),tuple(pal[BLACK])+(255,)); bg.alpha_composite(im)
    d=ImageDraw.Draw(bg)
    mk.text(bg,"x27",17,17,1,(255,248,232)); mk.text(bg,"x1",63,17,1,(255,248,232))
    mk.text(bg,"A",W-47,13+9,1,(60,36,20)) if False else None
    mk.text(bg,"VILLAGE",W-96,7,1,(242,184,58)) if False else None
    if dialog: dialogbox(bg,dialog,pal,t)
    if mode in('dusk','night'): glow(bg,sc,t,mode)
    return bg
def dialogbox(bg,dlg,pal,t):
    s=S(W,Hh); x0,y0,w,h=8,Hh-36,224,32
    frame_box(s,x0,y0,w,h)
    # onglet nom
    paint(s,m_rect(x0+10,y0-7,x0+10+len(dlg[0])*6+8,y0+2),Tc,tex='dither')
    s.set(x0+10,y0-7,ix(Tc,H))
    im=s.image(pal); bg.alpha_composite(im)
    ink=(34,22,18)
    mk.text(bg,dlg[0],x0+14,y0-5,1,(255,244,220))
    for i,l in enumerate(dlg[1:]): mk.text(bg,l,x0+10,y0+6+i*10,1,ink)
    if (t//3)%2==0:
        for i in range(4): ImageDraw.Draw(bg).line([x0+w-16+i,y0+h-12+i,x0+w-8-i,y0+h-12+i],fill=tuple(pal[ix(Tc,B)]))
def glow(bg,sc,t,mode):
    # cercles de lumiere dithered autour des lanternes
    d=bg.load()
    for (lx,ly) in ((92,23+74+3),(204,23+70+3)):
        for y in range(ly-26,ly+26):
            for x in range(lx-26,lx+26):
                if 0<=x<W and 0<=y<Hh and (x+y)%2==0:
                    dd=math.hypot(x-lx,(y-ly)*1.2)
                    if dd<22+(t%2):
                        r,g,b,a=d[x,y]; d[x,y]=(min(255,r+50),min(255,g+36),min(255,b+4),a)
if __name__=='__main__':
    pass
