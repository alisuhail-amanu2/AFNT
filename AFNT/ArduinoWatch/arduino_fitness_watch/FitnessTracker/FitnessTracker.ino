#include <SPI.h>
#include <TinyScreen.h> // This library is used to print sensor values to a TinyScreen
#include "BMA250.h" // Used to interface with the acceleromter Wireling, which is used to track your steps
#include <Wire.h>
#include <Wireling.h>
#include <RTClib.h>
#include "Adafruit_DRV2605.h" // used to interface with the LRA Wireling
#include <SdFat.h> // enables data to be logged to an sd card
#include <RTCZero.h>  // enables date and time to be recorded with each sensor reading
#include <MAX30101.h> // used to interface with the pulse oximetry sensor
using namespace std;
// RTC_DS3231 rtcd;

Adafruit_DRV2605 drv; // lra sensor object
MAX30101 pulseSensor = MAX30101(); // pulseOx sensor object
BMA250 accel_sensor; // accelerometer sensor object

// SD card variables
#define FILE_BASE_NAME "arduino.csv" // Log file base name.  Must be 13 characters or less.
char fileName[13] = FILE_BASE_NAME;
SdFat SD; // File system object.
SdFile file; // Log file.
const uint8_t ANALOG_COUNT = 4;
const int chipSelect = 10;

// TinyScreen Global Variables
TinyScreen display = TinyScreen(TinyScreenPlus);
int background = TS_8b_Black; // sets the background color to black

const int STEP_TRIGGER = 250; // The LRA Wireling will notify you of inactivity if you complete less than half of this number of steps each hour. Step % is based on this * 16 waking hours.
const int DATA_INTERVAL = 5; // data is recorded to the microSD every DATA_INTERVAL seconds
const bool DEBUG_MD = false; // if set to true, enables debug mode
const int FAST_DATA_INTERVAL = DATA_INTERVAL * 1000; // performance optimization
int stepsTowardGoal = 0; // keeps track of how many steps you have taken the the past hour as compared to your goal. This will trigger inactivity pulses on the LRA


// heart rate and oxygen concentration variables
int heartData[2880] = {};
int32_t bufferLength = 50; //Options: 50, 100, 200, 400, 800, 1000, 1600, 3200, the lower the faster the oxygen saturation calculation
int32_t saturatedOxygen; //saturatedOxygen value
int32_t heartRate; //heart rate value
int32_t temperature; //temperature value

// DateTime now = rtcd.now();
/* Change these values to set the current time when you upload the sketch. */
const byte seconds = 4;
const byte minutes = 4;
const byte hours = 4;

/* Change these values to set the current initial date */
const byte day = 24;
const byte month = 1;
const byte year = 2032;

// set your approximate bedtime. Your sleep quality score will be most accurate if you go to bed at this time.
// However, there is a variable time window (UP TO 30 MINUTES,you can change this number by modifying BEDTIME_ALLOWANCE) after this bedtime that will be exempt from the sleep quality calculation if you are quite active.
// The threshold to start calculating sleep quality is that the accelerometer cannot have detected more than 10 steps in the last 2 minutes. If at any point after the sleep quality calculation begins
// there is a minute with more than 15 steps, the sleep quality calculation will be reset and the entry condition of <= 10 steps in the last 2 minutes must be met again.
// At BEDTIME_ALLOWANCE minutes after your bedtime, sleep quality calculation will begin regardless of your activity level.
const int BEDTIME_HOUR = 23; // use 24 hour time only.
const int BEDTIME_MINUTE = 53;
const int BEDTIME_ALLOWANCE = 30; // see above

// used to store which sensors are connected and if so, what port they are connected to. initial 0 value represents that they are not connected
const float memsPin = A0; // used for microphone
int pulseSensorPort = 1;
int accelSensorPort = 3;

unsigned long stepTimestamps[STEP_TRIGGER] = {};
unsigned long loopStart = 0;
uint32_t doVibrate = 0;
bool firstSD = true;
#include <RTCZero.h>
RTCZero rtc;


