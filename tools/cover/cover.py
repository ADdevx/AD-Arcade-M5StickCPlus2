import sys; sys.path.insert(0,'/tmp/cov')
from mk import *
W,H=1280,720
im=sky(W,H)
t="AD ARCADE"; px=16; w=width(t,px)
text(im,t,(W-w)//2,36,px,(214,162,72),outline=(10,14,13),shadow=(156,46,48))
sub="15 RETRO GAMES - M5STICKC PLUS2"; p2=5; text(im,sub,(W-width(sub,p2))//2,168,p2,(212,222,200),outline=(10,14,13),shadow=(27,41,37))
names=['menu','g2','g10','g9','g5','skins']
fw=330; gap=30; x0=(W-(3*(fw+16)+2*gap))//2
for i,n in enumerate(names):
    f=frame(load(n),fw); x=x0+(i%3)*(fw+16+gap); y=232+(i//3)*(f.height+18)
    im.paste(f,(x,y))
im.save('/tmp/cov/AD-Arcade-cover-1280x720.png')
# square
S=800; sq=sky(S,S); t="AD ARCADE"; px=11
text(sq,t,(S-width(t,px))//2,40,px,(214,162,72),outline=(10,14,13),shadow=(156,46,48))
s2="15 RETRO GAMES"; text(sq,s2,(S-width(s2,6))//2,130,6,(212,222,200),outline=(10,14,13),shadow=(27,41,37))
for i,n in enumerate(['g2','g10','g9','g5']):
    f=frame(load(n),340); sq.paste(f,(30+(i%2)*(356+28),200+(i//2)*(f.height+18)))
s3="M5STICKC PLUS2"; text(sq,s3,(S-width(s3,6))//2,690,6,(212,222,200),outline=(10,14,13),shadow=(27,41,37))
sq.save('/tmp/cov/AD-Arcade-cover-800x800.png')
