# Export de tout l'art + des salles du Zelda-like vers src/zelda_art.h (PROGMEM, 4 bits a palette locale ou RLE)
# Lancer :  cd tools/art && python export_zelda.py
import os, sys, hashlib
from boss import *
from scene import hud_s, heart_s, gem_s, key_s, sword_icon, boot_icon, frame_box, W, HUD
from hero_more import attack, hurt, roll, victory
ROOT=os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..'))
OUTH=os.path.join(ROOT,'src','zelda_art.h')

# ------------------------------------------------------------------ registre de sprites
SPR=[]; BYHASH={}; NAMES={}
def key_of(s): return hashlib.md5(repr((s.w,s.h,s.p)).encode()).hexdigest()
def reg(s,name=None,anim=1):
    k=key_of(s)+str(anim)
    if k in BYHASH and name is None: return BYHASH[k]
    i=len(SPR); SPR.append([s,anim]); BYHASH[k]=i
    if name: NAMES[name]=i
    return i
def seq(frames,name):
    """frames contigus (anime) ; le 1er porte anim=len"""
    i0=len(SPR)
    for j,s in enumerate(frames): SPR.append([s,len(frames) if j==0 else 1])
    NAMES[name]=i0; return i0
def encode(s):
    flat=[v for row in s.p for v in row]
    cols=sorted({v for v in flat if v is not None})
    runs=[]; i=0
    while i<len(flat):
        j=i
        while j<len(flat) and flat[j]==flat[i] and j-i<255: j+=1
        runs+= [j-i, 255 if flat[i] is None else flat[i]]; i=j
    if len(cols)<=15:
        m={c:k+1 for k,c in enumerate(cols)}
        nib=[m[v] if v is not None else 0 for v in flat]
        if len(nib)%2: nib.append(0)
        packed=list(cols)+[(nib[k]<<4)|nib[k+1] for k in range(0,len(nib),2)]
        if len(packed)<=len(runs): return 0,len(cols),packed
    return 1,0,runs

# ------------------------------------------------------------------ personnages
DIRS=('down','up','right','left')
seq([human(d,f,HERO) for d in DIRS for f in range(4)],'HERO_WALK')        # dir*4+f
seq([attack(d,k) for d in DIRS for k in range(3)],'HERO_ATK')             # dir*3+k (32x32, heros en 8,6)
reg(hurt(),'HERO_HURT'); seq([roll(0),roll(1)],'HERO_ROLL'); seq([victory(0),victory(1)],'HERO_VIC')
NPC_ORDER=['marchand','forgeron','vieille','enfant','garde']
for n in NPC_ORDER:
    seq([npc(n,'down',0),npc(n,'down',1),npc(n,'right',0),npc(n,'right',1),npc(n,'left',0),npc(n,'left',1)],'NPC_'+n.upper())
# ennemis (regardent a droite ; miroir au rendu)
seq([sporeling(k) for k in range(4)],'SPORE_W'); seq([sporeling(k,'attack') for k in range(2)],'SPORE_A')
seq([thornboar(k) for k in range(4)],'BOAR_W'); seq([thornboar(k,'attack') for k in range(2)],'BOAR_A')
seq([leafbat(k) for k in range(4)],'BAT_F'); reg(leafbat(0,'dive'),'BAT_D')
seq([bonewalker(k) for k in range(4)],'BONE_W'); seq([bonewalker(k,'attack') for k in range(2)],'BONE_A')
seq([shroudling(k) for k in range(4)],'SHROUD_F'); seq([shroudling(k,'attack') for k in range(2)],'SHROUD_A')
seq([gravespinner(k) for k in range(4)],'SPIDER_W'); reg(gravespinner(0,'attack'),'SPIDER_A'); seq([webshot(k) for k in range(3)],'WEB')
# golem : pieces x 3 phases x 2 pulsations
for nm,fn in (('G_TORSO',g_torso),('G_SHOULDER',g_shoulder),('G_FIST',g_fist),('G_LEG',g_leg)):
    seq([fn(p,k) for p in (1,2,3) for k in (0,1)],nm)                      # (phase-1)*2+k
