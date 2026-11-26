import os, sys
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','cover'))
import mk
from td import *
from scene import W, Hh, HUD, shade_ell, heart_s, frame_box
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'preview')
BG=(30,26,46,255)
def label(im,txt,x,y,sc=2,col=(251,244,200)): mk.text(im,txt,x,y,sc,col)
def rows_sheet(rows,W_=1280,sc=4):
    im=Image.new('RGBA',(W_,3000),BG); y=8
    for head,items in rows:
        label(im,head,14,y,2); y+=24; x=14; mh=0
        for name,sp in items:
            w,h=sp.w*sc,sp.h*sc
            if x+w>W_-10: x=14; y+=mh+24; mh=0
            im.alpha_composite(sp.image().resize((w,h),Image.NEAREST),(x,y))
            label(im,name,x,y+h+3,1,(180,170,200)); x+=w+14; mh=max(mh,h)
        y+=mh+30
    return im.crop((0,0,W_,y))
TOWERS=[('ARCHER',tower_archer),('CANNON',tower_cannon),('FROST',tower_frost),('STORM',tower_storm)]
def sheet_towers():
    return rows_sheet([(n+' TOWER : LEVEL 1 / 2 / 3 (+ ACTION FRAME)',[('LV%d'%l,f(l)) for l in (1,2,3)]+[('FIRE',f(3,1))]) for n,f in TOWERS]+
                      [('BUILD PAD (NORMAL / SELECTED) + BUILD MENU',[('PAD',pad()),('PAD SEL',pad(True)),('MENU',build_menu(1))])])
def sheet_enemies():
    return rows_sheet([
     ('SLIME x4 / GOBLIN RUNNER x4',[('SLIME %d'%k,slime(k)) for k in range(4)]+[('GOBLIN %d'%k,goblin(k)) for k in range(4)]),
     ('ORC KNIGHT (ARMORED) x4 / BAT (FLYING) x4',[('KNIGHT %d'%k,orc_knight(k)) for k in range(4)]+[('BAT %d'%k,bat(k)) for k in range(4)]),
     ('SHAMAN (HEALS) x2 + CAST / OGRE KING BOSS x4',[('SHAMAN %d'%k,shaman(k)) for k in range(2)]+[('CAST',shaman(0,True))]+[('OGRE %d'%k,ogre(k)) for k in range(4)]),
     ('DEATH = PARTICLE BURST + COIN',[('BURST %d'%k,burst(goblin(0),k)) for k in range(4)]+[('COIN %d'%k,coin(k)) for k in range(4)]),
    ])
def td_path(mask):
    s=grass_t(mask%4)
    inn=lambda x,y: cfield(mask,x,y,11)>=0.5
    for y in range(16):
        for x in range(16):
            f=cfield(mask,x,y,11)
            if f>=0.5:
                t=B
                if not inn(x,y-1) or not inn(x-1,y): t=S_
                elif not inn(x,y+1) or not inn(x+1,y): t=H
                else: t=dt(2.6+fnoise(x,y,77)*0.6,x,y,2,4)
                s.set(x,y,ix(E,t))
                if f>0.65 and hsh(x,y,mask)%41==0: s.set(x,y,ix(St,L))
            elif f>0.42: s.set(x,y,ix(G,S_) if (x+y)%2 else ix(G,B))
    return s
def sheet_fx():
    return rows_sheet([
     ('PROJECTILES + EXPLOSION x4 + FROST BURST x3',[('ARROW',arrow()),('BALL',cannonball()),('FROST',frostbolt())]+[('BOOM %d'%k,explosion(k)) for k in range(4)]+[('ICE %d'%k,frostburst(k)) for k in range(3)]),
     ('MAP : SPAWN PORTAL x2 / CASTLE / TREES / FLOWERS / PATH AUTO-TILING',[('PORTAL %d'%k,portal(k)) for k in range(2)]+[('CASTLE',castle()),('TREE A',tree_round(0)),('TREE B',tree_round(1))]+[('FLOWERS %d'%v,flowers_tile(v)) for v in range(2)]+[('PATH %02d'%m,td_path(m)) for m in (3,5,6,12,15)]),
    ])
# ------------------------------------------------------------ scene de jeu
PV=[[0]*16 for _ in range(8)]
def _seg(rows,cols):
    for r in rows:
        for c in cols: PV[r][c]=1
_seg((1,2),range(0,7)); _seg(range(1,7),(5,6)); _seg((5,6),range(5,12)); _seg(range(2,7),(10,11)); _seg((2,3),range(10,16))
def cm(r,c): return PV[r][c]|(PV[r][c+1]<<1)|(PV[r+1][c]<<2)|(PV[r+1][c+1]<<3)
def path_pt(t):
    """centre du chemin (coordonnees salle) pour t pixels parcourus"""
    pts=[(0,24),(88,24),(88,88),(168,88),(168,40),(240,40)]
    for a,b_ in zip(pts,pts[1:]):
        L_=abs(b_[0]-a[0])+abs(b_[1]-a[1])
        if t<=L_: k=t/L_; return (a[0]+(b_[0]-a[0])*k,a[1]+(b_[1]-a[1])*k, 1 if b_[0]>a[0] else (-1 if b_[0]<a[0] else 0))
        t-=L_
    return (240,40,1)
