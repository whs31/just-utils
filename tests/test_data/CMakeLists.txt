cmake_minimum_required(VERSION 3.15.0)

include_guard(GLOBAL)

project(rolly 
  VERSION 2.8.12
  DESCRIPTION "Radar open-source library"
  HOMEPAGE_URL "whs31.github.io/rolly"
  LANGUAGES C CXX
)

option(CORONA_TEST "Build tests" OFF)
option(CORONA_WITH_RPATH "Use deploy RPATH" ON)
option(CORONA_WITH_NEURAL "Build neural network plugin" OFF)
option(CORONA_WITH_WATERMARK "Apply watermark" OFF)

set(CMAKE_POLICY_VERSION_MINIMUM 3.5) #todo: migrate to new cmake version recursively and remove this

if (MSVC)
  set(CORONA_BINARY_DIR "${CMAKE_BINARY_DIR}/bin/$<CONFIG>")
  set(CORONA_PLUGINS_DIR "${CORONA_BINARY_DIR}/plugins")
else ()
  set(CORONA_BINARY_DIR "${CMAKE_BINARY_DIR}/bin")
  set(CORONA_PLUGINS_DIR "${CORONA_BINARY_DIR}/plugins")
endif ()

set(PROJECT_NAMESPACE "quasar::")
set(PROJECT_FULL_NAME "${PROJECT_NAMESPACE}${PROJECT_NAME}")

message(STATUS "[${PROJECT_FULL_NAME}] version ${PROJECT_VERSION}")
message(STATUS "[${PROJECT_FULL_NAME}] tests: ${CORONA_TEST}")

if ("${CMAKE_GENERATOR}" MATCHES "^Visual Studio")
  set(CMAKE_GENERATOR_PLATFORM "x64" CACHE STRING "" FORCE)
endif ()

