#!/bin/bash

sudo apt-get -y install dos2unix mc htop geany meld
sudo apt-get -y install build-essential git git-gui cmake cmake-gui cmake-curses-gui
sudo apt-get -y install libfftw3-dev libusb-1.0-0-dev librtlsdr-dev rtl-sdr libtool autoconf pkg-config
sudo apt-get -y install libliquid-dev libsndfile1-dev libxml2-dev libsoapysdr-dev soapysdr-module-rtlsdr soapysdr-tools
sudo apt-get -y install qt5-default qtbase5-dev qtchooser libqt5multimedia5-plugins qtmultimedia5-dev qttools5-dev qttools5-dev-tools libqt5opengl5-dev qtbase5-dev
sudo apt-get -y install audacity gqrx-sdr cubicsdr
sudo apt-get -y install python3 python3-scipy python3-numpy python3-matplotlib ipython3

# sudo apt-get install python-setuptools python-pigpio
sudo apt-get -y install pigpio pigpio-tools pigpiod python3-setuptools python3-pigpio gtk+-3.0
