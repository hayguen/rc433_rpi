
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include <pigpio.h>

#define NUM_TEST_PULSES         0
#define CHECK_TIMING_ACCURACY   1
#define PRINT_EACH_TIMING_ERR   0

static int tx_pin = 10;
static int duration_ms = -1;
static const char * csv_filename = "/dev/shm/rec.csv";

static uint32_t * pPulse = NULL;
static uint32_t pulseLen = 0;
static int numPulseRows = 0;
static int pulseMemSize = 0;
#if CHECK_TIMING_ACCURACY
static uint32_t * pTick = NULL;
#endif

/* forward declare */
void transmit_pulse_train();
int read_pulse_train_from_csv();


int main(int argc, char *argv[])
{
  int k;

  if ( 1 < argc )
  {
    if ( !strcmp("-h", argv[1]) || !strcmp("--help", argv[1]) )
    {
      fprintf(stderr, "usage: sudo nice -n -10 %s [<tx-pin> [ <csv-filename> [<duration-ms> ] ] ]\n", argv[0] );
      fprintf(stderr, "  tx-pin       GPIO-xx: pin number to use for transmission; default = %d\n", tx_pin);
      fprintf(stderr, "  csv-filename; default = '%s'\n", csv_filename);
      fprintf(stderr, "  duration-ms  total transmit duration ; < 0 to ignore; default = %d\n", duration_ms);
      fprintf(stderr, "\n");
      fprintf(stderr, "to run this program, pigpiod needs to be stopped, which has it's pid in /var/run/pigpiod.pid:\n");
      fprintf(stderr, "  $ sudo kill $(cat /var/run/pigpio.pid)\n");
      fprintf(stderr, "\n");
      return 1;
    }
    tx_pin = atoi( argv[1] );
  }

  if ( 2 < argc && strlen(argv[2]) > 0 )
    csv_filename = argv[2];

  if ( 3 < argc && strlen(argv[3]) > 0 )
    duration_ms = atoi( argv[3] );

#if NUM_TEST_PULSES > 0
  pPulse = malloc( 2 * 2 * NUM_TEST_PULSES * sizeof(uint32_t) );
  numPulseRows = 2 * NUM_TEST_PULSES;
  pulseLen = 0;

  for ( k = 0; k < 2 * NUM_TEST_PULSES; ++k )
  {
    pulseLen += 500U * 1000U;
    pPulse[2*k] = 500U * 1000U;
    pPulse[2*k+1] = (k + 1) & 1;
  }
#else
  read_pulse_train_from_csv();
#endif

  if (gpioInitialise() < 0)
  {
    fprintf(stderr, "pigpio initialisation failed.\n");
    return 1;
  }

  /* initialize */
  gpioSetMode( tx_pin, PI_OUTPUT );
  gpioWrite( tx_pin, 0 ); /* set low */

  if ( duration_ms < 0 )
    duration_ms = ( pulseLen + 999 ) / 1000;
  fprintf(stderr, "  1 pulse length duration is %d ms\n", duration_ms);

  fprintf(stderr, "using tx-pin %d\n", tx_pin);
  fprintf(stderr, "using csv_filename %s\n", csv_filename);
  fprintf(stderr, "using duration_ms %d\n", duration_ms);

  transmit_pulse_train();

  return 0;
}


void transmit_pulse_train()
{
  uint32_t tickNom, delaySum_us;
  int32_t  adjustedDelay, tickErrFromNom, timeErr, minTimeErr, maxTimeErr;
  int k, i, j, contRepeat = 1;

  delaySum_us = 0;

  fprintf(stderr, "transmitting ..\n");

#if CHECK_TIMING_ACCURACY
  pTick = malloc( ( 2 + numPulseRows ) * sizeof(uint32_t) );
  tickNom = pTick[0] = gpioTick();
#else
  tickNom = gpioTick();
#endif
  tickErrFromNom = 0;

  while ( contRepeat )
  {
    i = 1;

    for ( k = 0; k < 2 * numPulseRows; k += 2, ++i )
    {
      /* set high for even k; set low for odd k */
      gpioWrite( tx_pin, pPulse[k+1] );

      const uint32_t delay_us = pPulse[k];  /* desired delay */
      adjustedDelay = delay_us - tickErrFromNom;

      if ( adjustedDelay > 2 * 1000 * 1000 )
        fprintf(stderr, "k %d, i %d: adjustedDelay = %d us\n", k, i, (int)adjustedDelay);
      if ( adjustedDelay > 0 )
      {
        if ( adjustedDelay <= 100 )
          gpioDelay( adjustedDelay ); /* this is busy loop! */
        else
        {
          gpioDelay( adjustedDelay - 99 );
          tickErrFromNom = tickNom + adjustedDelay - gpioTick();  /* how much left to delay? */
          if ( tickErrFromNom > 1 )
            gpioDelay( tickErrFromNom ); /* this is busy loop! */
        }
      }

      tickNom += delay_us; /* adjustedDelay */
      delaySum_us += delay_us;
      if ( duration_ms > 0 && (delaySum_us / 1000) >= duration_ms )
      {
        contRepeat = 0;
        break;
      }

#if CHECK_TIMING_ACCURACY
      pTick[i] = gpioTick();
      tickErrFromNom = pTick[i] - tickNom;
#else
      tickErrFromNom = gpioTick() - tickNom;
#endif
    }
  }

  gpioWrite( tx_pin, 0 ); /* set low */

  fprintf(stderr, "transmission finished.\n");

#if CHECK_TIMING_ACCURACY
  tickNom = 0;
  minTimeErr = 0;
  maxTimeErr = 0;
#if PRINT_EACH_TIMING_ERR
  for ( i = 0; i < numPulseRows; ++i )
    fprintf(stderr, "row %d: delay %d, pin %d\n", i, pPulse[2*i], pPulse[2*i+1] );
#endif

#if PRINT_EACH_TIMING_ERR
  i = 0;
  fprintf(stderr, "%d: t = %u\t%u\n", i, pTick[0], 0);
#endif
  for ( i = 0; i < numPulseRows; ++i )
  {
    j = i+1;
    tickNom += pPulse[2*i];
    timeErr = pTick[j] - pTick[0] - tickNom;
    if ( timeErr < minTimeErr )
      minTimeErr = timeErr;
    if ( timeErr > maxTimeErr )
      maxTimeErr = timeErr;

#if PRINT_EACH_TIMING_ERR
    fprintf(stderr, "%d: t = %u\t%u\t\terr %d\t\tdelta %d us\n", j, pTick[j], pTick[j] - pTick[0],
        timeErr,
        (int32_t)(pTick[j] - pTick[i]) );
#endif
  }

  fprintf(stderr, "timing accuracy: error in %d .. %d usec\n", minTimeErr, maxTimeErr);
#endif
}


