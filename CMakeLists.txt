cmake_minimum_required(VERSION 2.8)
set(CMAKE_C_STANDARD 99)
project(TX_CSV_PIGPIO)

option(USE_ASAN  "use GCC's address sanitizer?" OFF)

if (USE_ASAN)
  set(ASANLIB "asan")
else()
  set(ASANLIB "")
endif()

########################################################################
# select the release build type by default to get optimization flags
########################################################################
if(NOT CMAKE_BUILD_TYPE)
   set(CMAKE_BUILD_TYPE "Release")
   message(STATUS "Build type not specified: defaulting to release.")
endif(NOT CMAKE_BUILD_TYPE)

if ("${CMAKE_C_COMPILER_ID}" STREQUAL "MSVC")
  # using Visual Studio C++
  message(STATUS "INFO: detected MSVC: will not link math lib m")
  set(MATHLIB "")
else()
  message(STATUS "INFO: detected NO MSVC: ${CMAKE_C_COMPILER_ID}: will link math lib m")
  set(MATHLIB "m")
endif()


add_executable(tx_csv_pigpio   tx_csv_pigpio.c  )
target_compile_definitions(tx_csv_pigpio PRIVATE _USE_MATH_DEFINES)
if (USE_ASAN)
  target_compile_options(tx_csv_pigpio PRIVATE "-fsanitize=address")
endif()
# libpigpio.so
# gcc -Wall -pthread -o prog prog.c -lpigpio -lrt
target_link_libraries(tx_csv_pigpio pigpio pthread rt ${ASANLIB} ${MATHLIB} )

