#include <SPI.h>
#include <TinyScreen.h> // This library is used to print sensor values to a TinyScreen.
#include "BMA250.h" // Used to interface with the Accelerometer Wireling, which is used to track steps.
#include <Wire.h>
#include <Wireling.h>
#include <RTClib.h>
#include <SdFat.h> // Enables data to be logged to an SD card.
#include <RTCZero.h>  // Enables date and time to be recorded with each sensor reading.
#include <MAX30101.h> // Used to interface with the Pulse Oximeter sensor.

MAX30101 pulseSensor = MAX30101(); // pulseOx sensor object
BMA250 accel_sensor; // accelerometer sensor object

// SD card variables
#define FILE_BASE_NAME "arduino.csv" // Log file base name. This file will be stored in the SD card. Name of the csv file should be be 13 characters or less.
char fileName[13] = FILE_BASE_NAME;
SdFat SD; // File system object.
SdFile file; // Log file.
const uint8_t ANALOG_COUNT = 4;
const int chipSelect = 10;

// TinyScreen Global Variables
TinyScreen display = TinyScreen(TinyScreenPlus);
int background = TS_8b_Black; // Sets the background color to black.

const int STEP_TRIGGER = 250; // The LRA Wireling will notify you of inactivity if you complete less than half of this number of steps each hour. Step % is based on this * 16 waking hours.
const int DATA_INTERVAL = 5; // Data is recorded to the SD card every 5 seconds.
const bool DEBUG_MD = false; // If set to true, enables debug mode.
const int FAST_DATA_INTERVAL = DATA_INTERVAL * 1000; // Performance optimization.
int stepsTowardGoal = 20; // Keeps track of how many steps you have taken the the past hour as compared to your goal.


// Heart rate, Blood oxygen Level and body temperature concentration variables.
int heartData[2880] = {};
int32_t bufferLength = 50; //Options: 50, 100, 200, 400, 800, 1000, 1600, 3200, the lower the faster the oxygen saturation calculation.
int32_t oxygenLevel; // Blood oxygen level value.
int32_t heartRate; // Heart rate value.
int32_t temperature; // Temperature value.

// Change these values to set the current time when you upload the sketch.
const byte seconds = 45;
const byte minutes = 59;
const byte hours = 23;

// Change these values to set the current initial date.
const byte day = 6;
const byte month = 4;
const byte year = 24;

// Which port is each sensor connected to. initial 0 value represents that they are not connected.
int pulseSensorPort = 2;
int accelSensorPort = 3;

unsigned long stepTimestamps[STEP_TRIGGER] = {};
unsigned long loopStart = 0;
uint32_t doVibrate = 0;
bool firstSD = false;
RTCZero rtc;


// Heart rate variables.
const byte RATE_SIZE = DATA_INTERVAL * 100; // Based on the data interval. This could take a lot of memory.
byte rates[RATE_SIZE]; //heartData of heart rates.
int beatAvg = 0; // Represents the average heart rate over the DATA_INTERVAL.

int stepArr[4] = {};
void initStepTimestamps();
bool validatePorts(); // Validate ports in the Arduino Watch.
int updatePedometer();
void createString(String &, String &, bool); // This will be used to save the Body data in SD card csv file.
void validateSD(String , String , bool ); // Validating the SD card before adding data to the SD card.
int getTotalSteps(); // Gets the total step count.
void displayData(unsigned long &screenClearTime); // Display the collected data live.
void dailyStepReset(); // Reset step data by day.