int read_pulse_train_from_csv()
{
  char lineBuffer[1024];
  char *token = NULL;
  char *colStr = NULL;
  int lineNo = 0;
  int delayVal, pinLevelVal, k;
  FILE * f = NULL;

  f = fopen(csv_filename, "r");
  if ( !f )
  {
    fprintf(stderr, "error opening .csv file '%s'\n", csv_filename);
    return 1;
  }

  pulseLen = 0;
  while ( !feof(f) )
  {
    ++lineNo;
    if ( &lineBuffer[0] != fgets( lineBuffer, 1024, f ) )
    {
      fprintf(stderr, "error reading line %d; assume end-of-file\n", lineNo);
      break;
    }

    for ( k = 0; lineBuffer[k]; ++k )
    {
      if ( lineBuffer[k] == '\r' || lineBuffer[k] == '\n' )
      {
        lineBuffer[k] = 0;
        break;
      }
    }

    if ( lineBuffer[0] == '#' )
    {
      fprintf(stderr, "line %d is comment '%s'\n", lineNo, lineBuffer);
      continue;
    }
    token = strtok( &lineBuffer[0], "#" );  /* look for comments, starting with '#' */
    if ( !token )
    {
      fprintf(stderr, "error processing line %d. continue with next line\n", lineNo);
      continue;
    }

    token = strtok( token, "," );  /* split at comma */
    if ( !token )
    {
      fprintf(stderr, "error processing line %d. continue with next line\n", lineNo);
      continue;
    }
    if ( token[0] == 0 || token[0] == '\r' || token[0] == '\n' )
    {
      fprintf(stderr, "line %d 1st column is empty '%s'\n", lineNo, lineBuffer);
      continue;
    }

    colStr = token;
    while(isspace(*colStr)) ++colStr;
    if ( colStr[0] == 0 || colStr[0] == '\r' || colStr[0] == '\n' )
    {
      fprintf(stderr, "line %d 2nd column is empty '%s'\n", lineNo, lineBuffer);
      continue;
    }
    delayVal = atoi(colStr);

    token = strtok(NULL, ",");
    if ( !token )
    {
      fprintf(stderr, "error processing line %d. continue with next line\n", lineNo);
      continue;
    }
    if ( token[0] == 0 || token[0] == '\r' || token[0] == '\n' )
    {
      fprintf(stderr, "line %d 2nd column is empty '%s'\n", lineNo, lineBuffer);
      continue;
    }

    colStr = token;
    while(isspace(*colStr)) ++colStr;
    if ( colStr[0] == 0 || colStr[0] == '\r' || colStr[0] == '\n' )
    {
      fprintf(stderr, "line %d 2nd column is empty '%s'\n", lineNo, lineBuffer);
      continue;
    }
    pinLevelVal = atoi(colStr);

    if ( delayVal < 0 || delayVal >= 5 * 1000 * 1000 )
    {
      fprintf(stderr, "line %d: delay in 1st column must be >= 0; but is %d. skipping line\n", lineNo, delayVal );
      continue;
    }

    if ( pinLevelVal < 0 || pinLevelVal > 1 )
    {
      fprintf(stderr, "line %d: pin level must be 0 or 1; but is %d. skipping line\n", lineNo, pinLevelVal );
      continue;
    }

    if ( numPulseRows >= pulseMemSize )
    {
      uint32_t * pTempBuf = malloc( 2 * (pulseMemSize + 1024) * sizeof(uint32_t) );
      if ( numPulseRows > 0 )
        memcpy( pTempBuf, pPulse, 2 * numPulseRows * sizeof(uint32_t) );
      free( pPulse );
      pPulse = pTempBuf;
      pulseMemSize += 1024;
    }

    pulseLen += delayVal;
    pPulse[ 2 * numPulseRows ] = delayVal;
    pPulse[ 2 * numPulseRows + 1 ] = pinLevelVal;
    ++numPulseRows;
  }

  fprintf(stderr, "read %d pulses from .csv\n", numPulseRows);

  fclose(f);
  return 0;
}

