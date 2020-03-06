#!/bin/bash

OUTFILE="/dev/shm/rec.wav"

if [ -z "$1" ]; then
  echo "following gain values are possible:"
  timeout -s SIGTERM -k 2 1 rtl_test 2>&1 |grep "^Supported gain values"
  echo ""
  echo "usage: $0 <gain_value> [<freq_MHz> [bw_kHz] ]"
  echo ""
  exit 0
fi

GAIN="$1"
FREQ="$2"
BW="$3"
if [ -z "$FREQ" ]; then
  FREQ="433.92"
fi
if [ -z "$BW" ]; then
  BW="600"
fi

echo ""
echo "starting recording with rtl_fm to ${OUTFILE}"

# Supported bandwidth values in kHz - for option -w
# 290.0, 375.0, 420.0, 470.0, 600.0, 860.0, 950.0, 1100.0, 1300.0, 1503.0, 1600.0, 1753.0, 1953.0

# -m 1M   -M iq  -M am
timeout -s SIGTERM -k 5 4 rtl_fm -f ${FREQ}M -v -M iq -s 1M -g ${GAIN} -w ${BW}k -E rdc -L 10 -H $OUTFILE

#echo "recorded file's information"
#rtl_wavestat -a $OUTFILE

# create wave with magnitude from complex I/Q record
./magnitude_from_iq-wave.py $OUTFILE
