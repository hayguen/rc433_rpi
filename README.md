
# rc433_rpi

transmit remote control signals at 433.92 MHz with Raspberry Pi and a transmitter module

this software is intended for OOK (On-Off-Keying) signals, which has to be `recorded` once with an RTLSDR-USB receiver stick.
after `some` editing, you should be able to replay the signal utilizing a transmitter module connected to the Raspberry Pi.


# software setup

- download repository
    * `git clone https://github.com/hayguen/rc433_rpi.git`
    * `cd rc433_rpi`
- install recommended packages; you might want to edit - before execution. your user needs sudo rights for this
    * `./install_recommended_packages.sh`
- download several github sources
    * `./get_all_git_sources.sh`
- build/install the downloaded github sources; you might want to edit - before execution. your user needs sudo rights for this
    * `./build_all_git_sources.sh`


# hardware setup

transmitter module, e.g. FS1000A

- optional, depending on required distance: solder an 'antenna' to the FS1000A. 'antenna' might simply be a wire of ~ 17 cm.
- connect FS1000A's VCC to Raspberry Pi's Pin 17 (=3V3 Power)
- connect FS1000A's DATA to Raspberry Pi's Pin 19 (=GPIO10)
- connect FS1000A's GND to Raspberry Pi's Pin 20 (=Ground)

optional receiver module, e.g. XY-MK-5V - without antenna it's receive range is limited to about 10 cm!
that is enough for recording, cause you can transmit very close to the receiver with the remote control.

- connect XY-MK-5V's VCC to Raspberry Pi's Pin 1 (=3V3 Power)
- connect one of XY-MK-5V's DATA to Raspberry Pi's Pin 7 (=GPIO4)
- connect XY-MK-5V's GND to Raspberry Pi's Pin 7 (=Ground)

optionally connect an RTL-SDR receiver with a suitable antenna to one of the Raspberry Pi's USB ports.
you might try without antenna transmitting very close to the RTL-SDR's antenna input with the remote control.

an RTL-SDR will produce more accurate timing results with it's internal clock.
with a receiver module the timing depends on the latency from input pin change to execution of the callback handler.

you need to connect RTL-SDR or a receiver module once, to record the remote control signals.


# record remote control signal with a receiver module

- start the pigpio daemon - if not already running (this requires root privileges):
    * `sudo pigpiod`
- change directory to the clone github directory, e.g.
    * `cd $HOME/rc433_rpi`

- record the raw signal - be prepared to press the remote control multiple times before pressing enter:
    * `./rx_wav_from_gpio.py`

- open an audio editor, e.g. audacity. open the recorded '/dev/shm/rec.wav' file
    * `audacity`
- cut the signal to one single pulse train: mark and delete unnecessary regions. zoom if required
- export the edited region to a WAVE file, e.g. in your home as rec-lunvon-IV-ALL-OFF.wav
- close the file in audacity

- convert the exported WAVE into a smaller .csv file
    * `./csv_from_wave.py rec-lunvon-IV-ALL-OFF.wav`

- transmit the generated .csv - check if remote controlled device is switched:
    * `./tx_csv.py /dev/shm/rec.csv`

- repeat recording and test if device isn't switched

- copy/move the working generated .csv file to somewhere persistent
    * `mv /dev/shm/rec.csv lunvon-IV-ALL-OFF.csv`


# record remote control signal with an RTL-SDR

- start the pigpio daemon - if not already running (this requires root privileges):
    * `sudo pigpiod`
- change directory to the clone github directory, e.g.
    * `cd $HOME/rc433_rpi`

- determine exact frequency of remote control with an SDR software, e.g. gqrx
    * `gqrx`
- select correct device (menu File, I/O Devices)
- press 'Play' button (menu File, Start DSP / Ctrl-D)
- in 'Receiver Options' tab, set 'Frequency' to 433920 kHz and play around
- in addition you might play with the 'LNA' (gain) in the 'Input Control' tab
- note the exact frequency and close the program, e.g. 433.97 MHz

- record the raw signal - be prepared to press the remote control multiple times before pressing enter.
  use the gain value (required) and the exact frequency (optional) as parameters:
    * `./rx_wav_from_rtlsdr.sh 32.8 433.97`

- open an audio editor, e.g. audacity. open the recorded '/dev/shm/rec-magnitude.wav' file
    * `audacity`
- cut the signal to one single pulse train: mark and delete unnecessary regions. zoom if required
- export the edited region to a WAVE file, e.g. in your home as rec-lunvon-IV-A-ON.wav
- close the file in audacity
- repeat recording with a different gain level or transmitting more close/distand if no obious threshold can be determined

- calculate threshold value as 16 Bit, e.g. in python or with a calculator:
    * `python3`
- enter the threshold 0.4 * 32768, gives ~ 13100. then exit python with Ctrl-D
    * `0.4 * 32768`

- convert the exported WAVE into a smaller .csv file
    * `./csv_from_wave.py rec-lunvon-IV-A-ON.wav 13100`

- transmit the generated .csv - check if remote controlled device is switched:
    * `./tx_csv.py /dev/shm/rec.csv`

- repeat recording and test if device isn't switched

- copy/move the working generated .csv file to somewhere persistent
    * `mv /dev/shm/rec.csv lunvon-IV-A-ON.csv`


# replay remote control signal

- start the pigpio daemon - if not already running (this requires root privileges):
    * `sudo pigpiod`
- change directory to the clone github directory, e.g.
    * `cd $HOME/rc433_rpi`
- transmit the saved .csv
    * `./tx_csv.py $HOME/lunvon-IV-A-ON.csv`

