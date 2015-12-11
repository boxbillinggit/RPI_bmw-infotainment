set( CMAKE_LIBRARY_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/../resources/lib" )
set( SOURCES 
   main.cpp
)


# Other
include_directories( "${CMAKE_SYSROOT}/usr/include" )
set( CMAKE_CXX_FLAGS "-Wall -Werror -Wno-write-strings" ) # http://linux.die.net/man/1/g++


# build an dynamic library with defined name
# TODO SHARED or MODULE? https://cmake.org/cmake/help/v3.4/command/add_library.html?highlight=shared
add_library( ${PROJECT_NAME} MODULE ${SOURCES} )

find_package( PythonLibs 2.7 REQUIRED )

if(PYTHONLIBS_FOUND)
  include_directories( ${PYTHON_INCLUDE_DIRS} )
endif()

