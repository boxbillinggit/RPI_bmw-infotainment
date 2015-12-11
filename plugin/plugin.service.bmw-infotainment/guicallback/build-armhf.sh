#!/bin/bash

ARCHITECTURE=armhf

# navigate to current directory
cd $( dirname ${BASH_SOURCE[0]} )

mkdir $ARCHITECTURE
cd $ARCHITECTURE
cmake -D CMAKE_TOOLCHAIN_FILE=/usr/local/build-env/rpi/arm-linux-gnueabihf.cmake ../ &&
make