// heart rate variables
const byte RATE_SIZE = DATA_INTERVAL * 100; // Based on the data interval. this could take a lot of memory
byte rates[RATE_SIZE]; //heartDataay of heart rates
int beatAvg = 0; // represents the average heart rate over the DATA_INTERVAL

unsigned long bedtimeEpoch = 0;
int stepArr[4] = {};

void initStepTimestamps();
bool validatePorts();
int updatePedometer();
void createString(String &, String &, bool , int , bool &, unsigned long &);
void validateSD(String , String , bool );
int getTotalSteps();
void checkButtons(unsigned long &screenClearTime);
void dailyStepReset();

void setup(void)
{
  SerialUSB.begin(115200);
  //while (!SerialUSB);
  delay(5000); // replaces the above
  initStepTimestamps();
  Wire.begin();
  Wireling.begin();

//  checkPorts(); // determines what Wireling is attached to which port, if any
//  if (!validatePorts()) {
//    SerialUSB.println("Critical error with port assignment, please assign ports manually!");
//  }

  if (accelSensorPort) {
    // Set the cursor to the following coordinates before it prints "BMA250 Test"
    Wireling.selectPort(accelSensorPort);
    accel_sensor.begin(BMA250_range_4g, BMA250_update_time_16ms); // Sets up the BMA250 accel_sensorerometer
  }

  if (pulseSensorPort)
  {
    Wireling.selectPort(pulseSensorPort);
    pulseSensor.begin(); //Configure sensor with default settings
  }

  // Check for SD card
  SerialUSB.println("Initializing SD card...");
  if (SD.begin(chipSelect, SD_SCK_MHZ(50)))
  {
    SerialUSB.println("card initialized.");

    SerialUSB.print(F("Logging to: "));
    SerialUSB.println(fileName);
    SerialUSB.println();
  }
  else
  {
    SerialUSB.println("SD Card not found, exiting program!");
    SerialUSB.println();
    delay(5000);
    while (1);
  }

  rtc.begin();
  rtc.setTime(hours, minutes, seconds);//h,m,s
  rtc.setDate(day, month, year);//d,m,y
  unsigned long tempEpoch = rtc.getEpoch();
  int tempHour = rtc.getHours();
  int tempMinute = rtc.getMinutes();
  rtc.setTime(BEDTIME_HOUR, BEDTIME_MINUTE, 0);
  if (BEDTIME_HOUR < tempHour || (BEDTIME_HOUR == tempHour && BEDTIME_MINUTE < tempMinute))
  {
    bedtimeEpoch = rtc.getEpoch() + 86400;
  }
  else {
    bedtimeEpoch = rtc.getEpoch();
  }
  rtc.setEpoch(tempEpoch); // reset back to current time
  unsigned long epochDiff = (max(bedtimeEpoch, tempEpoch) - min(bedtimeEpoch, tempEpoch));

  // This is the setup used to initialize the TinyScreen's appearance
  display.begin();
  display.setBrightness(15);
  display.setFlip(true);
  display.setFont(thinPixel7_10ptFontInfo);
  display.fontColor(TS_8b_White, background);
}


