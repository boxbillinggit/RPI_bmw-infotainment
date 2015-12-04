# ref: https://cmake.org/Wiki/CMake:Packaging_With_CPack

# https://nowardev.wordpress.com/2009/12/27/how-to-create-a-debian-package-for-script-and-for-project-that-use-cmake/


# http://git.one-infiniteloop.com/larsa/bmw-infotainment/blob/6d8699d4282672d22021673cd60e61176cd1e29f/gateway/nbproject/Package-Release.bash#L106

# DEBUG: list installed files in package: dpkg-deb --contents openbm-gateway-1.0.0-Linux.deb

set(CPACK_GENERATOR "DEB")

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
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY 	"OpenBM Gateway makes a connection between IBus hardware connected to
					 serialport and TCP/IP connected clients.")



