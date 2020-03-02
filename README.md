# rc433_rpi
transmit remote control signals at 433.92 MHz with Raspberry Pi and a transmitter module

this software is intended for OOK (On-Off-Keying) signals, which has to be `recorded` once with an RTLSDR-USB receiver stick.
after `some` editing, you should be able to replay the signal utilizing a transmitter module connected to the Raspberry Pi.


# setup

- download repository
    * git clone https://github.com/hayguen/rc433_rpi.git
    * cd rc433_rpi
- install recommended packages; you might want to edit - before execution. your user needs sudo rights for this
    * ./install_recommended_packages.sh
- download several github sources
    * ./get_all_git_sources.sh
- build/install the downloaded github sources; you might want to edit - before execution. your user needs sudo rights for this
    * ./build_all_git_sources.sh

