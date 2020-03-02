#!/bin/bash

D="$(pwd)"
if [ ! -d "git-src" ]; then
  echo "error: run ./get_all_git_sources.sh first to download all sources from github"
  exit 0
fi

if [ -d "$D/git-src/csdr" ]; then
  pushd "$D/git-src/csdr" &>/dev/null
  echo -e "\n\n"
  echo "**************************"
  echo "building csdr"
  echo "**************************"
  make
  sudo make install
  popd &>/dev/null
fi

if [ -d "$D/git-src/rtl_433" ]; then
  pushd "$D/git-src/rtl_433" &>/dev/null
  echo -e "\n\n"
  echo "**************************"
  echo "building rtl_433"
  echo "**************************"
  mkdir build
  cd build
  cmake ..
  make
  sudo make install
  popd &>/dev/null
fi

# multimon-ng is not cloned/downloaded with get_all_git_sources.sh
if [ -d "$D/git-src/multimon-ng" ]; then
  pushd "$D/git-src/multimon-ng" &>/dev/null
  echo -e "\n\n"
  echo "**************************"
  echo "building multimon-ng"
  echo "**************************"
  mkdir build
  cd build
  cmake ..
  make
  sudo make install
  popd &>/dev/null
fi

if [ -d "$D/git-src/inspectrum" ]; then
  pushd "$D/git-src/inspectrum" &>/dev/null
    echo -e "\n\n"
  echo "**************************"
  echo "building inspectrum"
  echo "**************************"
  #sudo apt-get install qt5-default libfftw3-dev cmake pkg-config libliquid-dev
  mkdir build
  cd build
  cmake ..
  make
  sudo make install
  popd &>/dev/null
fi

# use the debian/raspbian system's pigpio package
#if [ -d "$D/git-src/pigpio" ]; then
if /bin/false; then
  pushd "$D/git-src/pigpio" &>/dev/null
  echo -e "\n\n"
  echo "**************************"
  echo "building pigpio"
  echo "**************************"
  make
  make install
  popd &>/dev/null
fi

if [ -d "$D/git-src/piscope" ]; then
  pushd "$D/git-src/piscope" &>/dev/null
  echo -e "\n\n"
  echo "**************************"
  echo "building piscope"
  echo "**************************"
  #sudo apt-get install pigpio pigpio-tools pigpiod python-pigpio python3-setuptools python3-pigpio gtk+-3.0
  make
  make install
  popd &>/dev/null
fi

if [ -d "$D/git-src/librtlsdr" ]; then
  pushd "$D/git-src/librtlsdr" &>/dev/null
  echo -e "\n\n"
  echo "**************************"
  echo "building librtlsdr"
  echo "**************************"
  git checkout development
  mkdir build
  cd build
  cmake ../ -DINSTALL_UDEV_RULES=ON -DLINK_RTLTOOLS_AGAINST_STATIC_LIB=ON
  sudo make install
  popd &>/dev/null
  pushd "$D/git-src/librtlsdr" &>/dev/null
  sudo ./install-blacklist.sh
  popd &>/dev/null
fi

