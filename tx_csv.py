#!/usr/bin/env python3

import sys
import time
import csv
import pigpio
import numpy as np
from scipy.io.wavfile import read

PIN=10
DURMS=-1
INPCSVFILE="/dev/shm/rec.csv"

if 1 < len(sys.argv):
	if sys.argv[1] == "-h" or sys.argv[1] == "--help":
		print("usage: {} [-h|--help]".format(sys.argv[0]))
		print("usage: {} [<csv-filename> [ <gpio-pin> [ <duration_ms> ] ] ]".format(sys.argv[0]))
		sys.exit()
	else:
		INPCSVFILE=sys.argv[1]

if 2 < len(sys.argv):
	PIN=int(sys.argv[2])

if 3 < len(sys.argv):
	DURMS=int(sys.argv[3])

p = pigpio.pi()
print("pigpio version: ", p.get_pigpio_version())
p.set_mode(PIN, pigpio.OUTPUT)
p.write(PIN, 0)

pulseTrain=[]
pinMask = 1 << PIN
#                              ON     OFF  DELAY
#pulseTrain.append(pigpio.pulse(1<<PIN, 0,  0))
pulseLen = 0

with open(INPCSVFILE) as csvfile:
	cr = csv.reader(csvfile)
	rowNo = 1
	for row in cr:
		#print(row, "# len(row) = ", len(row))
		if len(row) == 2:
			# pigpio version 74 (at least) seems to have an error:
			# the transmitted pulses have doubled length
			# (tested receiving with an rtlsdr).
			# -> halve the pulse length
			d = int( int(row[0]) / 2 )
			v = int(row[1])
			pulseLen = pulseLen + int(row[0])
			if v > 0:
				pulseTrain.append(pigpio.pulse(pinMask, 0, d))
			else:
				pulseTrain.append(pigpio.pulse(0, pinMask, d))
			#print("  {}, {}".format(d, v))
		else:
			print("ignoring row {}, with {} columns!: {}".format(rowNo, len(row), row))
		rowNo = rowNo + 1

print("read {} pulse values from csv file {}".format(len(pulseTrain), INPCSVFILE))
print("  1 pulse length duration is {} ms".format( int( (pulseLen+999) / 1000 )) )

if DURMS < 0:
	DURMS = int( (pulseLen+999) / 1000 )

#max_num_pulses = p.wave_get_max_pulses()
#print("pigpio.wave_get_max_pulses() = {}".format(max_num_pulses))

p.wave_clear() # clear any existing waveforms
p.wave_add_generic(pulseTrain)
pT = p.wave_create() # create and save id

print("transmitting for {} ms ..".format(DURMS))
DUR = DURMS / 1000.0
p.wave_send_repeat(pT)
time.sleep(DUR)
p.wave_tx_stop() # stop waveform
print(".. stopped")

#print("pigpio.wave_get_pulses() = {}".format(p.wave_get_pulses()))
#print("pigpio.wave_get_micros() = {}".format(p.wave_get_micros()))

p.wave_clear() # clear all waveforms
time.sleep(0.1)
p.write(PIN, 0)

