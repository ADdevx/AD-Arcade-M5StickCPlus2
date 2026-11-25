#!/bin/bash
# Harnais PC sous Windows (Git Bash) : compilateur C++ = zig (pip install ziglang)
cd "$(dirname "$0")"
OUTEXE=${1:-sim_full.exe}
python -m ziglang c++ -std=c++17 -O1 -w -DZTEST -Iinc -o "$OUTEXE" harness3.cpp $(ls ../../src/*.cpp | grep -v main.cpp) 2>&1 | head -40