void setup(void)
{
  Serial.begin(9600);
  delay(5000);
  initStepTimestamps();
  Wire.begin();
  Wireling.begin();

  // Set the cursor to the following coordinates before it prints "BMA250 Test".
  if (accelSensorPort) {
    Wireling.selectPort(accelSensorPort);
    accel_sensor.begin(BMA250_range_4g, BMA250_update_time_16ms); // Sets up the BMA250 accel_sensorerometer
  }

  if (pulseSensorPort)
  {
    Wireling.selectPort(pulseSensorPort);
    pulseSensor.begin();
  }

  // Check for SD card.
  SerialUSB.println("Initializing SD card...");
  if (SD.begin(chipSelect, SD_SCK_MHZ(50)))
  {
    SerialUSB.println("Card Initialized.");
    SerialUSB.print(F("Logging to: "));
    SerialUSB.println(fileName);
    SerialUSB.println();
  }
  else
  {
    SerialUSB.println("SD Card not found. Exiting program.");
    SerialUSB.println();
    delay(5000);
    while (1);
  }

  // Set date and time.
  rtc.begin();
  rtc.setTime(hours, minutes, seconds);
  rtc.setDate(day, month, year);
  unsigned long tempEpoch = rtc.getEpoch();
  int tempHour = rtc.getHours();
  int tempMinute = rtc.getMinutes();
  rtc.setEpoch(tempEpoch); // Reset back to current time.

  // This is the setup used to initialize the TinyScreen's appearance.
  display.begin();
  display.setBrightness(15);
  display.setFlip(true);
  display.setFont(thinPixel7_10ptFontInfo);
  display.fontColor(TS_8b_White, background);

  // Print the current datetime on the serial monitor when initializing the Arduino Watch.
  int yeari = rtc.getYear();
  int monthi = rtc.getMonth();
  int dayi = rtc.getDay();
  int hoursi = rtc.getHours();
  int minutesi = rtc.getMinutes();
  int secondsi = rtc.getSeconds();

  SerialUSB.print("Date: ");
  SerialUSB.print(dayi);
  SerialUSB.print("/");
  SerialUSB.print(monthi);
  SerialUSB.print("/");
  SerialUSB.println(yeari);

  SerialUSB.print("Time: ");
  SerialUSB.print(hoursi);
  SerialUSB.print(":");
  SerialUSB.print(minutesi);
  SerialUSB.print(":");
  SerialUSB.println(secondsi);

}

void loop() {

  String displayString = ""; // Written once in the logfile to provide column headings along with the body data.
  String dataString = ""; // Written to the logfile every data interval seconds. Does not contain headings, just csv data only (row data).
  static unsigned long screenClearTime = millis();
  static int currentHour = rtc.getHours(); // Performance optimization.
  static unsigned long batteryTimer = millis(); // Used to check the battery voltage every 5 seconds.
  static unsigned long goalTimer = millis(); // Used to check if you are meeting your daily goals.

  // These variables are used to keep track of how many steps were taken in recent minutes.
  static unsigned long one = millis();
  static unsigned long two = millis();
  static unsigned long five = millis();
  static unsigned long fifteen = millis();
  static unsigned long oneMinute = millis();

  Wireling.selectPort(pulseSensorPort);  
  checkPulse();
  
  Wireling.selectPort(accelSensorPort);
  updatePedometer();

  // Check if it's time to log data (This logs data into the SD card every 5 seconds by default).
  if (millis() - batteryTimer > FAST_DATA_INTERVAL)
  {
    SerialUSB.print("Current millis(): ");
    SerialUSB.println(millis());
    SerialUSB.print("Previous batteryTimer value: ");
    SerialUSB.println(batteryTimer);
    SerialUSB.print("FAST_DATA_INTERVAL: ");
    SerialUSB.println(FAST_DATA_INTERVAL);

    // Log data here.
    createString(displayString, dataString, firstSD);
    validateSD(dataString, displayString, firstSD);

    // Update batteryTimer to the current millis() value.
    batteryTimer = millis();
  }

  if (millis() - oneMinute > 60000)
  {
    oneMinute = millis();
    // If it is near the end of an hour and you are not on pace to meet your daily step goal.
    if (millis() - goalTimer > 3600000)
    {
      stepsTowardGoal = getTotalSteps() - stepsTowardGoal;
      goalTimer  = millis();
    }
  }

  // Displays data on the TinyScreen+ for the Arduino Watch.
  displayData(screenClearTime);
}

