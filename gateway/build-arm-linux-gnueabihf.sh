#!/bin/bash

BUILD_PATH=build-arm-linux-gnueabihf

# ---------------- Build ----------------
mkdir $BUILD_PATH
cd $BUILD_PATH
cmake -D CMAKE_TOOLCHAIN_FILE=/usr/local/build-env/rpi/arm-linux-gnueabihf.cmake ../
make package

