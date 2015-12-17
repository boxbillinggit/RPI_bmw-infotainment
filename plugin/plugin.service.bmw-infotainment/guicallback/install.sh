#!/bin/sh

mkdir build
cd build

echo "Install Dependices"

apt-get install python-dev gcc g++ libboost-program-options-dev libboost-thread-dev libboost-date-time-dev -y

echo "Configure Plugin"

cmake .. -DCMAKE_C_COMPILER=/usr/bin/gcc -DCMAKE_CXX_COMPILER=/usr/bin/g++

make

echo "Install Success You Must Copy Category plugin.service.bmw-infotainment to Addons Kodi."