# fetch Git info (TODO: generate changelog instead)
execute_process(COMMAND git show -s --format=%ci\ @%h OUTPUT_VARIABLE GIT_COMMIT)

# Inherited from CMakeLists.txt
set(CPACK_PACKAGE_NAME 		${PROJECT_NAME})
set(CPACK_PACKAGE_VERSION_MAJOR ${CMAKE_MAJOR_VERSION})
set(CPACK_PACKAGE_VERSION_MINOR ${CMAKE_MINOR_VERSION})
set(CPACK_PACKAGE_VERSION_PATCH ${CMAKE_PATCH_VERSION})

# Debian Package info
set(CPACK_PACKAGE_VENDOR 		"One Infinite Loop")
set(CPACK_PACKAGE_CONTACT 		"lars.gunnarsson@one-infiniteloop.com")
set(CPACK_RESOURCE_FILE_LICENSE 	"${CMAKE_CURRENT_SOURCE_DIR}/COPYING.txt")
set(CPACK_PACKAGE_DESCRIPTION_FILE 	"${CMAKE_CURRENT_SOURCE_DIR}/readme.md")
set(CPACK_PACKAGE_DESCRIPTION 		"OpenBM Gateway")
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY 	"OpenBM Gateway makes a connection between IBus hardware connected to serialport and TCP/IP connected clients. Commit: ${GIT_COMMIT}")

# CPack utilities
set(CPACK_GENERATOR "DEB")
include(CPack)

# DEBUG: list installed files in package: dpkg-deb --contents openbm-gateway-1.0.0-Linux.deb
# ref: 	https://cmake.org/Wiki/CMake:Packaging_With_CPack

