set( SOURCES 
   main.cpp
   ApplicationClient.cpp
   Application.cpp
   IBus.cpp
   Log.cpp
   mongoose.cpp
)

add_executable( ${PROJECT_NAME} ${SOURCES} )

install(
   TARGETS	"${PROJECT_NAME}"
   DESTINATION	"/usr/bin"
)


# Dependencies Boost libraries
set(BOOST_LIBRARYDIR /usr/local/lib/boost)
set(Boost_USE_STATIC_LIBS	ON)
set(Boost_USE_MULTITHREADED 	ON)
set(Boost_USE_STATIC_RUNTIME	OFF)

find_package(Boost 1.59.0 COMPONENTS date_time thread system program_options REQUIRED)

if(Boost_FOUND)
  include_directories( ${Boost_INCLUDE_DIRS} )
  target_link_libraries( ${PROJECT_NAME} ${Boost_LIBRARIES} )
endif()


# Detailed project-settings 
# other stuff (http://stackoverflow.com/a/986584)
add_definitions( "-D__STDC_LIMIT_MACROS" ) 
target_link_libraries( ${PROJECT_NAME} dl rt pthread )
set( CMAKE_CXX_FLAGS "-Wall -Werror" )