seq([g_head(p,k) for p in (1,2,3) for k in (0,1)]+[g_head(1,0,False)],'G_HEAD')   # +6 = endormi
seq([fragment(0,0),fragment(1,0)],'G_FRAG'); seq([death(2),death(3)],'G_RUBBLE')
# effets
seq([firefly(k) for k in range(4)],'FX_FIREFLY'); seq([leaf(k,[E,Tc,E,G][k]) for k in range(4)],'FX_LEAF'); reg(spore(1),'FX_SPORE')
seq([shockwave(k) for k in range(4)],'FX_SHOCK'); seq([eruption(k) for k in range(4)],'FX_ERUPT'); seq([boulder(k,3) for k in range(4)],'FX_BOULDER')
seq([fire_trail(k) for k in range(2)],'FX_TRAIL'); seq([ember(k) for k in range(4)],'FX_EMBER'); seq([heart_container(k) for k in range(2)],'FX_HEARTC')
seq([drip(k) for k in range(4)],'FX_DRIP'); seq([smoke(k) for k in range(4)],'FX_SMOKE')
# HUD
def hud_bg():
    s=S(W,HUD)
    paint(s,m_rect(0,0,W-1,HUD-1),Wd,tex='hatch')
    for x in range(W): s.set(x,HUD-1,ix(Wd,O)); s.set(x,HUD-2,GOLD) if x%2==0 else s.set(x,HUD-2,ix(E,B)); s.set(x,0,ix(Wd,L))
    for x in range(2,W,8): s.set(x,HUD-3,ix(Wd,S_))
    s.paste(gem_s(),6,13); s.paste(key_s(),48,14)
    for i in range(2): frame_box(s,W-52+i*26,2,22,18)
    return s
reg(hud_bg(),'HUD_BG'); seq([heart_s('full',0),heart_s('full',1),heart_s('half',0),heart_s('empty',0)],'HUD_HEART')
reg(sword_icon(),'HUD_SWORD'); reg(boot_icon(),'HUD_BOOT')
reg(boss_bar(1.0),'HUD_BOSSBAR')
reg(gem_s(),'ICON_GEM'); reg(key_s(),'ICON_KEY'); reg(chest(True),'CHEST_OPEN'); reg(chest(),'CHEST_SHUT'); reg(crypt_door(False),'DOOR_OPEN')

# ------------------------------------------------------------------ salles
Z_VILLAGE,Z_FOREST,Z_CRYPT,Z_ARENA=0,1,2,3
O_PROP,O_DECAL,O_FG,O_NPC,O_SIGN,O_CHEST,O_DOOR,O_WARP,O_ENEMY,O_GRASS,O_POT,O_SPIKES,O_BOSS,O_LIGHT,O_GATE=range(15)
E_SPORE,E_BOAR,E_BAT,E_BONE,E_SHROUD,E_SPIDER=range(6)
C_FREE,C_SOLID,C_WATER,C_LAVA=0,1,2,3
ROOMS=[]
class Room:
    def __init__(s,zone,name):
        s.zone=zone; s.name=name; s.t=[[0]*15 for _ in range(7)]; s.c=[[0]*30 for _ in range(14)]; s.o=[]; s.ex=[-1,-1,-1,-1]
        s.id=len(ROOMS); ROOMS.append(s)
    def tile(s,r,c,sp,coll=None):
        s.t[r][c]=sp if isinstance(sp,int) else reg(sp)
        if coll is not None:
            for sr in (0,1):
                for sc in (0,1): s.c[r*2+sr][c*2+sc]=coll
    def tile_anim(s,r,c,frames):
        k=key_of(frames[0])+'anim'
        if k not in BYHASH: BYHASH[k]=seq(frames,'_a%d'%len(SPR))
        s.t[r][c]=BYHASH[k]
    def sub(s,sr,sc,v):
        if 0<=sr<14 and 0<=sc<30: s.c[sr][sc]=v
    def block(s,x,y,w,h,v=C_SOLID):
        for sr in range(14):
            for sc in range(30):
                cx,cy=sc*8+4,sr*8+4
                if x<=cx<x+w and y<=cy<y+h: s.c[sr][sc]=v
    def obj(s,typ,x,y,spr=0,a=0,b=0,c=0,w=0,h=0):
        s.o.append((typ,a,b,c,spr,x,y,w,h)); return len(s.o)-1
    def prop(s,sp,x,y,foot=None,anim=None,typ=O_PROP):
        """sp: sprite ou liste de frames ; foot = (dx,dy,w,h) zone solide relative"""
        if isinstance(sp,list): k=key_of(sp[0])+'anim%d'%len(sp); i=BYHASH.get(k)
        else: i=None
        if isinstance(sp,list):
            if i is None: i=seq(sp,'_p%d'%len(SPR)); BYHASH[k]=i
            s0=sp[0]
        else: i=reg(sp); s0=sp
        s.obj(typ,x,y,i,a=(len(sp) if isinstance(sp,list) else 1),b=anim or 4)
        if foot: s.block(x+foot[0],y+foot[1],foot[2],foot[3])
        return i
