#!/bin/sh

mkdir build
cd build

echo "Install Dependices"

apt-get install make cmake autoconf gcc g++ libboost-program-options-dev libboost-thread-dev libboost-date-time-dev -y

echo "Configure Gateway"

cmake .. -DCMAKE_C_COMPILER=/usr/bin/gcc -DCMAKE_CXX_COMPILER=/usr/bin/g++

make && make install

echo "Install Success"

sleep 5

cd ..

echo "Create And Copy Service"

mkdir /etc/ibus/

cp -p config.conf /etc/ibus/config.conf

cp -p ibus.sh /etc/init.d/ibus && chmod +x /etc/init.d/ibus