void loop() {
  String displayString = ""; // written once in the logfile to provide column headings along with the data
  String dataString = ""; // written to the logfile every data interval seconds. does not contain headings, just csv data only. see createstring for more details
  static int emptyIntsCounter = 0;
  static unsigned long validationEpoch = 0; // represents the hour you fell asleep
  static unsigned long screenClearTime = millis();
  static int currentHour = rtc.getHours(); // performance optimization
  static bool validatedPreviously = false; // avoids the need to constantly validate whether it is past bedtime or not by store the fact within this variable.
  // note that the many areas of the sketch are not executed except at night when calculating or recording sleep quality.
  static unsigned long batt = millis(); // used to check the battery voltage and run some other code every data reporting inverval, default 30 seconds
  static unsigned long goalTimer = millis(); // used to check if you are meeting your daily goals
  static int heartIndex = 0;
  // these variables are used to keep track of how many steps were taken in recent minutes
  static unsigned long one = millis();
  static unsigned long two = millis();
  static unsigned long five = millis();
  static unsigned long fifteen = millis();
  static unsigned long oneMinute = millis();

  int micReading = analogRead(memsPin); // example of how you would check for and reference the MEMS microphone Wireling

  Wireling.selectPort(pulseSensorPort);  
  checkPulse();
  
  Wireling.selectPort(accelSensorPort);
  updatePedometer();
  if (millis() - batt > FAST_DATA_INTERVAL) // record battery voltage when needed
  {
    createString(displayString, dataString, firstSD, currentHour, validatedPreviously, validationEpoch); //create strings from recent data

  }

  if (millis() - oneMinute > 60000)
  {
    // sleepMovement(one, two, five, fifteen);
    oneMinute = millis();
    if (millis() - goalTimer > 3600000) // if it is near the end of an hour and you are not on pace to meet your daily step goal
    {
      stepsTowardGoal = getTotalSteps() - stepsTowardGoal;
      // if (stepsTowardGoal < STEP_TRIGGER * 0.5) // you have completed less than half the of the steps you would need to have completed in the past hour to be on pace to meet your goal.
      // {
      //   // buzzLRA(); // inactivity buzz
      // }
      goalTimer  = millis();
    }
  }

  checkButtons(screenClearTime); // will activate display if user presses any button on the TS+
}

void updateTime(uint8_t * b) {
  int y, M, d, k, m, s;
  char * next;
  y = strtol((char *)b, &next, 10);
  M = strtol(next, &next, 10);
  d = strtol(next, &next, 10);
  k = strtol(next, &next, 10);
  m = strtol(next, &next, 10);
  s = strtol(next, &next, 10);
#if defined (ARDUINO_ARCH_AVR)
  setTime(k, m, s, d, M, y);
#elif defined(ARDUINO_ARCH_SAMD)
  rtc.setTime(k, m, s);
  rtc.setDate(d, M, y - 2000);
#endif
}

int minutesMS(int input)
{
  return input * 60000;
}

int minutesLeftInHour()
{
  return 60 - rtc.getMinutes();
}

int getStepTrigger()
{
  return STEP_TRIGGER;
}

float percentOfDailyStepGoal(int totalSteps)
{
  const float DAILY_GOAL = (float)STEP_TRIGGER * 16.00; // 16 waking hours in day
  if (DEBUG_MD) {
    SerialUSB.print("total steps: ");
    SerialUSB.println(totalSteps);
    SerialUSB.print("total steps %: ");
    SerialUSB.println((totalSteps / DAILY_GOAL) * 100.00);
  }
  return (totalSteps / DAILY_GOAL) * 100.00;
}

// Calculate the battery voltage
float getBattVoltage(void) {
  const int VBATTpin = A4;
  float VCC = getVCC();

  // Use resistor division and math to get the voltage
  float resistorDiv = 0.5;
  float ADCres = 1023.0;
  float battVoltageReading = analogRead(VBATTpin);
  battVoltageReading = analogRead(VBATTpin); // Throw out first value
  float battVoltage = VCC * battVoltageReading / ADCres / resistorDiv;

  return battVoltage;
}