def water_sub(room,r,c,mask,lava=False):
    for sr in (0,1):
        for sc in (0,1):
            n=0
            for y in range(sr*8,sr*8+8):
                for x in range(sc*8,sc*8+8):
                    if cfield(mask,x,y,37 if lava else 23)>=0.5: n+=1
            if n>=28: room.c[r*2+sr][c*2+sc]=C_LAVA if lava else C_WATER
def vg(lines):
    return [[1 if ch!='.' else 0 for ch in ln] for ln in lines]
def cmask(V,r,c): return V[r][c]|(V[r][c+1]<<1)|(V[r+1][c]<<2)|(V[r+1][c+1]<<3)

# ---------------- VILLAGE (2 salles) : sol village, chemin a masques d'aretes, maisons
def village_ground(room,P,cob=()):
    for r in range(7):
        for c in range(15): room.tile(r,c,grass_t((r*3+c*5)%4))
    for r in range(7):
        for c in range(15):
            if (r,c) in cob: room.tile(r,c,cobble()); continue
            if P(r,c):
                m=0
                for i,(dr,dc) in enumerate(((-1,0),(0,1),(1,0),(0,-1))):
                    rr,cc=r+dr,c+dc
                    if (0<=cc<15 and 0<=rr<7 and P(rr,cc)) or cc<0 or cc>=15: m|=1<<i
                room.tile(r,c,path_auto(m))
R0=Room(Z_VILLAGE,'village square')
village_ground(R0,lambda r,c: r==4 or (r==3 and c==7),cob={(4,6),(4,7),(4,8),(5,6),(5,7),(5,8)})
for (r,c,k) in ((5,1,0),(6,12,1),(5,3,2),(6,9,0),(6,14,2),(6,2,1)): R0.tile(r,c,flowers(k))
for c in (11,12): R0.tile(5,c,garden(c%2))
base=62
R0.prop(house(Tc,Tc),4,base-36,(2,18,28,18)); R0.prop(house(Bl,Bl,beams=True),40,base-36,(2,18,28,18))
R0.prop(inn(),78,base-40,(2,20,44,20)); R0.prop(shop(),130,base-36,(2,17,28,19))
R0.prop([mill(0),mill(1)],168,base-52,(8,24,24,28),anim=8); R0.prop(cabin(),206,base-36,(3,19,26,17))
for (x,y) in ((4+19,base-45),(40+19,base-45),(78+3,base-50)): R0.prop([smoke(k) for k in range(4)],x,y,None,anim=6,typ=O_FG)
R0.prop(well(),112,72,(1,13,14,10)); R0.prop([lavoir(0),lavoir(1)],16,88,(0,4,32,12),anim=10)
R0.prop(market(),150,82,(1,16,30,12)); R0.prop(bench(),48,82,(1,6,14,8)); R0.prop(barrel(),190,90,(2,6,12,10))
R0.prop(crate(),204,92,(2,6,12,10)); R0.prop(haystack(),220,92,(1,6,14,10))
R0.prop([lantern(0),lantern(1)],84,74,(5,18,6,6),anim=8); R0.prop([lantern(1),lantern(0)],196,70,(5,18,6,6),anim=8)
R0.obj(O_SIGN,92,64,reg(signpost()),b=1); R0.block(96,72,8,8)
for c in range(0,5): R0.tile(6,c,fence('h')); R0.block(c*16,100,16,10)
for c in range(9,11): R0.tile(6,c,fence('h')); R0.block(c*16,100,16,10)
R0.obj(O_NPC,166,60,NAMES['NPC_MARCHAND'],a=0,b=2)
R0.obj(O_NPC,52,66,NAMES['NPC_VIEILLE'],a=2,b=3)
R0.obj(O_NPC,30,96,NAMES['NPC_ENFANT'],a=3,b=4)
R0.block(0,0,240,30)                                # maisons du fond
R0.ex=[-1,1,-1,-1]
R1=Room(Z_VILLAGE,'village gate')
village_ground(R1,lambda r,c: r==4 or (c==3 and r>=4))
R1.prop(forge(),20,26-6,(2,18,28,18)); R1.prop(house(Tc,Tc),60,20,(2,18,28,18)); R1.prop(thatch_house(),100,20,(3,21,26,15))
R1.prop([smoke(k) for k in range(4)],20+20,8,None,anim=5,typ=O_FG)
R1.prop(cabin(),150,20,(3,19,26,17))
for c in (0,1): R1.tile(6,c,garden(c%2))
for c in range(5,10): R1.tile(6,c,fence('h')); R1.block(c*16,100,16,10)
R1.prop(barrel(),44,52,(2,6,12,10)); R1.prop(crate(),190,52,(2,6,12,10)); R1.prop(haystack(),120,88,(1,6,14,10))
R1.prop([lantern(0),lantern(1)],186,72,(5,18,6,6),anim=8)
R1.obj(O_NPC,44,72,NAMES['NPC_FORGERON'],a=1,b=5)
R1.obj(O_GATE,212,54,NAMES['NPC_GARDE'],a=4,b=6)          # garde : bloque la sortie sans epee
R1.block(0,0,240,36)
for r in range(14):
    if r not in (7,8,9): R1.sub(r,29,C_SOLID)
