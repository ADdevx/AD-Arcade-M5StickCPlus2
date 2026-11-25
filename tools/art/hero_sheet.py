from humans import *
import sys
def sheet(rows,scale=4,labels=None,pal=None,bg=(34,28,48),pad=3,cw=None,ch=None):
    import sys,os; sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','cover')); import mk
    cw=cw or max(max(s.w for s in r) for r in rows)+pad*2; ch=ch or max(max(s.h for s in r) for r in rows)+pad*2
    W=max(len(r) for r in rows)*cw; Hh=len(rows)*ch
    im=Image.new('RGBA',(W,Hh),bg+(255,))
    for ry,r in enumerate(rows):
        for rx,sp in enumerate(r):
            im.alpha_composite(sp.image(pal),(rx*cw+pad,ry*ch+pad))
    return im.resize((W*scale,Hh*scale),Image.NEAREST)
if __name__=='__main__':
    rows=[[human(d,f,HERO) for f in range(4)] for d in('down','up','right','left')]
    flat=[[r[i] for r in rows[:2] for i in range(4)],[r[i] for r in rows[2:] for i in range(4)]]
    sheet(flat).convert('RGB').save('/tmp/zel2/t_hero.png')
