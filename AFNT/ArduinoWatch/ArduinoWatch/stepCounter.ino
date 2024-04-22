bool validStepPattern = false;
int stepIntervalLow = 200;
unsigned long stepIntervalHigh = 2000;
unsigned long lastStepTime = 0;

const int amtSamples = 32;
int aBuff[amtSamples];
int aBuffPos = 0;
unsigned long sampleInterval = 20;
unsigned long lastSample = 0;
int sampleNew = 0;
int sampleOld = 0;
int precision = 10;
bool halfStep = false;
bool stepAlert = false;

//int X, Y, Z, A, mX, mY, mZ;

int totalSteps = 0;

int isValidStepPattern() {
  return validStepPattern;
}

int getTotalSteps() {
  return totalSteps;
}

int getStepTrigger() {
  return STEP_TRIGGER;
}

int updatePedometer() {
  // Record the current time
  lastSample = millis();

  // Read new data from the accelerometer
  accel_sensor.read();

  // Calculate the magnitude (A) of the acceleration vector
  int sum = pow(accel_sensor.X, 2);
  sum += pow(accel_sensor.Y, 2);
  sum += pow(accel_sensor.Z, 2);
  int A = sqrt(sum);

  // Compute the difference between the current and previous acceleration magnitudes
  int difference = abs(A - sampleOld);

  // Apply filtering to smooth out small changes
  if (difference < 10) {
    difference = 0;
  }
  if (difference > 30) {
    difference = 30;
  }

  // Determine the sign of the change in acceleration magnitude
  if (A - sampleOld > 0) {
    difference = sampleOld + difference;
  } else {
    difference = sampleOld - difference;
  }

  // Store the difference in the acceleration buffer
  aBuff[aBuffPos] = difference;

  // Find the minimum and maximum values in the acceleration buffer
  int Amin = 1000;
  int Amax = 0;
  for (int i = 0; i < amtSamples; i++) {
    int sampleVal = aBuff[i];
    if (sampleVal < Amin) Amin = sampleVal;
    if (sampleVal > Amax) Amax = sampleVal;
  }

  // Calculate the peak-to-peak value and set a threshold
  int peakToPeak = Amax - Amin;
  int threshold = (peakToPeak / 2) + Amin;

  // Update the previous sample value
  sampleOld = sampleNew;

  // Check for a potential new step based on acceleration changes
  bool newStep = false;
  if (abs(sampleNew - difference) > precision) {
    sampleNew = difference;
    if (peakToPeak > 70 && sampleOld > threshold && sampleNew < threshold) {
      // Check if the step falls within a valid time interval
      if (validStepPattern) {
        if (millis() > lastStepTime + stepIntervalLow && millis() < lastStepTime + stepIntervalHigh) {
          newStep = true;
        } else {
          validStepPattern = false;
        }
      } else if (millis() > lastStepTime + stepIntervalLow && millis() < lastStepTime + stepIntervalHigh) {
        newStep = true;
        validStepPattern = true;
      }
      // Update the last step time and increment the step count
      lastStepTime = millis();
      if (newStep) {
        if (false) {
          stepAlert = true;
        }
        totalSteps++;
        // Display the total steps on the serial monitor
        SerialUSB.print("totalSteps:  ");
        SerialUSB.println(totalSteps);
        // Add the timestamp of the most recent step to the timestamps array
        stepTimestamps[firstMinusOne()] = millis();
      }
    }
  }

  // Update the buffer position and reset if necessary
  aBuffPos++;
  if (aBuffPos >= amtSamples) {
    aBuffPos = 0;
  }

  // Return 1 if a new step is detected, otherwise return 0
  if (newStep /*&& (totalSteps & 1) == 0*/) {
    return 1;
  }
  return 0;
}


int firstMinusOne() // returns the index in the stepTimestamps array that the next recorded step timestamp will be stored in
{
  for (int i = 0; i < getStepTrigger(); ++i) {
    // If all array values have not been previously used, then we want to place the most recent value in the first position containing 4294967295
    if (stepTimestamps[i] == 4294967295) {
      return i;
    } else if (i == getStepTrigger() - 1) // if all array values have been previously used, then we want to shift array to the left and add the most recent value in the final position
    {
      //SerialUSB.print("Second branch: ");
      //SerialUSB.println(i);
      shiftLeft();
      return i;
    }
  }
}

void initStepTimestamps() {
  for (int i = 0; i < getStepTrigger(); ++i) {
    stepTimestamps[i] = 4294967295;
  }
}

void shiftLeft() {
  for (int i = 1; i < getStepTrigger(); ++i) {
    stepTimestamps[i - 1] = stepTimestamps[i];
  }
  stepTimestamps[getStepTrigger() - 1] = 4294967295;
}

void serialStepTimestamps() {
  for (int i = 0; i < 250; ++i) {
    SerialUSB.print(i);
    SerialUSB.print(": ");
    SerialUSB.println(stepTimestamps[i]);
  }
}

bool getStepAlert() {
  return stepAlert;
}

void resetStepAlert() {
  stepAlert = false;
}