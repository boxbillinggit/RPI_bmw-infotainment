#!/bin/bash

BUILD_PATH=i386-linux-gnu

mkdir $BUILD_PATH
cd $BUILD_PATH
cmake ../
make package


