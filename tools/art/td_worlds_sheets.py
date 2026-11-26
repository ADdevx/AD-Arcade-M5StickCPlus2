from td_sheets import *
from td_worlds import *

def sheet_worlds():
    rows=[('NEW SPAWN PORTAL : RUNE ARCH + EMBER RIFT (4 FRAMES)',[('RIFT %d'%k,rift_portal(k)) for k in range(4)])]
    for w in ('meadow','desert','snow','volcano'):
        rows.append((w.upper()+' : GROUND x2 / PATH / DECOR',[('GROUND %d'%v,GROUNDS[w](v)) for v in range(2)]+[('PATH %02d'%m,world_path(w,m)) for m in (3,6,12,15)]+WORLD_DECOR[w]))
    return rows_sheet(rows)

# ------------------------------------------------------------ apercu d'un niveau par monde (chemins differents)
LAYOUTS={
 'meadow': [(0,24),(88,24),(88,88),(168,88),(168,40),(240,40)],
 'desert': [(0,88),(56,88),(56,24),(136,24),(136,72),(240,72)],
 'snow':   [(0,40),(40,40),(40,96),(120,96),(120,24),(200,24),(200,72),(240,72)],
 'volcano':[(0,96),(48,96),(48,24),(192,24),(192,88),(240,88)],
}
def vgrid_from(pts):
    V=[[0]*16 for _ in range(8)]
    for a,b_ in zip(pts,pts[1:]):
        x0,y0=a; x1,y1=b_
        n=max(abs(x1-x0),abs(y1-y0))//4+1
        for i in range(n+1):
            x=x0+(x1-x0)*i/n; y=y0+(y1-y0)*i/n
            c=int(round(x/16)); r=int(round(y/16))
            for rr in (r-1,r):
                for cc in (c-1,c):
                    if 0<=rr<8 and 0<=cc<16: V[rr][cc]=1
    return V
