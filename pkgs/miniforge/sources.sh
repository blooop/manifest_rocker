#!/bin/bash

#Add PPA or apt sources, or source code


URL=https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
# URL=https://repo.anaconda.com/archive/Anaconda3-2024.02-1-Linux-x86_64.sh
URL=https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh

wget --no-verbose --show-progress --progress=bar:force:noscroll $URL -O /anaconda.sh  
bash anaconda.sh -b -p "opt/conda"

rm /anaconda.sh

ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh 
echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc 
echo "conda activate base" >> ~/.bashrc 
find /opt/conda/ -follow -type f -name '*.a' -delete 
find /opt/conda/ -follow -type f -name '*.js.map' -delete

setfacl -R -m 1000:rwx /opt/conda

#source and update conda
. /opt/conda/etc/profile.d/conda.sh
conda update conda -y