// Function to update the time on the Arduino Watch.
void updateTime(uint8_t *b) {
  int y, M, d, k, m, s;
  char *next;

  // Convert the input string into integer values for year, month, day, hour, minute, and second.
  y = strtol((char *)b, &next, 10);  // Convert year to integer.
  M = strtol(next, &next, 10);       // Convert month to integer.
  d = strtol(next, &next, 10);       // Convert day to integer.
  k = strtol(next, &next, 10);       // Convert hour to integer.
  m = strtol(next, &next, 10);       // Convert minute to integer.
  s = strtol(next, &next, 10);       // Convert second to integer.

  // Set the system time based on the platform (AVR or SAMD).
#if defined (ARDUINO_ARCH_AVR)
  // For AVR architecture (e.g., Arduino Uno), use setTime from TimeLib.h.
  setTime(k, m, s, d, M, y);
#elif defined(ARDUINO_ARCH_SAMD)
  // For SAMD architecture (e.g., Arduino Zero), use RTCZero library for RTC management.
  rtc.setTime(k, m, s);                  // Set time (hour, minute, second).
  rtc.setDate(d, M, y - 2000);           // Set date (day, month, year).
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

// Function to calculate daily step goal in percentage.
float percentOfDailyStepGoal(int totalSteps)
{
  const float DAILY_GOAL = (float)STEP_TRIGGER * 16.00; // 16 waking hours in day.
  if (DEBUG_MD) {
    SerialUSB.print("total steps: ");
    SerialUSB.println(totalSteps);
    SerialUSB.print("total steps %: ");
    SerialUSB.println((totalSteps / DAILY_GOAL) * 100.00);
  }
  return (totalSteps / DAILY_GOAL) * 100.00;
}

// Calculate the battery voltage.
float getBattVoltage(void) {
  const int VBATTpin = A4;
  float VCC = getVCC();

  // Use resistor division and math to get the voltage.
  float resistorDiv = 0.5;
  float ADCres = 1023.0;
  float battVoltageReading = analogRead(VBATTpin);
  battVoltageReading = analogRead(VBATTpin); // Throw out first value.
  float battVoltage = VCC * battVoltageReading / ADCres / resistorDiv;

  return battVoltage;
}

// This function gets the battery VCC internally, to find out more:
// http://atmel.force.com/support/articles/en_US/FAQ/ADC-example

float getVCC() {
  SYSCTRL->VREF.reg |= SYSCTRL_VREF_BGOUTEN;
  while (ADC->STATUS.bit.SYNCBUSY == 1);
  ADC->SAMPCTRL.bit.SAMPLEN = 0x1;
  while (ADC->STATUS.bit.SYNCBUSY == 1);
  ADC->INPUTCTRL.bit.MUXPOS = 0x19; // Internal bandgap input.
  while (ADC->STATUS.bit.SYNCBUSY == 1);
  ADC->CTRLA.bit.ENABLE = 0x01; // Enable ADC.
  while (ADC->STATUS.bit.SYNCBUSY == 1);
  ADC->SWTRIG.bit.START = 1; // Start conversion
  ADC->INTFLAG.bit.RESRDY = 1; // Clear the Data Ready flag.
  while (ADC->STATUS.bit.SYNCBUSY == 1);
  ADC->SWTRIG.bit.START = 1;  // Start the conversion again to throw out first value.
  while ( ADC->INTFLAG.bit.RESRDY == 0 ); // Waiting for conversion to complete.
  uint32_t valueRead = ADC->RESULT.reg;
  while (ADC->STATUS.bit.SYNCBUSY == 1);
  ADC->CTRLA.bit.ENABLE = 0x00; // Disable ADC.
  while (ADC->STATUS.bit.SYNCBUSY == 1);
  SYSCTRL->VREF.reg &= ~SYSCTRL_VREF_BGOUTEN;
  float vcc = (1.1 * 1023.0) / valueRead;
  return vcc;
}

// Function to calculate and get the battery percentage.
float getBatteryPercent()
{
  float batteryLeft = max((getBattVoltage() - 3.00), 0);
  if (DEBUG_MD) {
    SerialUSB.print("battery left: ");
    // SerialUSB.println(min(batteryLeft * 83.333333, 100));
  }
  return min((batteryLeft * 83.333333), 100); // Hard upper limit of 100 as it often shows over 100 when charging.
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

// Function for checking the heart rate and blood oxygen percentage. Body temperature is also included as an extra feature.
void checkPulse()
{
  if (pulseSensor.update()) {
    if (pulseSensor.pulseValid()) {
      beatAvg = pulseSensor.BPM();
      oxygenLevel = pulseSensor.oxygen();
      temperature = pulseSensor.temperature();
      SerialUSB.println("beatAvg, oxy, temp");
      SerialUSB.println(beatAvg);
      SerialUSB.println(oxygenLevel);
      SerialUSB.println(temperature);
    }
  }
}

// Function used for validating the SD cards existance before logging data into it.
void validateSD(String dataString, String displayString, bool firstSD)
{
  if (!file.open(fileName, O_CREAT | O_RDWR | O_APPEND)) {
    SerialUSB.println("File open error.");
  }
  else
  {
    // If the file is available, write to it.
    logData(dataString, displayString);
  }

  // Force data to SD and update the directory entry to avoid data loss.
  if (!file.sync() || file.getWriteError()) {
    SerialUSB.println("write error");
  }
  file.close();
}

// Function that writes body data collected by the Arduino Watch to the SD card (in arduino.csv).
void logData(String dataString, String displayString) {
  uint16_t data[ANALOG_COUNT];

  // Read all channels to avoid SD write latency between readings.
  for (uint8_t i = 0; i < ANALOG_COUNT; i++) {
    data[i] = analogRead(i);
  }

  if (DEBUG_MD) {
    SerialUSB.println("WRITING TO FILE!!");
  }

  if (firstSD) {
    // If it's the first time writing to the file, write column headings.
    file.println(displayString);
    // Set firstSD to false after writing column headings.
    firstSD = false;
  }

  // Append dataString (which contains the data row) to the file.
  file.println(dataString);

  if (DEBUG_MD) {
    SerialUSB.println("WRITING Complete!");
    SerialUSB.print("dataString: ");
    SerialUSB.println(dataString);
  }
}

// Creates data strings using the body data collected, that is then saved into the SD card, in csv format.
void createString(String &displayString, String &dataString, bool firstSD) {
  int totalSteps = getTotalSteps();
  unsigned long epoch = rtc.getEpoch();
  int totalStepsPercent = percentOfDailyStepGoal(totalSteps);
  int batteryPercent = getBatteryPercent();
  
  // Get current date and time from RTC.
  int year = rtc.getYear();
  int month = rtc.getMonth();
  int day = rtc.getDay();
  int hours = rtc.getHours();
  int minutes = rtc.getMinutes();
  int seconds = rtc.getSeconds();
  
  // Construct column headings.
  if (firstSD) {
    displayString += "epoch_time,datetime,step_count,step_goal_percent,heart_rate,oxygen_level,temperature_celsius,battery_percent";
    firstSD = false; // Set firstSD to false after writing column headings.
  }
  
  // Construct datetime string in format "YY-MM-DD HH:MM:SS".
  String datetime = twoDigits(year) + "-" + twoDigits(month) + "-" + twoDigits(day) + " " +
                    twoDigits(hours) + ":" + twoDigits(minutes) + ":" + twoDigits(seconds);
  
  // Construct data row string.
  dataString += String(epoch);
  dataString += ",";
  dataString += datetime;
  dataString += ",";
  dataString += String(totalSteps);
  dataString += ",";
  dataString += String(totalStepsPercent);
  dataString += ",";
  dataString += String(beatAvg);
  dataString += ",";
  dataString += String(oxygenLevel);
  dataString += ",";
  dataString += String(temperature);
  dataString += ",";
  dataString += String(batteryPercent);
}

String twoDigits(int number) {
  if (number < 10) {
    return "0" + String(number);
  } else {
    return String(number);
  }
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

// Function to display the data collected by the Arduino Watch on the TinyScreen+.
void displayData(unsigned long &screenClearTime)
{
    int totalSteps = getTotalSteps();
    int totalStepsPercent = percentOfDailyStepGoal(totalSteps);
    int batteryPercent = getBatteryPercent();

    if (rtc.getSeconds() == 0 && millis() - screenClearTime > 1000) {
        display.clearScreen();
        screenClearTime = millis();
    }

    // Turn on the display.
    display.on();
    
    display.setCursor(0, 0);
    display.print(rtc.getDay());
    display.print("/");
    display.print(rtc.getMonth());
    display.print("/");
    display.print(rtc.getYear());
    display.print(" ");
    display.print(rtc.getHours());
    display.print(":");
    display.print(rtc.getMinutes());
    display.print(":");
    display.print(rtc.getSeconds());

    display.setCursor(0, 10);
    display.print("Steps: ");
    display.println(totalSteps);

    display.setCursor(0, 20);
    display.print("Steps %: ");
    display.println(totalStepsPercent);

    display.setCursor(0, 30);
    display.print("Heart Rate: ");
    display.println(beatAvg);

    display.setCursor(0, 40);
    display.print("Oxygen Level: ");
    display.println(oxygenLevel);

    display.setCursor(0, 50);
    display.print("Battery %: ");
    display.println(batteryPercent);
}
