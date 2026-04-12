cmake_minimum_required(VERSION 3.1)
project(opencog-hpp LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
find_package(Threads REQUIRED)

# Header-only library
add_library(oc INTERFACE)
target_include_directories(oc INTERFACE include)
target_link_libraries(oc INTERFACE Threads::Threads)

# Test suite
add_executable(test_all test/test_all.cpp)
target_link_libraries(test_all oc)
enable_testing()
add_test(NAME opencog_hpp_tests COMMAND test_all)