R1.ex=[-1,2,-1,0]

# ---------------- FORET (4 salles)
def forest_ground(room,W_,P_,cliff=False,seed=0):
    k=0
    for r in range(7):
        for c in range(15):
            if cliff and r<2: room.tile(r,c,cliff_t(r,(c*5+1+seed)%4),C_SOLID); continue
            wm=cmask(W_,r,c) if W_ else 0; pm=cmask(P_,r,c) if P_ else 0
            if wm:
                room.tile_anim(r,c,[water_c(wm,k) for k in range(4)])
                if wm==15: room.tile(r,c,room.t[r][c],C_WATER)
                else: water_sub(room,r,c,wm)
            elif pm: room.tile(r,c,path_c(pm))
            else: room.tile(r,c,floor_t((r*7+c*3+r*c+seed)%4))
def trees_top(room,xs):
    kinds={'o':(oak(),(13,38,14,8)),'p':(pine(),(10,40,10,8)),'b':(birch(),(10,40,8,6)),'m':(maple(),(13,38,12,8)),'h':(oak(True),(13,38,14,8))}
    for (k,x,y) in xs:
        sp,f=kinds[k]; room.prop(sp,x,y,f)
F_PATH=['................','................','................','................',
        '################','................','................','................']
R2=Room(Z_FOREST,'forest path')
forest_ground(R2,None,vg(F_PATH),seed=1)
trees_top(R2,[('o',-8,-10),('p',28,-16),('b',66,-8),('o',100,-12),('p',140,-16),('m',176,-10),('p',212,-16),
              ('p',-6,64),('o',150,62),('b',212,64)])
R2.block(0,0,240,28)
R2.prop(bush(),60,38,(2,8,16,8)); R2.prop(rock_s(),126,40,(2,6,12,8)); R2.prop(stump(),100,86,(2,8,12,8))
R2.prop(hollow_log(),30,88,(2,6,32,12)); R2.prop(mush_red(),70,94,None); R2.prop([fern(0),fern(1)],120,92,None,anim=12)
R2.prop([mush_glow(0),mush_glow(1)],196,40,None,anim=14)
for (x,y) in ((56,72),(72,72),(186,90),(170,96)): R2.obj(O_GRASS,x,y,NAMES.get('_tg') or seq([tallgrass(0),tallgrass(1)],'_tg'))
R2.obj(O_ENEMY,80,80,a=E_SPORE); R2.obj(O_ENEMY,180,74,a=E_SPORE)
R2.obj(O_SIGN,8,44,reg(signpost()),b=7); R2.block(12,52,8,8)
R2.ex=[-1,3,-1,1]
F_RIV_W=['................','................','........#####...','........#####...',
         '.........###....','.........###....','.........###....','.........###....']
