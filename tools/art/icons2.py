# Icones du menu v2 : JEUX = vrais pixels du jeu (captures du harnais, 1 ou 2 bandes recomposees)
#                     APPLIS = symboles nets (aplats, sans trame, contour epais)
# Sources : captures 240x135 du harnais (tools/hs) dans le dossier SRC (fichiers .ppm)
import os, sys, math
from PIL import Image, ImageDraw
SRC=os.environ.get('ICON_SRC',os.path.join(os.path.dirname(os.path.abspath(__file__)),'icon_src'))
def fr(n): return Image.open(os.path.join(SRC,n+'.ppm')).convert('RGB')
def band(img,x,y,h): return img.crop((x,y,x+64,y+h))
def stack(*bands):
    out=Image.new('RGB',(64,64)); y=0
    for b in bands: out.paste(b,(0,y)); y+=b.height
    return out
def paste_crop(dst,img,box,at): dst.paste(img.crop(box),at)

def game_icons():
    I={}
    m=fr('g02_2'); I[2]=stack(band(m,56,38,36),band(m,88,99,28))                       # meteores
    z=fr('g03_1'); ic=z.crop((0,0,64,64)); paste_crop(ic,z,(225,105,239,119),(46,46)); I[3]=ic   # labyrinthe + portail
    b=fr('g04_1'); I[4]=stack(band(b,60,14,30),band(b,88,99,34))                       # casse-briques
    v=fr('g05_1'); I[5]=stack(band(v,30,14,43),band(v,82,104,21))                      # invaders
    s1=fr('g06_1'); s2=fr('g06_2'); ic=s2.crop((88,8,152,72))
    paste_crop(ic,s1,(90,8,102,24),(2,8)); paste_crop(ic,s1,(130,8,142,24),(50,14)); I[6]=ic   # slalom + portes
    I[7]=fr('st_46').crop((84,36,148,100))                                              # stack
    I[8]=fr('g08_2').crop((90,48,154,112))                                              # course
    l=fr('g14_1'); I[14]=stack(band(l,100,14,44),band(l,168,78,20))                    # alunissage
    import pinball as pb                                                              # ember pinball : vrai art du plateau
    t=pb.table()
    for (x,y,r) in pb.BUMPERS: t.paste(pb.bumper(x==44),x-10,y-10)
    pb.flipper_preview(t,pb.FLIP_L,math.radians(10),True); pb.flipper_preview(t,pb.FLIP_R,math.radians(152),False)
    t.paste(pb.ball(),50,236)
    im=t.image(pb.PAL).convert('RGB')
    I[17]=stack(im.crop((28,80,92,128)),im.crop((28,250,92,266)))
    return I

# ---------------------------------------------------------------- applis : symboles nets
def canvas_(bg1,bg2):
    im=Image.new('RGB',(64,64),bg1); d=ImageDraw.Draw(im)
    for y in range(32,64): d.line([(0,y),(63,y)],fill=bg2)
    return im,d
K=(20,16,31)
def outline_box(d,box,fill,ol=K,w=2): d.rectangle(box,fill=ol); d.rectangle((box[0]+w,box[1]+w,box[2]-w,box[3]-w),fill=fill)
def star(d,cx,cy,r,fill,ol=K):
    pts=[]
    for i in range(10):
        a=math.radians(-90+i*36); rr=r if i%2==0 else r*0.45; pts.append((cx+math.cos(a)*rr,cy+math.sin(a)*rr))
    d.polygon(pts,fill=ol);
    pts2=[(cx+(x-cx)*0.78,cy+(y-cy)*0.78) for x,y in pts]; d.polygon(pts2,fill=fill)
def ic_daily():
    im,d=canvas_((46,120,140),(36,98,116))
    outline_box(d,(10,10,53,55),(240,232,214))
    d.rectangle((12,12,51,22),fill=(198,60,52)); d.line([(12,22),(51,22)],fill=K,width=2)
    for x in (19,31,43): d.rectangle((x-2,6,x+1,15),fill=K); d.rectangle((x-1,7,x,14),fill=(200,200,210))
    for gy in range(3):
        for gx in range(4): d.rectangle((15+gx*9,27+gy*8,20+gx*9,31+gy*8),fill=(205,195,175))
    star(d,40,42,13,(255,206,64))
    d.line([(31,38),(36,36)],fill=(255,250,220))
    return im
def pawn(d,cx,col,dark):
    d.ellipse((cx-9,14,cx+9,32),fill=K); d.ellipse((cx-7,16,cx+7,30),fill=col); d.ellipse((cx-4,18,cx-1,21),fill=(255,255,255))
    d.polygon([(cx-13,56),(cx-7,32),(cx+7,32),(cx+13,56)],fill=K); d.polygon([(cx-10,54),(cx-5,34),(cx+5,34),(cx+10,54)],fill=col)
    d.polygon([(cx+2,34),(cx+5,34),(cx+10,54),(cx+4,54)],fill=dark)
def ic_duo():
    im,d=canvas_((60,52,110),(48,40,92))
    pawn(d,17,(70,140,230),(40,90,170)); pawn(d,47,(230,80,70),(160,50,40))
    d.polygon([(34,12),(26,32),(32,32),(28,48),(40,26),(34,26),(38,12)],fill=K)
    d.polygon([(35,14),(28,30),(33,30),(30,44),(38,27),(33,27),(37,14)],fill=(255,214,72))
    return im
