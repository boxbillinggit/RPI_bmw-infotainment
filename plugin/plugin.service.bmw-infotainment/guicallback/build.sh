#!/bin/bash

BUILD_PATH=build-all-targets

# ---------------- Build ----------------
mkdir $BUILD_PATH
cd $BUILD_PATH
cmake ../
make