def ring_btn(icon,price_ok=True,sel=False):
    """bouton rond du menu circulaire (icone de tour reduite)"""
    s=S(22,22)
    m=m_ell(0,0,21,21); sphere(s,m,E if sel else Pl,0.4)
    for p in m_ell(2,2,19,19): s.set(*p,ix(Pl,H) if not sel else ix(E,H))
    small=S(icon.w//2+1,icon.h//2+1)
    for yy in range(0,icon.h,2):
        for xx in range(0,icon.w,2):
            v=icon.get(xx,yy)
            if v is not None: small.set(xx//2,yy//2,v)
    s.paste(small,11-small.w//2,19-small.h)
    s=outline(s)
    if sel:
        for p in m_ell(-1,-1,22,22):
            if s.get(*p) is None and (p[0]+p[1])%2==0: s.set(*p,GOLD)
    return s
def hbar(sc,x,y,w,frac):
    for i in range(w+2):
        sc.set(x+i,y,ix(St,O)); sc.set(x+i,y+2,ix(St,O))
    sc.set(x,y+1,ix(St,O)); sc.set(x+w+1,y+1,ix(St,O))
    for i in range(w): sc.set(x+1+i,y+1,ix(G,L) if i<w*frac else ix(Tc,B))
def compose(t=0):
    sc=S(W,Hh); Y=HUD
    for r in range(7):
        for c in range(15):
            m=cm(r,c)
            sc.paste(td_path(m) if m else (flowers_tile((r+c)%2) if (r*5+c*3)%11==0 else grass_t((r*3+c*5)%4)),c*16,Y+r*16)
    items=[]
    def add(x,y,sp,sh=True): items.append((y+sp.h,x,y,sp,sh))
    # decor
    for (x,y,v) in ((112,Y-12,0),(146,Y-10,1),(2,Y+70,1),(196,Y+84,0),(218,Y+60,1),(60,Y+48,0)): add(x,y,tree_round(v))
    add(196,Y-14,castle(t//4%2),False); add(-6,Y+1,portal(t%2),False)
    add(70,Y+98,rock_s()); add(108,Y+50,bush()); add(150,Y+98,rock_s()); add(224,Y+96,bush(False))
    # emplacements (a cote du chemin) + tours
    pads=[(34,Y+64,'archer',3),(128,Y+44,'cannon',2),(144,Y+76,'storm',2),(204,Y+76,'frost',3),(40,Y+100,None,0)]
    sel=(40,Y+100)
    for (x,y,kind,lv) in pads:
        sc.paste(pad((x,y)==sel),x-10,y-7)
        if kind:
            fn={'archer':tower_archer,'cannon':tower_cannon,'frost':tower_frost,'storm':tower_storm}[kind]
            tw=fn(lv,1 if (kind=='cannon' and t%6==0) else t%2)
            add(x-12,y-tw.h+4,tw)
    # ennemis le long du chemin
    foes=[(24,slime,1.0),(52,slime,0.6),(84,goblin,0.9),(150,orc_knight,0.45),(178,shaman,0.7),(212,slime,0.3),(262,ogre,0.8),(300,goblin,0.5)]
    enemy_pos=[]
    for (d,fn,hp) in foes:
        x,y,dr=path_pt(d+t*2)
        sp=fn((t//2)%4) if fn is not shaman else shaman((t//3)%2, cast=(d==178 and t%8<4))
        if dr<0: sp=sp.mirror()
        ex,ey=int(x)-sp.w//2,Y+int(y)-sp.h+6
        add(ex,ey,sp); enemy_pos.append((ex+sp.w//2,ey,sp.w,hp))
    bx,by,_=path_pt(120+t*2); add(int(bx)-10,Y+int(by)-34+int(3*math.sin(t*0.7)),bat(t%4),False)
    items.sort(key=lambda a:(a[0],a[1]))
    for b_,x,y,sp,sh in items:
        if sh: shade_ell(sc,x+sp.w//2,y+sp.h-1,max(3,min(12,sp.w//2-2)),2)
        sc.paste(sp,x,y)
    for (cx,ey,w,hp) in enemy_pos: hbar(sc,cx-7,ey-4,12,hp)
    # projectiles + effets
    sc.paste(arrow(),46+(t%6)*4,Y+40-(t%6)*2); sc.paste(cannonball(),116-(t%4)*4,Y+20+(t%4))
    sc.paste(explosion(t%4),enemy_pos[2][0]-15,enemy_pos[2][1]-6)
    sc.paste(frostburst(t%3),enemy_pos[5][0]-13,enemy_pos[5][1]-6)
    ox,oy=144,Y+76-36
    tgt=[(enemy_pos[3][0],enemy_pos[3][1]+8),(enemy_pos[4][0],enemy_pos[4][1]+8)]
    prev=(ox,oy); rng=random.Random(t)
    for (tx,ty) in tgt:
        n=12
        for i in range(n+1):
            x=int(prev[0]+(tx-prev[0])*i/n+(rng.randint(-2,2) if 0<i<n else 0)); y=int(prev[1]+(ty-prev[1])*i/n+(rng.randint(-2,2) if 0<i<n else 0))
            sc.set(x,y,WHITE); sc.set(x+1,y,ix(Bl,H)); sc.set(x,y+1,GOLD)
        prev=(tx,ty)
    for i,(x,y) in enumerate(((enemy_pos[1][0]-4,enemy_pos[1][1]-8),(enemy_pos[1][0]+4,enemy_pos[1][1]-12),(enemy_pos[1][0]-10,enemy_pos[1][1]-14))): sc.paste(coin((t+i)%4),x,y-(t%4))
    # menu circulaire autour de l'emplacement choisi
    icons=[tower_archer(1),tower_cannon(1),tower_frost(1),tower_storm(1)]
    spots=[(sel[0]-11,sel[1]-44),(sel[0]+16,sel[1]-26),(sel[0]-11,sel[1]-12+0),(sel[0]-38,sel[1]-26)]
    spots=[(sel[0]-34,sel[1]-30),(sel[0]-11,sel[1]-44),(sel[0]+12,sel[1]-30),(sel[0]+26,sel[1]-8)]
    for i,(ic,(x,y)) in enumerate(zip(icons,spots)): sc.paste(ring_btn(ic,sel=(i==1)),x,y)
    # HUD
    hud=S(W,HUD)
    paint(hud,m_rect(0,0,W-1,HUD-1),Wd,tex='hatch')
    for x in range(W): hud.set(x,HUD-1,ix(Wd,O)); hud.set(x,HUD-2,GOLD if x%2==0 else ix(E,B)); hud.set(x,0,ix(Wd,L))
    hud.paste(heart_s2(),6,7); hud.paste(coin(0),52,7)
    frame_box(hud,W-28,2,24,18)
    for i in range(2):
        for p in m_poly([(W-22+i*7,6),(W-15+i*7,11),(W-22+i*7,16)]): hud.set(*p,ix(G,L))
    sc.paste(hud,0,0)
    im=sc.image(PAL); bg=Image.new('RGBA',(W,Hh),tuple(PAL[BLACK])+(255,)); bg.alpha_composite(im)
    mk.text(bg,"18",17,9,1,(255,248,232)); mk.text(bg,"245",63,9,1,(255,214,120))
    mk.text(bg,"WAVE 7/12",110,4,1,(255,248,232));
    for i in range(12): ImageDraw.Draw(bg).rectangle([108+i*7,14,112+i*7,17],fill=(242,184,58) if i<7 else (70,50,40))
    # textes "juicy" : degats et +or
    def pop(txt,x,y,col): mk.text(bg,txt,x+1,y+1,1,(30,16,10)); mk.text(bg,txt,x,y,1,col)
    pop("-12",enemy_pos[3][0]-6,enemy_pos[3][1]-14-(t%4),(255,255,255))
    pop("+5",enemy_pos[1][0]+6,enemy_pos[1][1]-18-(t%5),(255,214,90)); pop("CRIT!",enemy_pos[2][0]-14,enemy_pos[2][1]-16-(t%3),(255,120,60))
    for pr,(x,y) in zip((50,80,70,90),[(sel[0]-34,sel[1]-30),(sel[0]-11,sel[1]-44),(sel[0]+12,sel[1]-30),(sel[0]+26,sel[1]-8)]):
        pop(str(pr),x+5,y+22,(255,214,90))
    for i,c in enumerate((('A',(214,162,72)),)): pass
    return bg
def up(im,sc=4): return im.convert('RGB').resize((im.width*sc,im.height*sc),Image.NEAREST)
if __name__=='__main__':
    sheet_towers().convert('RGB').save(f'{OUT}/W_td_towers.png')
    sheet_enemies().convert('RGB').save(f'{OUT}/X_td_enemies.png')
    sheet_fx().convert('RGB').save(f'{OUT}/Y_td_fx_map.png')
    up(compose(3)).save(f'{OUT}/Z_td_scene.png')
    fr=[up(compose(t),3) for t in range(16)]
    fr[0].save(f'{OUT}/tower_defense.gif',save_all=True,append_images=fr[1:],duration=110,loop=0)
    print('ok')
