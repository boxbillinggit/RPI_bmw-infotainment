# get current version "cmake --version"
cmake_minimum_required(VERSION 2.8.12)

# Project settings
set(PROJECT_NAME bmwaddon)
set(SOURCES 
   main.cpp
)

project(${PROJECT_NAME})

# Python related
#set(PYTHON_LIBRARY /usr/lib/i386-linux-gnu/libpython2.7.so)
#set(PYTHON_INCLUDE_DIR /usr/include/python2.7)

find_package(PythonLibs 2.7 REQUIRED)

if(PYTHONLIBS_FOUND)
  include_directories(${PYTHON_INCLUDE_DIRS})
endif()

# TODO set prefix (.so for Linux, .pyd for Windows)
#set_target_properties(${PROJECT_NAME} PROPERTIES SUFFIX ".pyd")

# build an dynamic library with defined name
# TODO SHARED or MODULE? https://cmake.org/cmake/help/v3.4/command/add_library.html?highlight=shared
add_library(${PROJECT_NAME} SHARED ${SOURCES})

# http://linux.die.net/man/1/g++
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Werror -Wno-write-strings")

