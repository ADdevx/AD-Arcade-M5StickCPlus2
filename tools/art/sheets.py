import sys; import os; sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','cover'))
import mk
from village import *
from hero_sheet import sheet
def label(im,txt,x,y,sc=2,col=(251,244,200)): mk.text(im,txt,x,y,sc,col)
def sheet_buildings():
    bs=[('RED HOUSE',house(Tc,Tc)),('BLUE HOUSE',house(Bl,Bl,beams=True)),('THATCH',thatch_house()),('CABIN',cabin()),('FORGE',forge()),('SHOP',shop()),('INN',inn()),('MILL',mill(0)),('MILL 2',mill(1))]
    sc=4; W=1280; im=Image.new('RGBA',(W,980),(34,28,48,255))
    x=14;y=34;rowh=0
    for name,sp in bs:
        if x+sp.w*sc>W-10: x=14; y+=rowh+34; rowh=0
        im.alpha_composite(sp.image().resize((sp.w*sc,sp.h*sc),Image.NEAREST),(x,y)); label(im,name,x,y-22,2); x+=sp.w*sc+22; rowh=max(rowh,sp.h*sc)
    return im.crop((0,0,W,y+rowh+14))
if __name__=='__main__':
    sheet_buildings().convert('RGB').save('/tmp/zel2/t_build.png')

def sheet_props():
    sc=4; W=1280; im=Image.new('RGBA',(W,900),(34,28,48,255))
    def row(items,y,title):
        label(im,title,14,y,2); x=14; mh=0
        for name,sp in items:
            im.alpha_composite(sp.image().resize((sp.w*sc,sp.h*sc),Image.NEAREST),(x,y+24)); 
            label(im,name,x,y+26+sp.h*sc,1,(180,170,200)); x+=sp.w*sc+14; mh=max(mh,sp.h*sc)
        return y+24+mh+22
    y=8
    y=row([('GRASS %d'%i,grass_t(i)) for i in range(4)]+[('SWAY A',grass_sway(0)),('SWAY B',grass_sway(1)),('COBBLE',cobble())]+[('FLOWER %d'%i,flowers(i)) for i in range(3)]+[('GARDEN A',garden(0)),('GARDEN B',garden(1))],y,'GROUND')
    y=row([('PATH %02d'%m,path_auto(m)) for m in range(16)],y,'PATH AUTO-TILING (16 EDGE MASKS)')
    y=row([('FENCE H',fence('h')),('FENCE V',fence('v')),('FENCE END',fence('e')),('BARREL',barrel()),('CRATE',crate()),('HAY',haystack()),('BENCH',bench()),('SIGN',signpost()),('WELL',well()),('LANTERN A',lantern(0)),('LANTERN B',lantern(1)),('LAVOIR A',lavoir(0)),('LAVOIR B',lavoir(1)),('MARKET',market())]+[('SMOKE %d'%k,smoke(k)) for k in range(4)],y,'VILLAGE PROPS + ANIMATED TILES')
    return im.crop((0,0,W,y))
def sheet_npc():
    sc=4; cw=22; rows=[]
    im=Image.new('RGBA',(8*cw*sc+10,5*26*sc+40),(34,28,48,255))
    for j,n in enumerate(NPCS):
        label(im,n.upper(),6,40+j*26*sc-2,1,(251,244,200)) if False else None
        sps=[npc(n,'down',f) for f in (0,1)]+[npc(n,'up',0),npc(n,'right',0),npc(n,'right',1),npc(n,'left',0)]
        for i,sp in enumerate(sps): im.alpha_composite(sp.image().resize((sp.w*sc,sp.h*sc),Image.NEAREST),(10+i*cw*sc,30+j*26*sc))
        label(im,n.upper(),10+6*cw*sc,60+j*26*sc,2)
    label(im,'VILLAGERS : DOWN x2, UP, RIGHT x2, LEFT',10,6,2)
    return im
def sheet_hero():
    rows,att=hero_all()
    r_walk=[x for r in rows[:2] for x in r],[x for r in rows[2:] for x in r]
    a=sheet(list(r_walk),scale=4,pad=3)
    b=sheet([[x for r in att[:2] for x in r],[x for r in att[2:] for x in r],[hurt(),hurt2(),roll(0),roll(1),victory(0),victory(1)]],scale=4,cw=38,ch=38)
    W=max(a.width,b.width); im=Image.new('RGBA',(W,a.height+b.height+70),(34,28,48,255))
    label(im,'HERO 16x24 : WALK x4 FRAMES (DOWN UP RIGHT LEFT)',10,6,2); im.alpha_composite(a,(0,28))
    label(im,'ATTACK x3 (DOWN UP RIGHT LEFT) / HURT / HURT 2 / ROLL x2 / VICTORY x2',10,a.height+34,2); im.alpha_composite(b,(0,a.height+56))
    return im
def sheet_palette():
    im=Image.new('RGB',(900,380),(34,28,48)); d=ImageDraw.Draw(im)
    label(im,'PALETTE : 48 COLOURS (RGB565) = 9 RAMPS x 5 TONES + 3',10,8,2)
    for r,n in enumerate(NAMES):
        label(im,n.upper(),10,56+r*34,1)
        for t in range(5): d.rectangle([110+t*54,48+r*34,110+t*54+50,48+r*34+28],fill=PAL[r*5+t])
    for i,(n,c) in enumerate((('WHITE',45),('BLACK',46),('GOLD',47))):
        d.rectangle([420+i*80,48,420+i*80+70,48+28],fill=PAL[c]); label(im,n,420+i*80,82,1)
    label(im,'TONES : OUTLINE / SHADE / BASE / LIGHT / HIGHLIGHT. LIGHT FROM TOP-LEFT.',390,150,1)
    label(im,'PALETTE SWAPS (SAME SPRITES): DAY / DUSK / NIGHT / CRYPT',390,170,1)
    for i,(n,p) in enumerate((('DAY',PAL),('DUSK',tint(PAL,(1.05,0.78,0.7),0.12,(200,80,60))),('NIGHT',tint(PAL,(0.45,0.55,0.95),0.18,(20,30,90))),('CRYPT',tint(PAL,(0.8,0.7,1.05),0.25,(60,40,110))))):
        label(im,n,390+i*118,190,1)
        for k in range(9): d.rectangle([390+i*118+(k%3)*12,206+(k//3)*12,390+i*118+(k%3)*12+10,206+(k//3)*12+10],fill=p[k*5+2])
    return im
