#!/bin/bash

# git clone https://github.com/KhronosGroup/OpenXR-SDK.git
cd OpenXR-SDK

#Build code
mkdir -p build/linux_release
cd build/linux_release
cmake -DCMAKE_BUILD_TYPE=Release ../..
make
sudo make install