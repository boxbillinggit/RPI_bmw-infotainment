install( 
  DIRECTORY	"${CMAKE_SOURCE_DIR}/html"
  DESTINATION	"/usr/share/${PROJECT_NAME}/html"
  PATTERN 	"CMakeLists.txt" EXCLUDE
)
