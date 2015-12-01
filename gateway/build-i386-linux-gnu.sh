#!/bin/bash

BUILD_PATH=build-i386-linux-gnu

# ---------------- Build ----------------
mkdir $BUILD_PATH
cd $BUILD_PATH
cmake ../
make


