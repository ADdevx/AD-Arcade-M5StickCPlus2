import os, sys
from crypt_sheets import rows_sheet, label, OUT
from boss import *
def sheet_golem():
    return rows_sheet([
     ('PHASE 1 DORMANT/AWAKE (MOSS, RUNE PLATE) : SLEEP / IDLE x4 / WALK x4',[('SLEEP',golem('idle',0,0))]+[('IDLE %d'%k,golem('idle',k,1)) for k in range(4)]+[('WALK %d'%k,golem('walk',k,1)) for k in range(4)]),
     ('PHASE 2 ENRAGED (CORE EXPOSED) : WALK x2 / SLAM WINDUP x2 / SLAM / HURT FLASH / STAGGER',[('WALK %d'%k,golem('walk',k,2)) for k in range(2)]+[('WINDUP %d'%k,golem('windup',k,2)) for k in range(2)]+[('SLAM',golem('slam',0,2)),('HURT',golem('hurt',0,2)),('STAGGER',golem('stagger',0,2))]),
     ('PHASE 3 BREAKING (ORBITING SHARDS) : IDLE x2 / THROW x2 / STAGGER / DEATH x4',[('IDLE %d'%k,golem('idle',k,3)) for k in range(2)]+[('THROW A',golem('throw0',0,3)),('THROW B',golem('throw1',1,3)),('STAGGER',golem('stagger',1,3))]+[('DEATH %d'%k,death(k)) for k in range(4)]),
    ],sc=3,pal=ARENA)
def sheet_parts():
    return rows_sheet([
     ('ARTICULATED PARTS (PHASE 1 / 2 / 3) : TORSO, HEAD, SHOULDER, FIST, LEG',[('TORSO %d'%p,g_torso(p,0)) for p in (1,2,3)]+[('HEAD %d'%p,g_head(p,0)) for p in (1,2,3)]+[('SHOULDER %d'%p,g_shoulder(p,0)) for p in (1,2,3)]+[('FIST %d'%p,g_fist(p,0)) for p in (1,2,3)]+[('LEG %d'%p,g_leg(p,0)) for p in (1,2,3)]),
     ('ATTACK FX : SHOCKWAVE x4 / FIRE ERUPTION x4 / BOULDER x4 / TRAIL x2 / EMBERS',[('SHOCK %d'%k,shockwave(k)) for k in range(4)]+[('ERUPT %d'%k,eruption(k)) for k in range(4)]+[('ROCK %d'%k,boulder(k)) for k in range(4)]+[('TRAIL %d'%k,fire_trail(k)) for k in range(2)]+[('EMBER %d'%k,ember(k)) for k in range(4)]),
     ('ARENA : BASALT FLOOR x4 / BASALT WALL x2 / RUNE CIRCLE x4 / REWARD / BOSS BAR',[('FLOOR %d'%v,basalt_floor(v)) for v in range(4)]+[('WALL %d'%v,basalt_face(v)) for v in range(2)]+[('RUNES %d'%k,rune_circle(k)) for k in range(4)]+[('HEART %d'%k,heart_container(k)) for k in range(2)]+[('BOSS BAR',boss_bar(0.6))]),
     ('LAVA : CORNER AUTO-TILING (16 TILES x 4 FRAMES)',[('LAVA %02d'%m,lava_c(m,0)) for m in range(16)]),
    ],pal=ARENA)
if __name__=='__main__':
    sheet_golem().convert('RGB').save(f'{OUT}/P_boss_golem.png')
    sheet_parts().convert('RGB').save(f'{OUT}/Q_boss_parts_arena.png')
    print('ok')
