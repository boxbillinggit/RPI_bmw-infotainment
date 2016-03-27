#!/bin/sh

mkdir build
cd build

echo "Install Dependices"

apt-get install python-dev gcc g++ libboost-program-options-dev libboost-thread-dev libboost-date-time-dev -y

echo "Configure Plugin"

cmake .. -DCMAKE_C_COMPILER=/usr/bin/gcc -DCMAKE_CXX_COMPILER=/usr/bin/g++

make

cd ..

echo "Install GPIO Controller"

wget https://pypi.python.org/packages/source/R/RPi.GPIO/RPi.GPIO-0.6.2.tar.gz
tar -xvf RPi.GPIO-0.6.2.tar.gz
cd RPi.GPIO-0.6.2
sudo python setup.py install
cd ..
sudo rm -rf RPi.GPIO-0.*

echo "Install Success You Must Copy Category plugin.service.bmw-infotainment to Addons Kodi."