F_RIV_P=['................','................','................','...............#',
         '#########...####','.............#..','.............#..','.............#..']
R3=Room(Z_FOREST,'forest river')
forest_ground(R3,vg(F_RIV_W),vg(F_RIV_P),cliff=True,seed=2)
R3.prop([waterfall(k) for k in range(4)],144,-12,None,anim=3,typ=O_DECAL)
bi=R3.prop(bridge(),128,51,None,typ=O_DECAL)
R3.block(136,58,48,14,C_FREE)                       # le pont est praticable
trees_top(R3,[('o',-8,-6),('p',26,-14),('b',98,-2),('p',178,-16),('m',206,-12),('h',-6,64)])
R3.prop(bush(),66,28,(2,8,16,8)); R3.prop(rock_s(),120,34,(2,6,12,8)); R3.prop(rock_b(),214,84,(2,8,28,14))
R3.prop(stump(),112,96,(2,8,12,8)); R3.prop(hollow_log(),36,92,(2,6,32,12)); R3.prop(mush_red(),84,94,None)
R3.prop([fern(0),fern(1)],100,82,None,anim=12); R3.prop([fern(1),fern(0)],224,60,None,anim=12); R3.prop(mush_brown(),228,96,None)
R3.obj(O_ENEMY,200,56,a=E_BOAR); R3.obj(O_ENEMY,150,80,a=E_BAT)
for (x,y) in ((160,96),(56,70)): R3.obj(O_GRASS,x,y,NAMES['_tg'])
for r in range(14): R3.sub(r,29,C_SOLID)
for c in range(30):
    if not 24<=c<=27: R3.sub(13,c,C_SOLID)          # sortie sud seulement par le chemin
R3.ex=[-1,-1,4,2]
F_CLR_P=['.............#..','.............#..','.............#..','........######..',
         '........#.......','###########.....','................','................']
R4=Room(Z_FOREST,'forest clearing')
forest_ground(R4,None,vg(F_CLR_P),seed=3)
trees_top(R4,[('p',-8,-16),('o',24,-12),('m',60,-14),('p',96,-18),('h',150,-12),('p',182,-18),('o',212,-8),
              ('b',150,64),('p',190,60),('o',212,68)])
R4.block(0,0,200,26); R4.block(224,0,16,26)
R4.obj(O_CHEST,118,30,reg(chest()),a=1,b=8)                # coffre : CLE de la crypte
R4.block(120,36,14,10)
for (x,y) in ((100,30),(140,28)): R4.prop([fern(0),fern(1)],x,y,None,anim=12)
R4.prop([mush_glow(0),mush_glow(1)],60,96,None,anim=14); R4.prop(mush_red(),24,64,None); R4.prop(rock_b(),96,84,(2,8,28,14))
R4.prop(bush(),40,92,(2,8,16,8))
for (x,y) in ((60,50),(76,50),(170,94)): R4.obj(O_GRASS,x,y,NAMES['_tg'])
R4.obj(O_ENEMY,60,70,a=E_BOAR); R4.obj(O_ENEMY,140,60,a=E_BAT); R4.obj(O_ENEMY,30,40,a=E_SPORE)
for r in range(14): R4.sub(r,29,C_SOLID)
for c in range(30):
    if not 24<=c<=27: R4.sub(0,c,C_SOLID)          # entree nord seulement par le chemin
R4.ex=[3,-1,-1,5]
F_RUIN_P=['................','................','.......##.......','.......##.......',
          '.......#########','................','................','................']