def ic_trophies():
    im,d=canvas_((150,40,46),(124,30,38))
    for i in range(12):
        a=math.radians(i*30); d.line([(32,26),(32+math.cos(a)*40,26+math.sin(a)*40)],fill=(170,56,58) if i%2 else (150,40,46),width=5)
    d.ellipse((6,12,22,30),outline=K,width=4); d.ellipse((42,12,58,30),outline=K,width=4)
    d.ellipse((8,14,20,28),outline=(255,196,60),width=2); d.ellipse((44,14,56,28),outline=(255,196,60),width=2)
    d.pieslice((14,0,50,44),0,180,fill=K); d.rectangle((14,6,50,22),fill=K)
    d.pieslice((16,2,48,42),0,180,fill=(255,196,60)); d.rectangle((16,8,48,22),fill=(255,196,60))
    d.rectangle((36,8,46,30),fill=(214,150,40)); d.rectangle((20,10,23,24),fill=(255,244,200))
    d.rectangle((28,40,36,48),fill=K); d.rectangle((30,40,34,48),fill=(214,150,40))
    d.rectangle((18,48,46,58),fill=K); d.rectangle((20,50,44,56),fill=(120,70,40)); d.rectangle((24,51,40,53),fill=(255,196,60))
    return im
def ic_stats():
    im,d=canvas_((236,228,210),(222,212,192))
    for y in (16,28,40): d.line([(6,y),(58,y)],fill=(200,190,170))
    for i,(h,c,dk) in enumerate(((16,(70,140,230),(40,90,170)),(28,(90,190,90),(50,130,60)),(22,(255,196,60),(200,140,40)),(38,(230,80,70),(160,50,40)))):
        x0=8+i*13; outline_box(d,(x0,54-h,x0+10,56),c); d.rectangle((x0+7,56-h,x0+8,54),fill=dk)
    d.line([(8,50),(56,50)],fill=K,width=2)
    pts=[(12,36),(25,26),(38,30),(54,10)]
    d.line(pts,fill=K,width=4); d.line(pts,fill=(255,255,255),width=2)
    d.polygon([(48,8),(58,6),(56,16)],fill=K); d.polygon([(50,9),(56,8),(55,13)],fill=(255,255,255))
    return im
def ic_music():
    im,d=canvas_((70,60,150),(56,46,124))
    for (cx,cy) in ((19,47),(45,41)):
        d.ellipse((cx-9,cy-6,cx+7,cy+6),fill=K); d.ellipse((cx-7,cy-4,cx+3,cy+3),fill=(60,56,80))
        d.rectangle((cx+4,cy-34,cx+8,cy),fill=K)
        d.ellipse((cx-5,cy-3,cx-2,cy-1),fill=(255,255,255))
    d.polygon([(23,13),(53,7),(53,15),(23,21)],fill=K)
    for (x,y) in ((8,12),(56,26),(10,30)):
        d.line([(x-3,y),(x+3,y)],fill=(255,214,72),width=1); d.line([(x,y-3),(x,y+3)],fill=(255,214,72),width=1)
    return im
def ic_skins():
    im,d=canvas_((236,228,210),(222,212,192))
    d.ellipse((4,8,58,56),fill=K); d.ellipse((6,10,56,54),fill=(190,130,70)); d.ellipse((36,36,46,46),fill=K); d.ellipse((38,38,44,44),fill=(222,212,192))
    d.ellipse((8,12,52,44),fill=(210,150,86))
    for (x,y,c) in ((16,20,(230,80,70)),(28,15,(255,196,60)),(41,20,(90,190,90)),(14,33,(70,140,230)),(26,40,(255,255,255))):
        d.ellipse((x-6,y-5,x+6,y+5),fill=K); d.ellipse((x-4,y-3,x+4,y+3),fill=c); d.point((x-2,y-1),fill=(255,255,255))
    d.line([(36,62),(60,38)],fill=K,width=6); d.line([(37,61),(59,39)],fill=(150,96,50),width=3)
    d.polygon([(30,62),(35,55),(40,60)],fill=(70,140,230))
    return im
def ic_settings():
    im,d=canvas_((54,60,78),(44,48,64))
    def gear(cx,cy,r,n,col,dk):
        pts=[]
        for i in range(n*2):
            a=i*math.pi/n; rr=r+4 if i%2==0 else r
            for da in (-0.18,0.18): pts.append((cx+math.cos(a+da)*rr,cy+math.sin(a+da)*rr))
        d.polygon(pts,fill=K)
        pts2=[(cx+(x-cx)*0.86,cy+(y-cy)*0.86) for x,y in pts]; d.polygon(pts2,fill=col)
        d.ellipse((cx-r*0.55,cy-r*0.55,cx+r*0.55,cy+r*0.55),fill=dk); d.ellipse((cx-r*0.3,cy-r*0.3,cx+r*0.3,cy+r*0.3),fill=K)
        d.arc((cx-r+3,cy-r+3,cx+r-3,cy+r-3),200,290,fill=(255,255,255),width=2)
    gear(25,27,15,8,(190,196,214),(130,136,160))
    gear(46,46,9,6,(255,196,60),(200,140,40))
    return im
APPS={18:ic_daily,19:ic_duo,20:ic_trophies,21:ic_stats,22:ic_music,23:ic_skins,24:ic_settings}   # (17 = Ember Pinball)
def all_icons():
    I=game_icons()
    for k,f in APPS.items(): I[k]=f()
    for k,im in I.items():                                          # liseré fin commun
        d=ImageDraw.Draw(im); d.rectangle((0,0,63,63),outline=(20,16,31))
    return I
