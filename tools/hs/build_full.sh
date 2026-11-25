#!/bin/bash
cd /home/claude/proj/m5arcade/tools/hs
SRC=../../src
g++ -std=c++17 -O1 -w -Iinc -o /tmp/sim_full harness3.cpp $(ls $SRC/*.cpp | grep -v main.cpp) 2>&1 | head -30
