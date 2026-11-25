import os, sys
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','cover'))
import mk
from forest import *
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'preview')
BG=(34,28,48,255)
def label(im,txt,x,y,sc=2,col=(251,244,200)): mk.text(im,txt,x,y,sc,col)
def rows_sheet(rows,W=1280,sc=4,title=None):
    im=Image.new('RGBA',(W,3000),BG); y=8
    if title: label(im,title,14,y,2); y+=26
    for head,items in rows:
        label(im,head,14,y,2); y+=24; x=14; mh=0
        for name,sp in items:
            w,h=sp.w*sc,sp.h*sc
            if x+w>W-10: x=14; y+=mh+24; mh=0
            im.alpha_composite(sp.image().resize((w,h),Image.NEAREST),(x,y))
            label(im,name,x,y+h+3,1,(180,170,200)); x+=w+14; mh=max(mh,h)
        y+=mh+30
    return im.crop((0,0,W,y))
def sheet_decor():
    return rows_sheet([
     ('TREES : OAK / HOLLOW OAK / PINE / BIRCH / AUTUMN MAPLE',[('OAK',oak()),('HOLLOW OAK',oak(True)),('PINE',pine()),('BIRCH',birch()),('MAPLE',maple())]),
     ('FOREST PROPS',[('STUMP',stump()),('HOLLOW LOG',hollow_log()),('BUSH',bush()),('BUSH 2',bush(False)),('ROCK',rock_s()),('BOULDER',rock_b()),
                      ('RED CAPS',mush_red()),('BROWN CAPS',mush_brown()),('GLOW A',mush_glow(0)),('GLOW B',mush_glow(1)),('FERN A',fern(0)),('FERN B',fern(1))]),
     ('BRIDGE + WATERFALL (4 FRAMES)',[('BRIDGE',bridge())]+[('FALL %d'%k,waterfall(k)) for k in range(4)]),
    ])
def sheet_tiles():
    return rows_sheet([
     ('FOREST FLOOR + TALL GRASS (2 FRAMES) + CLIFF',[('FLOOR %d'%v,floor_t(v)) for v in range(4)]+[('TALL A',tallgrass(0)),('TALL B',tallgrass(1))]+
        [('CLIFF TOP %d'%v,cliff_t(0,v)) for v in range(4)]+[('CLIFF BASE %d'%v,cliff_t(1,v)) for v in range(4)]),
     ('DIRT PATH : CORNER AUTO-TILING (16 TILES, ORGANIC EDGES)',[('PATH %02d'%m,path_c(m)) for m in range(16)]),
     ('RIVER : CORNER AUTO-TILING WITH BANKS (16 TILES x 4 FRAMES)',[('WATER %02d'%m,water_c(m,0)) for m in range(16)]),
    ])
def sheet_enemies():
    sp=[sporeling(k) for k in range(4)]; bo=[thornboar(k) for k in range(4)]; ba=[leafbat(k) for k in range(4)]
    return rows_sheet([
     ('SPORELING : WALK x4 / ATTACK x2 (SPORE CLOUD) / DEATH BURST x4',sp and [('WALK %d'%k,s) for k,s in enumerate(sp)]+[('ATK %d'%k,sporeling(k,'attack')) for k in range(2)]+[('DIE %d'%k,burst(sp[0],k)) for k in range(4)]),
     ('THORNBOAR : RUN x4 / CHARGE x2 / DEATH BURST x4',[('RUN %d'%k,s) for k,s in enumerate(bo)]+[('CHARGE %d'%k,thornboar(k,'attack')) for k in range(2)]+[('DIE %d'%k,burst(bo[0],k)) for k in range(4)]),
     ('LEAFBAT : FLY x4 / DIVE / DEATH BURST x4',[('FLY %d'%k,s) for k,s in enumerate(ba)]+[('DIVE',leafbat(0,'dive'))]+[('DIE %d'%k,burst(ba[0],k)) for k in range(4)]),
     ('FX : FIREFLY x4 / FALLING LEAVES x4 / SPORE',[('FLY %d'%k,firefly(k)) for k in range(4)]+[('LEAF %d'%k,leaf(k,[E,Tc,E,G][k])) for k in range(4)]+[('SPORE',spore(1))]),
    ])
if __name__=='__main__':
    sheet_decor().convert('RGB').save(f'{OUT}/G_forest_decor.png')
    sheet_tiles().convert('RGB').save(f'{OUT}/H_forest_tiles.png')
    sheet_enemies().convert('RGB').save(f'{OUT}/I_forest_enemies.png')
    print('ok')
