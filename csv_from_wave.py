#!/usr/bin/env python3

import sys
import csv
import numpy as np
from scipy.io.wavfile import read
from scipy.io.wavfile import write

WAVINPFILENAME="/dev/shm/rec.wav"
WAVMAGFILE="/dev/shm/rec-magnitude.wav"
CSVFILE="/dev/shm/rec.csv"
TEST=False

if 1 < len(sys.argv):
	if sys.argv[1] == "-h" or sys.argv[1] == "--help":
		print("usage: {} [-h|--help]".format(sys.argv[0]))
		print("usage: {} [<wave-filename> [<threshold>] ]".format(sys.argv[0]))
		sys.exit()
	else:
		WAVINPFILENAME=sys.argv[1]

if TEST:
	SAMPLERATE=1000 * 1000
	data = np.zeros( SAMPLERATE, dtype='uint8') # 1 sec
	data[ np.arange(100*1000, 200*1000) ] = 128+64 # hi in [ 100 ms .. 200 ms ]
	data[ np.arange(350*1000, 600*1000) ] = 128+64 # hi in [ 350 ms .. 600 ms ]
else:
	[ SAMPLERATE, data ] = read(WAVINPFILENAME)
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
	write(WAVMAGFILE, SAMPLERATE, mag2)
	print("wrote magnitude to {}".format(WAVMAGFILE))
	data = mag2

print("samplerate from wave file: {} kHz".format(SAMPLERATE/1000.0))
print("number of samples: ", len(data))
print("duration: {} ms".format(duration*1000))

haveThrVal=False
if 2 < len(sys.argv):
	thrVal=int(sys.argv[2])
	haveThrVal=True

minVal = data.min()
maxVal = data.max()
print("wave samples range: {} .. {}".format(minVal, maxVal))
if not haveThrVal:
	thrVal = minVal / 2 + maxVal / 2
	print("determined threshold from samples range")
else:
	print("using threshold from command line")
print("using threshold {}".format(thrVal))

olddata = data
data = np.zeros( len(olddata), dtype = np.dtype('uint8') )
data[ olddata >= thrVal ] = 1


dif = np.diff( data )
nz = np.nonzero( dif )[0] +1
nz = np.insert(nz, 0, 0)
bitv = data[nz]
lens = np.diff(nz)

if TEST:
	print("data ", data.dtype)
	print("data: ", data, " len = ", len(data), ", dtype ", data.dtype)
	print("diff:    ", dif, " len = ", len(dif), ", dtype ", dif.dtype)
	print("nz:      ", nz, " len = ", len(nz), ", dtype ", nz.dtype)
	print("bitv:    ", bitv, " len = ", len(bitv), ", dtype ", bitv.dtype)
	print("lens:    ", lens, " len = ", len(lens), ", dtype ", lens.dtype)

with open(CSVFILE, 'w') as csvfile:
	cw = csv.writer(csvfile)
	for idx in range(len(nz)-1):
		#print("{}: len {}, level {}".format(idx, lens[idx], bitv[idx]))
		cw.writerow([ lens[idx], bitv[idx] ])
	idx = len(nz)-1
	#print("{}: len {}, level {}".format(idx, len(data)-nz[idx], bitv[idx]))
	cw.writerow([ len(data)-nz[idx], bitv[idx] ])
	print("wote {}".format(CSVFILE))

