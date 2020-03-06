#!/usr/bin/env python3

import sys
import time
import pigpio
import numpy as np
from scipy.io.wavfile import write

PIN=4
PUD=pigpio.PUD_OFF		# PUD_OFF / PUD_UP / PUD_DOWN
pudStr="OFF"
OUTFILE="/dev/shm/rec.wav"
DURMS=3000

SAMPLERATE=1000 * 1000    # samplerate 1 MHz == T = 1 us
bufused = 0
bufmax = 3 * 1000*1000   # max 5 sec
bufTime  = np.zeros( bufmax, dtype = np.dtype('uint32') )
bufLevel = np.zeros( bufmax, dtype = np.dtype('uint8') )


def cbf(gpio, level, tick):
	global bufused, bufmax, bufTime, bufLevel
	# just save incoming data, to be as fast as possible
	if PIN == gpio and bufused < bufmax:
		bufTime[bufused] = tick
		bufLevel[bufused] = level
		bufused = bufused + 1


def convert():
	global bufused, bufmax, bufTime, bufLevel
	global PIN, OUTFILE, SAMPLERATE
	lasttick = 0
	duration = pigpio.tickDiff( bufTime[0], bufTime[bufused -1] ) + 1
	print(f"#total duration {duration} us")
	linLevel = np.zeros( duration, dtype = np.dtype('uint8') )
	lastTime = 0
	lastLevel = 0
	for k in range(bufused):
		newTime = pigpio.tickDiff(bufTime[0], bufTime[k])
		newLevel = bufLevel[k]
		#print(f"{lastTime}, {newLevel}")
		for t in range( lastTime, newTime ):
			linLevel[t] = lastLevel
		lastTime = newTime
		lastLevel = newLevel
		linLevel[newTime] = newLevel
	linLevel=linLevel * 64 + 128
	write(OUTFILE, SAMPLERATE, linLevel)


if 1 < len(sys.argv):
	if sys.argv[1] == "-h" or sys.argv[1] == "--help":
		print("usage: {} [-h|--help]".format(sys.argv[0]))
		print("usage: {} [<pin-number> [<duration> [<pull-mode>] ] ]".format(sys.argv[0]))
		print("  pin-number    pin number of receiver module, default = {}".format(PIN))
		print("  duration      recording duration in milliseconds, default = {}".format(DURMS))
		print("  pull-mode     'O' for off, 'U' for up or 'D' for down; default = {}".format(pudStr))
		sys.exit()
	else:
		PIN=int(sys.argv[1])

if 2 < len(sys.argv):
	DURMS = int(sys.argv[2])
	if DURMS > int(bufmax / 1000 ):
		DURMS = int(bufmax / 1000)
		print("limited duration to maximum of {} ms".format(DURMS*1000))

DUR=int(DURMS) / 1000

if 3 < len(sys.argv):
	if sys.argv[2] == "o" or sys.argv[2] == "O":
		PUD=pigpio.PUD_OFF
		pudStr="OFF"
	elif sys.argv[2] == "u" or sys.argv[2] == "U":
		PUD=pigpio.PUD_UP
		pudStr="UP"
	elif sys.argv[2] == "d" or sys.argv[2] == "D":
		PUD=pigpio.PUD_DOWN
		pudStr="DOWN"
	else:
		print("3rd parameter must be 'O' for off, 'U' for up or 'D' for down")

print("using input-pin {}  with pull mode {}".format(PIN, pudStr))
print("using recording duration of {} ms".format(DUR*1000))


p = pigpio.pi()
print("pigpio version: ", p.get_pigpio_version())

p.hardware_clock(PIN, SAMPLERATE)
p.set_mode(PIN, pigpio.INPUT)
p.set_pull_up_down(PIN, PUD)

#time.sleep(0.01)  # wait 10 ms
cb = p.callback(PIN, pigpio.EITHER_EDGE, cbf)
print("installed callback function, now sleeping {} sec for record ..".format(DUR))
time.sleep(DUR)
cb.cancel()  # cancel callback and recording
time.sleep(0.1)  # wait additional 100 ms, that no further callbacks follow

print("collected {} events".format(bufused))

convert()