R5=Room(Z_FOREST,'forest ruins')
forest_ground(R5,None,vg(F_RUIN_P),cliff=True,seed=4)
R5.obj(O_DOOR,104,0,reg(crypt_door()),a=6,b=9,c=0)         # porte verrouillee -> crypte (salle 6)
trees_top(R5,[('p',-8,-14),('o',22,-8),('p',196,-14),('m',212,-8),('o',-6,66),('p',40,60)])
R5.prop(pillar(True),70,38,(2,34,14,8)); R5.prop(pillar(True),152,38,(2,34,14,8))
R5.prop(tombstone(0),40,86,(3,10,10,7)); R5.prop(tombstone(1),180,84,(3,10,10,7)); R5.prop(statue(True),206,60,(2,34,22,10))
R5.prop(rock_s(),130,90,(2,6,12,8)); R5.prop([fern(0),fern(1)],100,92,None,anim=12)
R5.obj(O_SIGN,140,50,reg(signpost()),b=10); R5.block(144,58,8,8)
R5.obj(O_ENEMY,90,80,a=E_SPORE); R5.obj(O_ENEMY,170,60,a=E_BAT)
for r in range(14): R5.sub(r,0,C_SOLID)
R5.ex=[-1,4,-1,-1]

# ---------------- CRYPTE (3 salles)
def crypt_room(name,face=None,floor=None,open_n=False,open_e=False,open_w=False):
    R=Room(Z_CRYPT,name)
    grid=[[1]*15]+[[1]+[2]*13+[1]]+[[1]+[0]*13+[1] for _ in range(5)]
    if open_n:
        for r in (0,1): grid[r][7]=0
    if open_e:
        for r in (3,4): grid[r][14]=0
    if open_w:
        for r in (3,4): grid[r][0]=0
    def wall(r,c): return r<0 or c<0 or c>=15 or (r<7 and grid[r][c]>0)
    for r in range(7):
        for c in range(15):
            g=grid[r][c]
            if g==1:
                m=sum(b<<i for i,b in enumerate((wall(r-1,c),wall(r,c+1),wall(r+1,c) if r+1<7 else 1,wall(r,c-1))))
                R.tile(r,c,wall_top(m),C_SOLID)
            elif g==2: R.tile(r,c,wall_face((face or {}).get(c,0)),C_SOLID)
            else: R.tile(r,c,slab_floor((floor or {}).get((r,c),0)))
    return R
