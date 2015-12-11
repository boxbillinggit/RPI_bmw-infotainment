cmake_minimum_required(VERSION 2.8.12)

# General project settings
project( guicallback )
set( CMAKE_LIBRARY_OUTPUT_DIRECTORY "../../" )
set( SOURCES 
   main.cpp
)


find_package( PythonLibs 2.7 REQUIRED )

if(PYTHONLIBS_FOUND)
  include_directories( ${PYTHON_INCLUDE_DIRS} )
endif()


# build an dynamic library with defined name
# TODO SHARED or MODULE? https://cmake.org/cmake/help/v3.4/command/add_library.html?highlight=shared
add_library( ${PROJECT_NAME} MODULE ${SOURCES} )

include_directories( "${CMAKE_SYSROOT}/usr/include" )

# http://linux.die.net/man/1/g++
set( CMAKE_CXX_FLAGS "-Wall -Werror -Wno-write-strings" )

