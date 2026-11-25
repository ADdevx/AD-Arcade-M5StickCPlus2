from scene import *
def up(im,sc=4): return im.convert('RGB').resize((im.width*sc,im.height*sc),Image.NEAREST)
up(compose(2,'day')).save('/tmp/zel2/F_village_day.png')
up(compose(3,'day',dialog=["MERCHANT","WELCOME TRAVELLER! THE FOREST","IS DANGEROUS. TAKE THIS SWORD."],hero_x=132)).save('/tmp/zel2/F_village_dialogue.png')
up(compose(5,'dusk')).save('/tmp/zel2/F_village_dusk.png')
fr=[up(compose(t,'day'),3) for t in range(16)]
fr[0].save('/tmp/zel2/village.gif',save_all=True,append_images=fr[1:],duration=110,loop=0)