// This function gets the battery VCC internally, you can checkout this link
// if you want to know more about how:
// http://atmel.force.com/support/articles/en_US/FAQ/ADC-example
float getVCC() {
  SYSCTRL->VREF.reg |= SYSCTRL_VREF_BGOUTEN;
  while (ADC->STATUS.bit.SYNCBUSY == 1);
  ADC->SAMPCTRL.bit.SAMPLEN = 0x1;
  while (ADC->STATUS.bit.SYNCBUSY == 1);
  ADC->INPUTCTRL.bit.MUXPOS = 0x19;         // Internal bandgap input
  while (ADC->STATUS.bit.SYNCBUSY == 1);
  ADC->CTRLA.bit.ENABLE = 0x01;             // Enable ADC
  while (ADC->STATUS.bit.SYNCBUSY == 1);
  ADC->SWTRIG.bit.START = 1;  // Start conversion
  ADC->INTFLAG.bit.RESRDY = 1;  // Clear the Data Ready flag
  while (ADC->STATUS.bit.SYNCBUSY == 1);
  ADC->SWTRIG.bit.START = 1;  // Start the conversion again to throw out first value
  while ( ADC->INTFLAG.bit.RESRDY == 0 );   // Waiting for conversion to complete
  uint32_t valueRead = ADC->RESULT.reg;
  while (ADC->STATUS.bit.SYNCBUSY == 1);
  ADC->CTRLA.bit.ENABLE = 0x00;             // Disable ADC
  while (ADC->STATUS.bit.SYNCBUSY == 1);
  SYSCTRL->VREF.reg &= ~SYSCTRL_VREF_BGOUTEN;
  float vcc = (1.1 * 1023.0) / valueRead;
  return vcc;
}

float getBattPercent()
{
  float batteryLeft = max((getBattVoltage() - 3.00), 0);
  if (DEBUG_MD) {
    SerialUSB.print("battery left: ");
    SerialUSB.println(min(batteryLeft * 83.333333, 100));
  }
  return min((batteryLeft * 83.333333), 100); // hard upper limit of 100 as it often shows over 100 when charging
}

int stepsInPastXMinutes(int x)
{
  if (x == 1)
  {
    return stepArr[0];
  }
  else if (x == 2)
  {
    return stepArr[1];
  }
  else if (x == 5)
  {
    return stepArr[2];
  }
  else if (x == 15)
  {
    return stepArr[3];
  }
  else
  {
    SerialUSB.println("Critical Error: stepsInPastXMinutes expected a different input");
  }
}

void checkPulse()
{
    if (pulseSensor.update()) {
      if (pulseSensor.pulseValid()) {
        beatAvg = pulseSensor.BPM();
        saturatedOxygen = pulseSensor.oxygen();
        temperature = pulseSensor.temperature();
        SerialUSB.println("beatAvg, oxy, temp");
        SerialUSB.println(beatAvg);
        SerialUSB.println(saturatedOxygen);
        SerialUSB.println(temperature);

      }
    }
}


void validateSD(String dataString, String displayString, bool firstSD)
{
  if (!file.open(fileName, O_CREAT | O_RDWR | O_APPEND)) {
    SerialUSB.println("File open error!");
  }
  else
  {
    // if the file is available, write to it:
    logData(dataString, displayString);
  }

  // Force data to SD and update the directory entry to avoid data loss.
  if (!file.sync() || file.getWriteError()) {
    SerialUSB.println("write error");
  }
  file.close();
}

// Log a data record.
void logData(String dataString, String displayString) {
  uint16_t data[ANALOG_COUNT];

  // Read all channels to avoid SD write latency between readings.
  for (uint8_t i = 0; i < ANALOG_COUNT; i++) {
    data[i] = analogRead(i);
  }
  if (DEBUG_MD) {
    SerialUSB.println("WRITING TO FILE!!");
  }
 if (firstSD)
  {
    file.println(displayString);
    firstSD = false;
  }
  else if (firstSD == false) {
    file.println(dataString);
  }
  if (DEBUG_MD) {
    SerialUSB.println("WRITING Complete!");
    SerialUSB.print("dataString: ");
    SerialUSB.println(dataString);
  }
}