set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_INCLUDE_CURRENT_DIR ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set_property(GLOBAL PROPERTY USE_FOLDERS ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake" ${CMAKE_MODULE_PATH})

if (NOT MSVC)
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fcoroutines")
endif ()

include(FetchContent)
include(GenerateProtobufs)
include(GenerateProtobufsAndGRPC)
include(EmbedJSON)

find_package(mms.api REQUIRED)
find_package(quasar-api REQUIRED)
find_package(imgui REQUIRED)
find_package(implot REQUIRED)
find_package(frozen REQUIRED)
find_package(protobuf REQUIRED)
find_package(asio REQUIRED)
find_package(gRPC REQUIRED)
find_package(asio-grpc REQUIRED)
find_package(nlohmann_json REQUIRED)
find_package(Taskflow REQUIRED)
find_package(Qt6 REQUIRED
  COMPONENTS
  Core
  Gui
  Location
  Positioning
  Network
  ShaderTools
  Widgets
)

add_subdirectory(modules)

qt_add_library(${PROJECT_NAME} SHARED)
add_library(${PROJECT_FULL_NAME} ALIAS ${PROJECT_NAME})

add_subdirectory(plugins)
add_subdirectory(bin)
add_dependencies(${PROJECT_NAME} "corona-bin")

generate_protobufs(
  INPUT_DIR "${CMAKE_CURRENT_BINARY_DIR}/quasar.protobufs"
  OUTPUT_DIR "${CMAKE_CURRENT_BINARY_DIR}/generated"
  INCLUDE_DIR "${CMAKE_CURRENT_BINARY_DIR}/generated"
  TARGET_NAME "quasar.protobufs_gen"
  TARGET_ALIAS "quasar::protobufs_gen"
  GRPC
  GRPC_INPUT_DIR "${CMAKE_CURRENT_BINARY_DIR}/quasar.protobufs/quasar/relay/services"
)

add_protobufs(
  INPUT_DIR "${CMAKE_CURRENT_SOURCE_DIR}/share/proto"
  OUTPUT_DIR "${CMAKE_CURRENT_BINARY_DIR}/generated"
  TARGET_NAME "corona.protobufs"
  TARGET_ALIAS "quasar::corona::protobufs"
  IMPORT_PATHS "${CMAKE_CURRENT_BINARY_DIR}/quasar.protobufs"
)

mms_embed_yaml(
  ${PROJECT_NAME}-meta
  FILE "${CMAKE_CURRENT_SOURCE_DIR}/meta/meta.yml"
  NAMESPACE "corona::embedded::yml"
)
add_library("quasar::corona::meta" ALIAS ${PROJECT_NAME}-meta)

mms_embed_yaml(
  ${PROJECT_NAME}-licenses
  FILE "${CMAKE_CURRENT_SOURCE_DIR}/meta/licenses.yml"
  NAMESPACE "corona::embedded::yml"
)
add_library("quasar::corona::licenses" ALIAS ${PROJECT_NAME}-licenses)

mms_embed_yaml(
  ${PROJECT_NAME}-settings
  FILE "${CMAKE_CURRENT_SOURCE_DIR}/meta/settings.yml"
  NAMESPACE "corona::embedded::yml"
)
add_library("quasar::corona::settings" ALIAS ${PROJECT_NAME}-settings)

if (CORONA_TEST)
  message(STATUS "[${PROJECT_FULL_NAME}] building tests")
  add_subdirectory(tests)
endif ()

set_target_properties(${PROJECT_NAME} PROPERTIES
  CXX_STANDARD 23
  CXX_STANDARD_REQUIRED ON
  CXX_EXTENSIONS OFF
)

if (CORONA_WITH_RPATH)
  set_target_properties(${PROJECT_NAME} PROPERTIES
    INSTALL_RPATH "$ORIGIN;$ORIGIN/..;$ORIGIN/lib"
    BUILD_WITH_INSTALL_RPATH TRUE
  )
endif ()

add_subdirectory(src)

target_link_libraries(${PROJECT_NAME}
  PUBLIC
  quasar::corona::datagrams

  mms::api
  quasar::api
  asio::asio
  nlohmann_json::nlohmann_json
  Qt6::Core
  Qt6::Gui
  Qt6::Positioning
  Qt6::Network

  PRIVATE
  quasar::protobufs_gen
  quasar::protobufs_gen_grpc
  quasar::corona::protobufs
  quasar::corona::meta
  quasar::corona::settings
  quasar::corona::licenses
  quasar::corona::atti

  protobuf::protobuf
  protobuf::libprotobuf
  protobuf::libprotoc

  gRPC::grpc
  gRPC::grpc++
  asio-grpc::asio-grpc

  imgui::imgui
  implot::implot
  Taskflow::Taskflow

  Qt6::Location
)

target_include_directories(${PROJECT_NAME}
  PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
  PRIVATE
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src>
)

message(STATUS "[${PROJECT_FULL_NAME}] adding shared export symbols: CORONA_API_LIBRARY")
target_compile_definitions(${PROJECT_NAME} PUBLIC -DCORONA_API_LIBRARY=1 -D_WIN32_WINNT=0x0601)
if (CORONA_WITH_WATERMARK)
  target_compile_definitions(${PROJECT_NAME} PUBLIC -DCORONA_WATERMARK_ENABLED=1)
else ()
  target_compile_definitions(${PROJECT_NAME} PUBLIC -DCORONA_WATERMARK_DISABLED=1)
endif ()

add_custom_command(TARGET ${PROJECT_NAME}
  POST_BUILD
  COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:${PROJECT_NAME}> ${CORONA_PLUGINS_DIR}
  COMMAND_EXPAND_LISTS
)

if (WIN32)
  set_target_properties(${PROJECT_NAME} PROPERTIES PREFIX "")
else ()
  message(STATUS "[${PROJECT_FULL_NAME}] copying ${CMAKE_CURRENT_BINARY_DIR}/compile_commands.json to the root folder ${CMAKE_CURRENT_SOURCE_DIR}")
  file(CREATE_LINK
    ${CMAKE_CURRENT_BINARY_DIR}/compile_commands.json
    ${CMAKE_CURRENT_SOURCE_DIR}/compile_commands.json
    SYMBOLIC
  )
endif ()

copy_plugin(${PROJECT_NAME} DIRECTORY ${CORONA_BINARY_DIR})

unset(CORONA_TEST CACHE)
unset(CORONA_WITH_RPATH CACHE)
unset(CORONA_WITH_NEURAL CACHE)
unset(CORONA_WITH_WATERMARK CACHE)