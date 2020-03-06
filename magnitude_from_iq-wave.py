#!/usr/bin/env python3

import sys
import numpy as np
from scipy.io.wavfile import read
from scipy.io.wavfile import write

INPFILENAME="/dev/shm/rec.wav"
WAVMAGFILE="/dev/shm/rec-magnitude.wav"

if 1 < len(sys.argv):
	if sys.argv[1] == "-h" or sys.argv[1] == "--help":
		print("usage: {} [-h|--help]".format(sys.argv[0]))
		print("usage: {} [<wave-filename>]".format(sys.argv[0]))
		sys.exit()
	else:
		INPFILENAME=sys.argv[1]

[ SAMPLERATE, data ] = read(INPFILENAME)
duration = len(data) / SAMPLERATE

#print("shape: ", data.shape)
#print("len(shape): ", len(data.shape))
if len(data.shape) == 2 and data.shape[1] == 2:
	print("data looks to be complex baseband -> use magnitude")
	mag = np.absolute( data[:,0] + 1j * data[:,1] )
	print("mag.shape ", mag.shape, ", mag.dtype ", mag.dtype)
	minVal = mag.min()
	maxVal = mag.max()
	print("magnitude samples range: {} .. {}".format(minVal, maxVal))
	mag2 = mag.astype('int16')
	normVal = int(0.9 * 32768)
	mulFactor = normVal / maxVal
	mag = mag2 * mulFactor
	mag2 = mag.astype('int16')
	print("normalized magnitude to {} == {} with factor {}".format(normVal, normVal / 32768.0, mulFactor))
	write(WAVMAGFILE, SAMPLERATE, mag2)
	print("wrote magnitude to {}".format(WAVMAGFILE))
	data = mag2
else:
	print("input file is not complex")

print("samplerate from wave file: {} kHz".format(SAMPLERATE/1000.0))
print("number of samples: {} , sampletype {}".format(len(data), data.dtype))
print("duration: {} ms".format(duration*1000))

