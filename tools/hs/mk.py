import sys,subprocess,os
g,script=sys.argv[1],sys.argv[2]
S=os.path.dirname(os.path.abspath(__file__))
src=['harness.cpp','../../../../../../../home/claude/m5arcade/src/tilt.cpp','/home/claude/m5arcade/src/%s.cpp'%g]
cmd=['g++','-std=c++17','-O1','-w','-I%s/inc'%S,'-DGAME=%s'%g,'-o','%s/sim_%s'%(S,g),'%s/harness.cpp'%S,'/home/claude/m5arcade/src/tilt.cpp','/home/claude/m5arcade/src/%s.cpp'%g]
r=subprocess.run(cmd,capture_output=True,text=True); print(r.stderr[:3000])