def world_scene(w,t=0,big=True):
    sc=S(W,Hh); Y=HUD; pts=LAYOUTS[w]; V=vgrid_from(pts)
    for r in range(7):
        for c in range(15):
            m=V[r][c]|(V[r][c+1]<<1)|(V[r+1][c]<<2)|(V[r+1][c+1]<<3)
            sc.paste(world_path(w,m) if m else GROUNDS[w]((r*3+c*5)%4),c*16,Y+r*16)
    if w=='volcano':
        LV=[[0]*16 for _ in range(8)]
        for (r,c) in ((4,6),(4,7),(5,6),(5,7),(4,8),(5,8)): LV[r][c]=1
        for r in range(7):
            for c in range(15):
                lm=LV[r][c]|(LV[r][c+1]<<1)|(LV[r+1][c]<<2)|(LV[r+1][c+1]<<3)
                if lm and not (V[r][c]|V[r][c+1]|V[r+1][c]|V[r+1][c+1]): sc.paste(lava_c(lm,t%4),c*16,Y+r*16)
    items=[]
    def add(x,y,sp,sh=True): items.append((y+sp.h,x,y,sp,sh))
    dec=[s for _,s in WORLD_DECOR[w]]
    spots={'meadow':[(112,-10),(150,-8),(2,70),(196,84),(60,48)],'desert':[(150,40),(4,10),(196,84),(90,52),(214,6)],
           'snow':[(70,40),(150,40),(8,64),(210,2),(160,80)],'volcano':[(100,70),(80,40),(150,46),(10,40),(214,40)]}[w]
    for i,(x,y) in enumerate(spots): add(x,Y+y,dec[i%len(dec)])
    ex,ey=pts[-1]; add(min(196,ex-44),Y+ey-40,castle(t//4%2),False)
    sx,sy=pts[0]; add(-6,Y+sy-28,rift_portal(t%4),False)
    towers={'meadow':[(tower_archer,2,36,64),(tower_cannon,1,128,48)],'desert':[(tower_cannon,2,96,62),(tower_archer,3,24,54)],
            'snow':[(tower_frost,3,80,72),(tower_archer,2,160,60)],'volcano':[(tower_storm,3,120,56),(tower_frost,2,160,96)]}[w]
    for (fn,lv,x,y) in towers:
        sc.paste(pad(),x-10,Y+y-7); tw=fn(lv,t%2); add(x-12,Y+y-tw.h+4,tw)
    foes={'meadow':[slime,slime,goblin],'desert':[goblin,goblin,orc_knight,shaman],'snow':[orc_knight,bat,shaman,orc_knight],'volcano':[orc_knight,ogre,goblin,bat]}[w]
    def ppt(d):
        for a,b_ in zip(pts,pts[1:]):
            L_=abs(b_[0]-a[0])+abs(b_[1]-a[1])
            if d<=L_: k=d/L_; return a[0]+(b_[0]-a[0])*k,a[1]+(b_[1]-a[1])*k
            d-=L_
        return pts[-1]
    for i,fn in enumerate(foes):
        x,y=ppt(40+i*46+t*2); sp=fn((t//2)%4)
        add(int(x)-sp.w//2,Y+int(y)-sp.h+6,sp)
    items.sort(key=lambda a:(a[0],a[1]))
    for b_,x,y,sp,sh in items:
        if sh: shade_ell(sc,x+sp.w//2,y+sp.h-1,max(3,min(12,sp.w//2-2)),2)
        sc.paste(sp,x,y)
    hud=S(W,HUD); paint(hud,m_rect(0,0,W-1,HUD-1),Wd,tex='hatch')
    for x in range(W): hud.set(x,HUD-1,ix(Wd,O)); hud.set(x,HUD-2,GOLD if x%2==0 else ix(E,B))
    hud.paste(heart_s2(),6,7); hud.paste(coin(0),52,7); sc.paste(hud,0,0)
    im=sc.image(PAL); bg=Image.new('RGBA',(W,Hh),(0,0,0,255)); bg.alpha_composite(im)
    names={'meadow':'1-2 MEADOW','desert':'2-1 DESERT','snow':'3-3 SNOW','volcano':'4-3 VOLCANO'}
    mk.text(bg,"20",17,9,1,(255,248,232)); mk.text(bg,"150",63,9,1,(255,214,120)); mk.text(bg,names[w],120,8,1,(255,248,232))
    return bg

# ------------------------------------------------------------ carte du monde
def world_map(t=0):
    sc=S(W,Hh)
    regions=[('meadow',0),('desert',60),('snow',120),('volcano',180)]
    for (w,x0) in regions:
        for r in range(9):
            for c in range(4):
                sc.paste(GROUNDS[w]((r+c)%4),x0+c*16,r*16-4)
    # route pointillee entre les niveaux
    nodes=[(18,98),(34,62),(22,28),(78,30),(96,66),(84,100),(138,98),(156,64),(142,28),(198,30),(216,66),(204,100)]
    for a,b_ in zip(nodes,nodes[1:]):
        n=int(math.hypot(b_[0]-a[0],b_[1]-a[1])/4)
        for i in range(n):
            if i%2==0: x=int(a[0]+(b_[0]-a[0])*i/n); y=int(a[1]+(b_[1]-a[1])*i/n); sc.set(x,y,ix(Wd,O)); sc.set(x+1,y,ix(Wd,S_))
    deco=[(cactus(1),74,48),(palm(),100,2),(snowy_pine(),120,40),(snowman(),170,82),(dead_tree(),182,40),(vent(t%2),230,84),(tree_round(0),40,40)]
    for sp,x,y in deco: sc.paste(sp,x,y)
    states=[4,3,4,2,3,1,0,0,0,0,0,0]
    for (x,y),st in zip(nodes,states): sc.paste(level_node(st),x-9,y-9)
    sc.paste(castle(t//4%2).copy(),214-40,-12) if False else None
    # curseur : heros sur le niveau courant
    sc.paste(human('down',(t//4)%2,HERO),84-8,100-30)
    im=sc.image(PAL); bg=Image.new('RGBA',(W,Hh),(0,0,0,255)); bg.alpha_composite(im)
    for (x,y),st in zip(nodes,states):
        if st>=2:
            for i in range(3): bg.alpha_composite(star_icon(i<st-1).image(PAL),(x-14+i*9,y+9))
    d=ImageDraw.Draw(bg); d.rectangle([0,0,239,12],fill=(40,24,16)); d.rectangle([0,12,239,13],fill=(242,184,58))
    mk.text(bg,"WORLD MAP",4,3,1,(255,248,232)); mk.text(bg,"STARS 11/36",160,3,1,(255,214,120))
    for i,(n,x0) in enumerate((('MEADOW',4),('DESERT',64),('SNOW',128),('VOLCANO',182))): mk.text(bg,n,x0,124,1,(255,248,232) if i<2 else (150,150,170))
    return bg
# ------------------------------------------------------------ boutique
def shop_screen():
    sc=S(W,Hh)
    paint(sc,m_rect(0,0,W-1,Hh-1),Wd,tex='hatch')
    for p in m_rect(6,18,W-7,Hh-7): sc.set(*p,ix(Pl,L))
    kinds=['damage','range','gold','lives','speed']
    for i,k in enumerate(kinds):
        x=12+i*45; sc.paste(shop_icon(k),x+8,26)
        for j in range(5):                                        # niveaux achetes
            for p in m_rect(x+3+j*7,52,x+8+j*7,56): sc.set(*p,GOLD if j<[3,1,2,0,1][i] else ix(St,S_))
    for p in m_rect(12+45-3,22,12+45+38,100): pass
    im=sc.image(PAL); bg=Image.new('RGBA',(W,Hh),(0,0,0,255)); bg.alpha_composite(im)
    d=ImageDraw.Draw(bg); d.rectangle([54,21,94,103],outline=(242,184,58),width=2)
    mk.text(bg,"UPGRADES",6,5,2,(255,248,232)); bg.alpha_composite(coin(0).image(PAL),(170,5)); mk.text(bg,"1240",182,7,1,(255,214,120))
    for i,(n,p) in enumerate((('DMG',120),('RANGE',150),('GOLD',100),('LIVES',200),('SPEED',180))):
        x=12+i*45; mk.text(bg,n,x+2,62,1,(52,34,26)); mk.text(bg,str(p),x+8,74,1,(160,90,20))
    mk.text(bg,"+10% TOWER DAMAGE",12,90,1,(52,34,26)); mk.text(bg,"A:BUY  B:NEXT  PWR:BACK",12,112,1,(52,34,26))
    return bg
if __name__=='__main__':
    sheet_worlds().convert('RGB').save(f'{OUT}/AA_td_portal_worlds.png')
    g=Image.new('RGB',(W*2*2,Hh*2*2))
    for i,w in enumerate(('meadow','desert','snow','volcano')): g.paste(up(world_scene(w,3),2),((i%2)*W*2,(i//2)*Hh*2))
    g.save(f'{OUT}/AB_td_4_worlds.png')
    g=Image.new('RGB',(W*3*2+20,Hh*3)); g.paste(up(world_map(2),3),(0,0)); g.paste(up(shop_screen(),3),(W*3+20,0)); g.save(f'{OUT}/AC_td_map_shop.png')
    print('ok')
