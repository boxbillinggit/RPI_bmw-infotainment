# get current version "cmake --version"
cmake_minimum_required(VERSION 2.8.9)

# Project settings
set(PROJECT_NAME gateway)
set(SOURCES 
   main.cpp
   ApplicationClient.cpp
   Application.cpp
   IBus.cpp
   Log.cpp
   mongoose.cpp
)

project(${PROJECT_NAME})

# search only for static libs ending with .a
set(Boost_USE_STATIC_LIBS	ON)
set(Boost_USE_MULTITHREADED 	ON)
set(Boost_USE_STATIC_RUNTIME	OFF)

# give a hint to "find_package" where to find boost (with prefix from CMAKE_FIND_ROOT_PATH)
set(BOOST_LIBRARYDIR /usr/local/lib/boost)

# required boost components for this project
find_package(Boost 1.59.0 COMPONENTS date_time thread system program_options REQUIRED)

# build an executable with defined name
add_executable(${PROJECT_NAME} ${SOURCES})

if(Boost_FOUND)
  include_directories(${Boost_INCLUDE_DIRS})
  target_link_libraries(${PROJECT_NAME} ${Boost_LIBRARIES})
endif()

# other stuff
target_link_libraries(${PROJECT_NAME} dl rt pthread)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Werror")

# http://www.duskborn.com/running-your-first-job-on-the-raspberry-pi-2-jenkins/
# http://stackoverflow.com/a/986584
add_definitions(-D__STDC_LIMIT_MACROS) 