void createString(String &displayString, String &dataString, bool firstSD, int currentHour, bool &validatedPreviously, unsigned long &validationEpoch) {
  int total = getTotalSteps();
  unsigned long epoch = rtc.getEpoch();
  int percent = percentOfDailyStepGoal(total);
  int battery = getBattPercent();
  if (firstSD) // only the first line will look like this so that you know what data is in each column
  {
    // SerialUSB.println("writing column heading ...");
    displayString += "epochTime: ";
    displayString += String(epoch);
    displayString += ",";
    
    // displayString += " stepCount: ";
    // displayString += String(total);
    // displayString += ",";
    
    // displayString += " stepPercent: ";
    // displayString += String(percent);
    // displayString += ",";
    
    // displayString += " pulse: ";
    // displayString += String(beatAvg); // represents the average pulse recorded since the last time file was written to
    // displayString += ",";
    
    // Wireling.selectPort(pulseSensorPort);
    // displayString += " Oxygen Saturation: ";
    // displayString += ",";
    
    // Wireling.selectPort(accelSensorPort);
    // displayString += " batt: ";
    // SerialUSB.println("wrote column heading ...");
  }
  else
  {
    dataString += String(epoch);
    dataString += ",";
    // dataString += String(total);
    // dataString += ",";
    // dataString += String(percent);
    // dataString += ",";
    // dataString += String(beatAvg);
    // dataString += ",";
    // Wireling.selectPort(pulseSensorPort);
    // dataString += String(saturatedOxygen);
    // dataString += ",";
    // Wireling.selectPort(accelSensorPort);
    // dataString += String(battery);
    // SerialUSB.println("wrote data ...");
  }
}

String getFirst(int &emptyIntsCounter)
{
  //sorting - ASCENDING ORDER
  for (int i = 0; i < 2880; i++)
  {
    for (int j = i + 1; j < 2880; j++)
    {
      if (heartData[i] > heartData[j])
      {
        int temp  = heartData[i];
        heartData[i] = heartData[j];
        heartData[j] = temp;
      }
    }
  }

  for (int i = 0; i < 2880; ++i)
  {
    if (heartData[i] == 0)
    {
      ++emptyIntsCounter;
    }
  }
  return String(max(10, heartData[(int)((2880 - emptyIntsCounter) * 0.25) + emptyIntsCounter])); // after the array is sorted, we know the index of the first quartile after adjusting for unfilled array positions characterized by 0's
}

void resetHeartData()
{
  for (int i = 0; i < 2880; ++i)
  {
    heartData[i] = 0;
  }
}

void resetStepCounters()
{
  for (int i = 0; i < 4; ++i)
  {
    stepArr[i] = 0;
  }
  stepsTowardGoal = 0;
}

void checkButtons(unsigned long &screenClearTime)
{
   if(display.getButtons(TSButtonUpperLeft) || display.getButtons(TSButtonUpperRight) || display.getButtons(TSButtonLowerLeft) || display.getButtons(TSButtonLowerRight))
   {
    int total = getTotalSteps();
    int percent = percentOfDailyStepGoal(total);
    int battery = getBattPercent();
     if(rtc.getSeconds() == 0 && millis()-screenClearTime > 1000){
    display.clearScreen();
    screenClearTime = millis();
   }
    display.on();
    display.setCursor(0,0);
    display.print(rtc.getMonth());
    display.print("/");
    display.print(rtc.getDay());
    display.print("/");
    display.print(rtc.getYear());
    display.print(" ");
    display.print(rtc.getHours());
    display.print(":");
    display.print(rtc.getMinutes());
    display.print(":");
    display.print(rtc.getSeconds());
    display.setCursor(0,10);
    display.print("Steps: ");
    display.println(total);
    display.setCursor(0,20);
    display.print("Step %: "); 
    display.println(percent);
    display.setCursor(0,30);
    display.print("Heart Rate: ");
    display.println(beatAvg);
    display.setCursor(0,40);
    display.print("Oxygen: ");
    display.println(saturatedOxygen);
    display.setCursor(0,50);
    display.print("Battery %: ");
    display.println(battery);
    
   }
   else
   {
     display.off();
   }
}