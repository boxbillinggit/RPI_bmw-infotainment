cmake_minimum_required(VERSION 2.8.9)

# General project settings
project( openbm-gateway )
set(CMAKE_MAJOR_VERSION 1)
set(CMAKE_MINOR_VERSION 0)
set(CMAKE_PATCH_VERSION 0)

# General CPack-settings
set( CPACK_SYSTEM_NAME 		 "${PROJECT_TARGET_ARCHITECTURE}" )
set( CPACK_PACKAGE_NAME 	 "${PROJECT_NAME}" )
set( CPACK_PACKAGE_VERSION_MAJOR "${CMAKE_MAJOR_VERSION}" )
set( CPACK_PACKAGE_VERSION_MINOR "${CMAKE_MINOR_VERSION}" )
set( CPACK_PACKAGE_VERSION_PATCH "${CMAKE_PATCH_VERSION}" )
set( CMAKE_MODULE_PATH 		 "${CMAKE_SOURCE_DIR}/cmake-debhelper" )

# Detailed CPack-settings
set(CPACK_PACKAGE_VENDOR 		"One Infinite Loop")
set(CPACK_PACKAGE_CONTACT 		"lars.gunnarsson@one-infiniteloop.com")
set(CPACK_PACKAGE_DESCRIPTION 		"OpenBM Gateway")
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY 	"OpenBM Gateway makes a connection between IBus hardware connected to serialport and TCP/IP connected clients.")

# Includes & modules
add_subdirectory( src )
add_subdirectory( html )
add_subdirectory( debian )

include( CPack )



