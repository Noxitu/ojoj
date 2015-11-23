#!/bin/bash

find -name '*.cpp' -exec dos2unix {} \;
find -name '*.py' -exec dos2unix {} \;

rm {daemon,tester}/*.pyc

g++ judge/ojoj_judge.cpp -o judge/ojoj_judge -O2
g++ judge/ojoj_entry_point.cpp -c -o judge/ojoj_entry_point.o -O2

cp judge/ojoj_judge tester/ojoj_judge
cp judge/ojoj_entry_point.o tester/languages/ojoj_entry_point.o

chmod +x tester/ojoj_judge
chmod +x tester/languages/c++.lang
chmod +x tester/tester.py
chmod +x daemon/daemon.py