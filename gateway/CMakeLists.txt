cmake_minimum_required(VERSION 2.8.9)

# Project settings
set(PROJECT_NAME openbm-gateway)
set(CMAKE_MAJOR_VERSION 1)
set(CMAKE_MINOR_VERSION 0)
set(CMAKE_PATCH_VERSION 0)
set(SOURCES 
   main.cpp
   ApplicationClient.cpp
   Application.cpp
   IBus.cpp
   Log.cpp
   mongoose.cpp
)

project(${PROJECT_NAME})
add_executable(${PROJECT_NAME} ${SOURCES})

# install package
#set(CMAKE_INSTALL_PREFIX /usr)
install(TARGETS   ${PROJECT_NAME} 	DESTINATION /usr/bin)
install(DIRECTORY html/ 		DESTINATION "/usr/share/${PROJECT_NAME}/html")
install(FILES     openbm-gateway.conf	DESTINATION /etc/init)


# Boost libraries
set(BOOST_LIBRARYDIR /usr/local/lib/boost)
set(Boost_USE_STATIC_LIBS	ON)
set(Boost_USE_MULTITHREADED 	ON)
set(Boost_USE_STATIC_RUNTIME	OFF)

find_package(Boost 1.59.0 COMPONENTS date_time thread system program_options REQUIRED)

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


# Create .deb-package with cPack
# >>> make package
include(CPackConfig.cmake)
include(CPack)
