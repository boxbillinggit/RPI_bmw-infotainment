#!/bin/sh

cd gateway

mkdir build
cd build

echo "Install Dependices"

apt-get install make cmake autoconf gcc g++ libboost-program-options-dev libboost-thread-dev libboost-date-time-dev -y

echo "Configure Gateway"

cmake .. -DCMAKE_C_COMPILER=/usr/bin/gcc -DCMAKE_CXX_COMPILER=/usr/bin/g++

make && make install

echo "Install Success"