R6=crypt_room('crypt hall',face={3:3,11:3,5:1},floor={(3,4):1,(5,11):2,(4,2):3,(6,3):4},open_n=True)
for tx in (42,186): R6.prop([wall_torch(k) for k in range(4)],tx,4,None,anim=3,typ=O_DECAL); R6.obj(O_LIGHT,tx+6,10,a=50)
R6.prop([chain(k) for k in range(4)],62,3,None,anim=6,typ=O_DECAL); R6.prop([chain((k+2)%4) for k in range(4)],164,3,None,anim=6,typ=O_DECAL)
R6.prop(cobweb(),16,32,None,typ=O_DECAL); R6.prop(cobweb('tr'),208,32,None,typ=O_DECAL)
R6.prop(pillar(),16,20,(2,34,14,10)); R6.prop(pillar(),206,20,(2,34,14,10)); R6.prop(pillar(True),16,64,(2,34,14,10))
R6.prop(statue(),74,0,(2,34,22,12)); R6.prop(statue(True),140,0,(2,34,22,12))
for (x,y) in ((44,40),(174,40),(190,90)): R6.obj(O_POT,x,y,NAMES.get('_urn') or seq([urn(0),urn(1)],'_urn'))
R6.prop([puddle(k,True) for k in range(2)],30,92,None,anim=10,typ=O_DECAL); R6.prop(bones(),120,90,None,typ=O_DECAL)
R6.obj(O_ENEMY,60,70,a=E_BONE); R6.obj(O_ENEMY,170,70,a=E_BONE)
R6.obj(O_WARP,104,106,a=5,b=112,c=40,w=32,h=6)               # sortie vers la foret (devant la porte)
R6.ex=[7,-1,-1,-1]
R7=crypt_room('crypt spikes',face={2:2,7:1,12:2},floor={(2,3):1,(4,9):2,(6,6):3,(3,12):4},open_e=True)
for tx in (26,202): R7.prop([wall_torch((k+1)%4) for k in range(4)],tx,4,None,anim=3,typ=O_DECAL); R7.obj(O_LIGHT,tx+6,10,a=48)
R7.prop([chain(k) for k in range(4)],100,3,None,anim=6,typ=O_DECAL); R7.prop([chain((k+1)%4) for k in range(4)],130,3,None,anim=6,typ=O_DECAL)
sp=NAMES.get('_spk') or seq([spikes(k) for k in range(4)],'_spk')
for (r,c,ph) in ((3,5,0),(4,5,0),(5,5,0),(2,9,2),(3,9,2),(4,9,2),(5,9,1),(6,9,1)): R7.obj(O_SPIKES,c*16,r*16,sp,c=ph)
R7.prop(cobweb(),16,32,None,typ=O_DECAL); R7.prop(tombstone(0),36,84,(3,10,10,7)); R7.prop(tombstone(1),176,36,(3,10,10,7))
R7.prop([brazier(k) for k in range(4)],112,44,(2,18,14,8),anim=3); R7.obj(O_LIGHT,121,52,a=42)
R7.prop([puddle(k) for k in range(2)],60,40,None,anim=10,typ=O_DECAL); R7.prop([drip(k) for k in range(4)],66,20,None,anim=8,typ=O_DECAL)
R7.obj(O_ENEMY,80,60,a=E_SHROUD); R7.obj(O_ENEMY,180,80,a=E_SHROUD); R7.obj(O_ENEMY,140,90,a=E_BONE)
R7.ex=[-1,8,6,-1]
R8=crypt_room('crypt sarcophagus',face={4:3,10:3,7:1},floor={(3,3):2,(5,12):1,(6,2):3,(2,11):4},open_w=True)
for tx in (42,186): R8.prop([wall_torch((k+2)%4) for k in range(4)],tx,4,None,anim=3,typ=O_DECAL); R8.obj(O_LIGHT,tx+6,10,a=50)
R8.prop(statue(),74,0,(2,34,22,12)); R8.prop(statue(),140,0,(2,34,22,12))
R8.prop(sarcophagus(),102,40,(1,4,34,24))
for bx in (78,144): R8.prop([brazier((k+bx)%4) for k in range(4)],bx,44,(2,18,14,8),anim=3); R8.obj(O_LIGHT,bx+9,52,a=40)
R8.prop(pillar(),16,20,(2,34,14,10)); R8.prop(pillar(),206,20,(2,34,14,10))
R8.prop(cobweb('tr'),208,32,None,typ=O_DECAL); R8.prop(bones(),58,86,None,typ=O_DECAL)
R8.obj(O_CHEST,186,76,reg(chest()),a=2,b=11)              # coffre : 5 gemmes / coeur
R8.block(188,82,14,10)
R8.prop(stairs_down(),112,92,None,typ=O_DECAL)
R8.obj(O_WARP,114,96,a=9,b=112,c=86,w=12,h=10)             # escalier -> arene
R8.obj(O_ENEMY,60,60,a=E_SPIDER); R8.obj(O_ENEMY,170,64,a=E_SPIDER); R8.obj(O_ENEMY,90,90,a=E_BONE)
R8.ex=[-1,-1,-1,7]

# ---------------- ARENE DU BOSS
R9=Room(Z_ARENA,'ember arena')
LV=[[0]*16 for _ in range(8)]
for r in range(4,8):
    for c in (1,2,3,12,13,14): LV[r][c]=1
LV[3][13]=1; LV[3][14]=1; LV[7][4]=1; LV[7][11]=1
grid=[[1]*15]+[[1]+[2]*13+[1]]+[[1]+[0]*13+[1] for _ in range(5)]
def wl(r,c): return r<0 or c<0 or c>=15 or (r<7 and grid[r][c]>0)
FV={(3,5):3,(5,6):2,(4,9):3,(6,7):1,(2,3):2,(3,10):1,(6,9):3}
for r in range(7):
    for c in range(15):
        g=grid[r][c]
        if g==1:
            m=sum(b<<i for i,b in enumerate((wl(r-1,c),wl(r,c+1),wl(r+1,c) if r+1<7 else 1,wl(r,c-1))))
            R9.tile(r,c,wall_top(m),C_SOLID)
        elif g==2: R9.tile(r,c,basalt_face(1 if c in (3,11) else 0),C_SOLID)
        else:
            lm=cmask(LV,r,c)
            if lm:
                R9.tile_anim(r,c,[lava_c(lm,k) for k in range(4)])
                if lm==15: R9.tile(r,c,R9.t[r][c],C_LAVA)
                else: water_sub(R9,r,c,lm,lava=True)
            else: R9.tile(r,c,basalt_floor(FV.get((r,c),0)))
