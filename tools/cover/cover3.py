# Covers M5Burner v1.9 (1280x720 + 800x800) pour chaque appareil
# Lancer : cd tools/cover && python cover3.py     (sources : src_v19/*.png, captures du harnais)
import os
from mk import *
HERE=os.path.dirname(os.path.abspath(__file__)); SRC=os.path.join(HERE,'src_v19')
def img(n): return Image.open(os.path.join(SRC,n+'.png')).convert('RGB')
DEVICES=[('M5STICKC PLUS2',''),('M5STICKC PLUS','StickCPlus-'),('M5STICKS3','StickS3-'),('M5CARDPUTER','Cardputer-')]
GOLD=(214,162,72); INK=(10,14,13); RED=(156,46,48); PALE=(212,222,200); DARK=(27,41,37)
def label(im,t,x,y,px,col=PALE): text(im,t,x,y,px,col,outline=INK,shadow=DARK)
for dev,tag in DEVICES:
    W,H=1280,720; im=sky(W,H)
    t="AD ARCADE"; px=15; text(im,t,(W-width(t,px))//2,26,px,GOLD,outline=INK,shadow=RED)
    sub="18 RETRO GAMES - "+dev; label(im,sub,(W-width(sub,5))//2,150,5)
    shots=[('menu','NEW MENU'),('ew_village','EMBERWOOD'),('siege','POCKET SIEGE'),('pbg20','EMBER PINBALL'),('ew_boss','BOSS FIGHT'),('flight','FLIGHT')]
    fw=330; gap=30; x0=(W-(3*(fw+16)+2*gap))//2
    for i,(n,cap) in enumerate(shots):
        f=frame(img(n),fw); x=x0+(i%3)*(fw+16+gap); y=212+(i//3)*(f.height+42)
        im.paste(f,(x,y)); label(im,cap,x+(fw+16-width(cap,3))//2,y+f.height+8,3,GOLD)
    v="V1.9"; label(im,v,W-width(v,4)-24,24,4,GOLD)
    im.save(os.path.join(HERE,'AD-Arcade-%scover-1280x720.png'%tag))
    S_=800; sq=sky(S_,S_); t="AD ARCADE"; px=11
    text(sq,t,(S_-width(t,px))//2,30,px,GOLD,outline=INK,shadow=RED)
    s2="18 RETRO GAMES"; label(sq,s2,(S_-width(s2,6))//2,122,6)
    for i,n in enumerate(['ew_village','siege','pbg20','menu']):
        f=frame(img(n),340); sq.paste(f,(30+(i%2)*(356+28),190+(i//2)*(f.height+24)))
    label(sq,dev,(S_-width(dev,6))//2,676,6); label(sq,"VERSION 1.9",(S_-width("VERSION 1.9",3))//2,748,3,GOLD)
    sq.save(os.path.join(HERE,'AD-Arcade-%scover-800x800.png'%tag))
print('ok')
