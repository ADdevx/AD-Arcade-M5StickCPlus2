import os, sys
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','cover'))
import mk
from crypt import *
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'preview')
BG=(26,22,40,255)
def label(im,txt,x,y,sc=2,col=(251,244,200)): mk.text(im,txt,x,y,sc,col)
def rows_sheet(rows,W=1280,sc=4,pal=None):
    pal=pal or LIT
    im=Image.new('RGBA',(W,3000),BG); y=8
    for head,items in rows:
        label(im,head,14,y,2); y+=24; x=14; mh=0
        for name,sp in items:
            w,h=sp.w*sc,sp.h*sc
            if x+w>W-10: x=14; y+=mh+24; mh=0
            im.alpha_composite(sp.image(pal).resize((w,h),Image.NEAREST),(x,y))
            label(im,name,x,y+h+3,1,(180,170,200)); x+=w+14; mh=max(mh,h)
        y+=mh+30
    return im.crop((0,0,W,y))
def sheet_decor():
    return rows_sheet([
     ('PILLARS / GUARDIAN STATUES / SARCOPHAGUS / LOCKED DOOR',[('PILLAR',pillar()),('BROKEN PILLAR',pillar(True)),('STATUE',statue()),('BROKEN STATUE',statue(True)),('SARCOPHAGUS',sarcophagus()),('DOOR',crypt_door())]),
     ('TOMBS / BONES / URNS / CHEST / STAIRS / COBWEBS',[('TOMB A',tombstone(0)),('TOMB B',tombstone(1)),('BONES',bones()),('URN',urn()),('URN CRACK',urn(1)),('CHEST',chest()),('CHEST OPEN',chest(True)),('STAIRS',stairs_down()),('WEB TL',cobweb()),('WEB TR',cobweb('tr'))]),
     ('ANIMATED : TORCH x4 / BRAZIER x4 / CHAIN x4 / SPIKE TRAP x4',[('TORCH %d'%k,wall_torch(k)) for k in range(4)]+[('BRAZIER %d'%k,brazier(k)) for k in range(4)]+[('CHAIN %d'%k,chain(k)) for k in range(4)]+[('SPIKES %d'%k,spikes(k)) for k in range(4)]),
     ('PUDDLES x2 + WATER DRIP x4',[('PUDDLE %d'%k,puddle(k)) for k in range(2)]+[('POOL %d'%k,puddle(k,True)) for k in range(2)]+[('DRIP %d'%k,drip(k)) for k in range(4)]),
    ])
def sheet_tiles():
    return rows_sheet([
     ('FLOOR SLABS : CLEAN / CRACKED x2 / DAMP / BONES',[('FLOOR %d'%v,slab_floor(v)) for v in range(5)]+[('FACE %d'%v,wall_face(v)) for v in range(4)]),
     ('WALL TOPS : AUTO-TILING (16 NEIGHBOUR MASKS)',[('TOP %02d'%m,wall_top(m)) for m in range(16)]),
    ])
def sheet_enemies():
    bw=[bonewalker(k) for k in range(4)]; sh=[shroudling(k) for k in range(4)]; gs=[gravespinner(k) for k in range(4)]
    return rows_sheet([
     ('BONEWALKER : WALK x4 / CLUB ATTACK x2 / DEATH BURST x4',[('WALK %d'%k,s) for k,s in enumerate(bw)]+[('ATK %d'%k,bonewalker(k,'attack')) for k in range(2)]+[('DIE %d'%k,burst(bw[0],k)) for k in range(4)]),
     ('SHROUDLING : FLOAT x4 / WAIL LUNGE x2 / DEATH BURST x4',[('FLOAT %d'%k,s) for k,s in enumerate(sh)]+[('ATK %d'%k,shroudling(k,'attack')) for k in range(2)]+[('DIE %d'%k,burst(sh[0],k)) for k in range(4)]),
     ('GRAVESPINNER : CRAWL x4 / REAR + WEB SHOT x3 / DEATH BURST x4',[('CRAWL %d'%k,s) for k,s in enumerate(gs)]+[('REAR',gravespinner(0,'attack'))]+[('WEB %d'%k,webshot(k)) for k in range(3)]+[('DIE %d'%k,burst(gs[0],k)) for k in range(4)]),
    ])
def sheet_palette():
    im=Image.new('RGB',(900,200),(26,22,40)); d=ImageDraw.Draw(im)
    label(im,'CRYPT LIGHTING : 3 PALETTE SWAPS PICKED PER PIXEL BY TORCH DISTANCE (DITHERED)',10,8,1)
    for i,(n,p) in enumerate((('TORCHLIT',LIT),('HALF-LIGHT',MID),('DARK',DARK))):
        label(im,n,10+i*290,30,2)
        for r in range(9):
            for t in range(5): d.rectangle([10+i*290+t*22,56+r*14,10+i*290+t*22+20,56+r*14+12],fill=p[r*5+t])
    return im
if __name__=='__main__':
    sheet_palette().save(f'{OUT}/K_crypt_palette.png')
    sheet_decor().convert('RGB').save(f'{OUT}/L_crypt_decor.png')
    sheet_tiles().convert('RGB').save(f'{OUT}/M_crypt_tiles.png')
    sheet_enemies().convert('RGB').save(f'{OUT}/N_crypt_enemies.png')
    print('ok')
