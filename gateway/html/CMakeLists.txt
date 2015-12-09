install( 
  DIRECTORY	"${CMAKE_SOURCE_DIR}/html"
  DESTINATION	"/usr/share/${PROJECT_NAME}"
  PATTERN 	"CMakeLists.txt" EXCLUDE
)
