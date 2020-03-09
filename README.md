
# rc433_rpi

transmit remote control signals at [ISM band](https://en.wikipedia.org/wiki/ISM_band) frequency 433.92 MHz with [Raspberry Pi](https://www.raspberrypi.org/) and a transmitter module

this software is intended for [OOK (On-Off-Keying)](https://en.wikipedia.org/wiki/On%E2%80%93off_keying) signals, which has to be *recorded* once with an RTL-SDR or a receiver module. For RTL-SDR see [http://superkuh.com/rtlsdr.html](http://superkuh.com/rtlsdr.html) or [https://www.rtl-sdr.com/](https://www.rtl-sdr.com/).
after *some* editing, you should be able to replay the signal utilizing a transmitter module connected to the Raspberry Pi.



there is other software for this purpose, e.g. [https://github.com/sui77/rc-switch](https://github.com/sui77/rc-switch). these software packages depend on the [http://wiringpi.com/](http://wiringpi.com/) software library. Unfortunately, the latest Wiring Pi sources with support for Raspberry Pi 4,now (2020-03-08) isn't available for several months .. see blog entry [http://wiringpi.com/wiringpi-deprecated/](http://wiringpi.com/wiringpi-deprecated/).

this software utilizes the [http://abyz.me.uk/rpi/pigpio/](http://abyz.me.uk/rpi/pigpio/) library, which is also referenced from the Raspberry Pi organization; see [https://www.raspberrypi.org/documentation/usage/gpio/README.md](https://www.raspberrypi.org/documentation/usage/gpio/README.md)




# software setup

1. download the repository:
    ```
    git clone https://github.com/hayguen/rc433_rpi.git
    cd rc433_rpi
    ```

2. install required packages:
    ```
    sudo apt-get install python3 python3-scipy pthon3-numpy
    sudo apt-get install pigpio pigpio-tools pigpiod python3-pigpio
    sudo apt-get install audacity gqrx-sdr
    ```

    or install several recommended packages. in this case, you might want to edit the install file - before executing it. the script/user requires `sudo` permissions:

    `./install_recommended_packages.sh`
    
3. download several github sources

    `./get_all_git_sources.sh`

4. build/install the downloaded github sources; you might want to edit - before execution. your user needs `sudo` rights for this

    `./build_all_git_sources.sh`


# hardware setup

transmitter module, e.g. FS1000A

1. optional, depending on required distance: solder an 'antenna' to the FS1000A. 'antenna' might simply be a wire of ~ 17 cm.
2. connect FS1000A's VCC to Raspberry Pi's Pin 17 (=3V3 Power)
3. connect FS1000A's DATA to Raspberry Pi's Pin 19 (=GPIO10)
4. connect FS1000A's GND to Raspberry Pi's Pin 20 (=Ground)


optional receiver module, e.g. XY-MK-5V - without antenna it's receive range is limited to about 10 cm!
that is enough for recording, cause you can transmit very close to the receiver with the remote control.

1. connect XY-MK-5V's VCC to Raspberry Pi's Pin 1 (=3V3 Power)
2. connect one of XY-MK-5V's DATA to Raspberry Pi's Pin 7 (=GPIO4)
3. connect XY-MK-5V's GND to Raspberry Pi's Pin 9 (=Ground)


optionally connect an RTL-SDR receiver with a suitable antenna to one of the Raspberry Pi's USB ports.
you might try without antenna transmitting very close to the RTL-SDR's antenna input with the remote control.

an RTL-SDR will produce more accurate timing results with it's internal clock.
with a receiver module the timing depends on the latency from input pin change to execution of the callback handler.

you need to connect RTL-SDR or a receiver module once, to record the remote control signals.


# record remote control signal with a receiver module

1. start the pigpio daemon - if not already running (this requires root privileges):

    `sudo pigpiod`

2. change directory to the clone github directory, e.g.

    `cd $HOME/rc433_rpi`

    

3. record the raw signal - be prepared to press the remote control multiple times before pressing enter:

    `./rx_wav_from_gpio.py`

4. open an audio editor, e.g. audacity. open the recorded '/dev/shm/rec.wav' file

    `audacity`

    1. cut the signal to one single pulse train: mark and delete unnecessary regions. zoom if required

    2. export the edited region to a WAVE file, e.g. in your home as rec-lunvon-IV-ALL-OFF.wav

    3. close the file in audacity

        

5. convert the exported WAVE into a smaller .csv file

    `./csv_from_wave.py rec-lunvon-IV-ALL-OFF.wav`

6. transmit the generated .csv - check if remote controlled device is switched:

    `./tx_csv.py /dev/shm/rec.csv`

    repeat recording and test if device isn't switched

    

7. copy/move the working generated .csv file to somewhere persistent

    `mv /dev/shm/rec.csv $HOME/lunvon-IV-ALL-OFF.csv`


# record remote control signal with an RTL-SDR

1. start the pigpio daemon - if not already running (this requires root privileges):

    `sudo pigpiod`

2. change directory to the clone github directory, e.g.

    `cd $HOME/rc433_rpi`

3. determine exact frequency of remote control with an SDR software, e.g. gqrx

    `gqrx`

    1. select correct device (menu File, I/O Devices)

    2. press 'Play' button (menu File, Start DSP / Ctrl-D)

    3. in 'Receiver Options' tab, set 'Frequency' to 433920 kHz and play around

    4. in addition play with the 'LNA' (gain) in the 'Input Control' tab

    5. note the exact frequency (e.g. 433.97 MHz) and gain (32.8), then close the program

         

4. record the raw signal - be prepared to press the remote control multiple times before pressing enter.
     use the gain value (required) and the exact frequency (optional) as parameters:

     `./rx_wav_from_rtlsdr.sh 32.8 433.97`

5. open an audio editor, e.g. `audacity`. open the recorded '/dev/shm/rec-magnitude.wav' file

     `audacity`

     1. cut the signal to one single pulse train: mark and delete unnecessary regions. zoom if required
     2. export the edited region to a WAVE file, e.g. in your home as rec-lunvon-IV-A-ON.wav
     3. close the file in audacity

     repeat recording with different gain level or transmit more close / distant if no obvious threshold can be determined

6. calculate threshold value as 16 Bit with a calculator or  in `python3`:

     `python3`

     enter the threshold `0.4 * 32768`, gives ~ 13100. then `exit()` python with Ctrl-D

7. convert the exported WAVE into a smaller .csv file

     `./csv_from_wave.py rec-lunvon-IV-A-ON.wav 13100`

8. transmit the generated .csv - check if remote controlled device is switched:

     `./tx_csv.py /dev/shm/rec.csv`

     repeat recording - if device isn't switched

     

9. copy/move the working .csv file to somewhere persistent

     `mv /dev/shm/rec.csv $HOME/lunvon-IV-A-ON.csv`


# replay remote control signal

1. start the `pigpio` daemon - if not already running (this requires root privileges):

    `sudo pigpiod`

2. change directory to the cloned github directory, e.g.

    `cd $HOME/rc433_rpi`

3. transmit the saved .csv

    `./tx_csv.py $HOME/lunvon-IV-A-ON.csv`