R9.prop([rune_circle(k) for k in range(4)],88,62,None,anim=6,typ=O_DECAL)
R9.obj(O_BOSS,78,-10)
R9.ex=[-1,-1,-1,-1]

# ------------------------------------------------------------------ ecriture du header
def palette(p): return [((r>>3)<<11)|((g>>2)<<5)|(b>>3) for (r,g,b) in p]
PALS=[('PAL_DAY',PAL),('PAL_DUSK',tint(PAL,(1.05,0.8,0.72),0.12,(190,90,60))),('PAL_NIGHT',tint(PAL,(0.38,0.52,0.8),0.2,(8,24,52))),
      ('PAL_LIT',LIT),('PAL_MID',MID),('PAL_DARK',DARK),('PAL_ARENA',ARENA)]
blob=[]; entries=[]
for s,anim in SPR:
    fmt,nl,data=encode(s); off=len(blob); blob+=data
    entries.append((s.w,s.h,fmt,anim,nl,off))
tot=len(blob)
L_=[]
L_.append('// GENERE par tools/art/export_zelda.py -- ne pas modifier a la main')
L_.append('#pragma once\n#include <stdint.h>\nnamespace zart {')
for n,p in PALS: L_.append('static const uint16_t %s[48] = {%s};'%(n,','.join('0x%04X'%v for v in palette(p))))
L_.append('struct Spr { uint8_t w, h, fmt, anim, nlut; uint32_t off; };   // fmt 0 = 4 bits (lut nlut couleurs puis pixels), 1 = RLE (n, idx|255)')
L_.append('static const Spr SPR[%d] = {'%len(entries))
for e in entries: L_.append('{%d,%d,%d,%d,%d,%d},'%e)
L_.append('};')
L_.append('static const uint8_t BLOB[%d] = {'%tot)
for i in range(0,tot,40): L_.append(','.join(str(v) for v in blob[i:i+40])+',')
L_.append('};')
for n,i in sorted(NAMES.items(),key=lambda a:a[1]):
    if not n.startswith('_'): L_.append('static const uint16_t %s = %d;'%(n,i))
L_.append('static const uint16_t S_TALLGRASS = %d, S_URN = %d, S_SPIKES = %d;'%(NAMES['_tg'],NAMES['_urn'],NAMES['_spk']))
L_.append('struct Obj { uint8_t type, a, b, c; uint16_t spr; int16_t x, y, w, h; };')
L_.append('struct Room { uint8_t zone; int8_t ex[4]; uint16_t tiles[7][15]; uint8_t coll[14][30]; const Obj* objs; uint8_t nobj; };')
for R in ROOMS:
    L_.append('static const Obj OBJ_%d[%d] = {%s};'%(R.id,max(1,len(R.o)),','.join('{%d,%d,%d,%d,%d,%d,%d,%d,%d}'%o for o in R.o) or '{0}'))
L_.append('static const Room ROOMS[%d] = {'%len(ROOMS))
for R in ROOMS:
    L_.append('{%d,{%s},{%s},{%s},OBJ_%d,%d},  // %s'%(R.zone,','.join(map(str,R.ex)),
        ','.join('{'+','.join(map(str,row))+'}' for row in R.t),','.join('{'+','.join(map(str,row))+'}' for row in R.c),R.id,len(R.o),R.name))
L_.append('};')
L_.append('static const int NROOMS = %d;'%len(ROOMS))
L_.append('}  // namespace zart')
open(OUTH,'w',encoding='utf-8',newline='\n').write('\n'.join(L_)+'\n')
roomb=len(ROOMS)*(5+210+420)+sum(len(R.o) for R in ROOMS)*14
print('sprites:',len(SPR),' art: %.1f Ko'%(tot/1024+len(SPR)*9/1024),' salles: %.1f Ko'%(roomb/1024),' ->',OUTH)
