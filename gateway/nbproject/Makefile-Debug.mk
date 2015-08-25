#
# Generated Makefile - do not edit!
#
# Edit the Makefile in the project folder instead (../Makefile). Each target
# has a -pre and a -post target defined where you can add customized code.
#
# This makefile implements configuration specific macros and targets.


# Environment
MKDIR=mkdir
CP=cp
GREP=grep
NM=nm
CCADMIN=CCadmin
RANLIB=ranlib
CC=gcc
CCC=g++
CXX=g++
FC=gfortran
AS=as

# Macros
CND_PLATFORM=GNU-Linux-x86
CND_DLIB_EXT=so
CND_CONF=Debug
CND_DISTDIR=dist
CND_BUILDDIR=build

# Include project Makefile
include Makefile

# Object Directory
OBJECTDIR=${CND_BUILDDIR}/${CND_CONF}/${CND_PLATFORM}

# Object Files
OBJECTFILES= \
	${OBJECTDIR}/Application.o \
	${OBJECTDIR}/ApplicationClient.o \
	${OBJECTDIR}/IBus.o \
	${OBJECTDIR}/Log.o \
	${OBJECTDIR}/main.o \
	${OBJECTDIR}/mongoose.o


# C Compiler Flags
CFLAGS=

# CC Compiler Flags
CCFLAGS=-g -rdynamic -pthread
CXXFLAGS=-g -rdynamic -pthread

# Fortran Compiler Flags
FFLAGS=

# Assembler Flags
ASFLAGS=

# Link Libraries and Options
LDLIBSOPTIONS=/usr/lib/libboost_date_time.a /usr/lib/libboost_system-mt.a /usr/lib/libboost_thread-mt.a /usr/lib/libboost_program_options-mt.a -ldl

# Build Targets
.build-conf: ${BUILD_SUBPROJECTS}
	"${MAKE}"  -f nbproject/Makefile-${CND_CONF}.mk ${CND_DISTDIR}/${CND_CONF}/${CND_PLATFORM}/gateway

${CND_DISTDIR}/${CND_CONF}/${CND_PLATFORM}/gateway: /usr/lib/libboost_date_time.a

${CND_DISTDIR}/${CND_CONF}/${CND_PLATFORM}/gateway: /usr/lib/libboost_system-mt.a

${CND_DISTDIR}/${CND_CONF}/${CND_PLATFORM}/gateway: /usr/lib/libboost_thread-mt.a

${CND_DISTDIR}/${CND_CONF}/${CND_PLATFORM}/gateway: /usr/lib/libboost_program_options-mt.a

${CND_DISTDIR}/${CND_CONF}/${CND_PLATFORM}/gateway: ${OBJECTFILES}
	${MKDIR} -p ${CND_DISTDIR}/${CND_CONF}/${CND_PLATFORM}
	${LINK.cc} -o ${CND_DISTDIR}/${CND_CONF}/${CND_PLATFORM}/gateway ${OBJECTFILES} ${LDLIBSOPTIONS}

${OBJECTDIR}/Application.o: Application.cpp 
	${MKDIR} -p ${OBJECTDIR}
	${RM} "$@.d"
	$(COMPILE.cc) -O2 -Wall -MMD -MP -MF "$@.d" -o ${OBJECTDIR}/Application.o Application.cpp

${OBJECTDIR}/ApplicationClient.o: ApplicationClient.cpp 
	${MKDIR} -p ${OBJECTDIR}
	${RM} "$@.d"
	$(COMPILE.cc) -O2 -Wall -MMD -MP -MF "$@.d" -o ${OBJECTDIR}/ApplicationClient.o ApplicationClient.cpp

${OBJECTDIR}/IBus.o: IBus.cpp 
	${MKDIR} -p ${OBJECTDIR}
	${RM} "$@.d"
	$(COMPILE.cc) -O2 -Wall -MMD -MP -MF "$@.d" -o ${OBJECTDIR}/IBus.o IBus.cpp

${OBJECTDIR}/Log.o: Log.cpp 
	${MKDIR} -p ${OBJECTDIR}
	${RM} "$@.d"
	$(COMPILE.cc) -O2 -Wall -MMD -MP -MF "$@.d" -o ${OBJECTDIR}/Log.o Log.cpp

${OBJECTDIR}/main.o: main.cpp 
	${MKDIR} -p ${OBJECTDIR}
	${RM} "$@.d"
	$(COMPILE.cc) -O2 -Wall -MMD -MP -MF "$@.d" -o ${OBJECTDIR}/main.o main.cpp

${OBJECTDIR}/mongoose.o: mongoose.c 
	${MKDIR} -p ${OBJECTDIR}
	${RM} "$@.d"
	$(COMPILE.c) -g -Werror -MMD -MP -MF "$@.d" -o ${OBJECTDIR}/mongoose.o mongoose.c

# Subprojects
.build-subprojects:

# Clean Targets
.clean-conf: ${CLEAN_SUBPROJECTS}
	${RM} -r ${CND_BUILDDIR}/${CND_CONF}
	${RM} ${CND_DISTDIR}/${CND_CONF}/${CND_PLATFORM}/gateway

# Subprojects
.clean-subprojects:

# Enable dependency checking
.dep.inc: .depcheck-impl

include .dep.inc
