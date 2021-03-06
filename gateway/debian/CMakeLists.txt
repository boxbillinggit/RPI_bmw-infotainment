# Files that should be configured and will be used by the debhelpers as input.
# In these files you can use @CMAKE_VARIABLES@ that will be filled out.
# We don't glob here because then CMake won't regenerate automatically when a file is added.
#
# Note that CPACK_PACKAGE_NAME is assumed to be lower-case at this point.
# If it isn't, you should lowercase it here (string( TOLOWER ...)) and the filenames,
# because that's how Debian wants it.
# (Alternatively, set and use a lowercase CPACK_DEBIAN_PACKAGE_NAME)
set( DH_INPUT
	${CPACK_PACKAGE_NAME}.init.in
	${CPACK_PACKAGE_NAME}.postinst.in
	${CPACK_PACKAGE_NAME}.postrm.in
)

# These files (generated by dhelpers) will be copied into the control-part of the deb.
# Files that end up in the filesystem normally (e.g. cron/init-scripts) must not be mentioned here.
# It's a good idea to add "conffiles", as the debhelpers may generate it.
set( DH_GENERATED_CONTROL_EXTRA
	postinst
	postrm
	prerm
	conffiles
)

# Set this to the debhelpers that should run (dh_prep and dh_installdeb need not be listed here).
set( DH_RUN
	dh_installinit
)

# At this point, CMakeDebHelper must be included (add .cmake if you have it in this directory)
include( CMakeDebHelper )

set( CPACK_GENERATOR ${CPACK_GENERATOR} "DEB" PARENT_SCOPE )

# "PROJECT_TARGET_ARCHITECTURE" is a custom variable ans is defined in toolset-file -or from command-line (-D )
set( CPACK_DEBIAN_PACKAGE_ARCHITECTURE "${PROJECT_TARGET_ARCHITECTURE}" PARENT_SCOPE )

