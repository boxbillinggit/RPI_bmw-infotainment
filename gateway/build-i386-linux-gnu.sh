#!/bin/bash

ARCHITECTURE=i386

# navigate to current directory
cd $( dirname ${BASH_SOURCE[0]} )

mkdir $ARCHITECTURE
cd $ARCHITECTURE
cmake -D PROJECT_TARGET_ARCHITECTURE=$ARCHITECTURE ../ &&
make package


