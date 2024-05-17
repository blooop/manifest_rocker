#!/bin/bash

rm -rf palanteer
git clone https://github.com/dfeneyrou/palanteer.git
cd palanteer
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc) install