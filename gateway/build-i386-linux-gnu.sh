#!/bin/bash

BUILD_PATH=i386-linux-gnu

mkdir $BUILD_PATH
cd $BUILD_PATH
cmake -D PROJECT_TARGET_ARCHITECTURE=i386 ../ &&
make package


