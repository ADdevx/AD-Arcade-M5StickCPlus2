import sys,glob,os
from PIL import Image,ImageDraw,ImageFont
d=sys.argv[1]
F={0:8,2:14,4:24,8:60,9:9,10:15}
for p in sorted(glob.glob(d+'/*.ppm')):
    im=Image.open(p).convert('RGB'); S=3; im=im.resize((240*S,135*S),Image.NEAREST); dr=ImageDraw.Draw(im)
    for l in open(p[:-4]+'.txt'):
        x,y,f,sz,dt,col,s=l.rstrip('\n').split('\t',6)
        x,y,f,sz,dt,col=int(x),int(y),int(f),float(sz),int(dt),int(col)
        px=int(F[f]*sz*S*0.95); font=ImageFont.truetype(('C:/Windows/Fonts/arialbd.ttf' if f>=2 and f!=10 else 'C:/Windows/Fonts/consola.ttf') if os.name=='nt' else ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if f>=2 and f!=10 else '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'),px)
        w=dr.textlength(s,font=font); X=x*S-(0 if dt==0 else (w/2 if dt==1 else w))
        c=((col>>11)&31)<<3,((col>>5)&63)<<2,(col&31)<<3
        dr.text((X,y*S),s,font=font,fill=c)
    im.save(p[:-4]+'.png')
