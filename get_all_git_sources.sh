#!/bin/bash

D="$(pwd)"
if [ ! -d "git-src" ]; then
  mkdir -p $D/git-src
  echo "git-src" >$D/.gitignore
fi

cd $D/git-src
if [ "$(pwd)" = "$D/git-src" ]; then
  # https://github.com/ha7ilm/csdr
  git clone https://github.com/ha7ilm/csdr.git
  echo ""
  # https://github.com/merbanan/rtl_433
  git clone https://github.com/merbanan/rtl_433.git
  #echo ""
  # https://github.com/EliasOenal/multimon-ng
  #git clone https://github.com/EliasOenal/multimon-ng.git
  echo ""
  # https://github.com/miek/inspectrum
  # https://github.com/miek/inspectrum/wiki/Build
  git clone https://github.com/miek/inspectrum.git
  echo ""
  # https://github.com/joan2937/pigpio
  # http://abyz.me.uk/rpi/pigpio/
  git clone https://github.com/joan2937/pigpio.git
  echo ""
  # https://github.com/joan2937/piscope
  git clone https://github.com/joan2937/piscope.git
  echo ""
  # https://github.com/hayguen/librtlsdr/tree/development
  git clone https://github.com/hayguen/librtlsdr.git
else
  echo "could not create or change into $D/git-src"
fi
