#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>

Adafruit_MPU6050 mpu;

// Joystick Pins
const int VRxPin = A0;
const int VRyPin = A1;
const int joySwPin = 7; // NEW: Joystick click button

// Button Pins (Index, Middle, Ring, Pinky)
const int numButtons = 4;
const int buttonPins[4] = {3, 4, 12, 13 };

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10); 

  if (!mpu.begin()) {
    Serial.println("Error: MPU6050 not found!");
    while (1) delay(10);
  }
  
  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

  // Initialize finger buttons
  for (int i = 0; i < numButtons; i++) {
    pinMode(buttonPins[i], INPUT_PULLUP);
  }
  
  // Initialize joystick button
  pinMode(joySwPin, INPUT_PULLUP);
}

void loop() {
  // 1. Read Joystick
  int joyX = analogRead(VRxPin);
  int joyY = analogRead(VRyPin);

  // 2. Read MPU6050
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  // 3. Read Buttons (Convert LOW to 1 for "Pressed")
  int btnIndex  = (digitalRead(buttonPins[0]) == LOW) ? 1 : 0;
  int btnMiddle = (digitalRead(buttonPins[1]) == LOW) ? 1 : 0;
  int btnRing   = (digitalRead(buttonPins[2]) == LOW) ? 1 : 0;
  int btnPinky  = (digitalRead(buttonPins[3]) == LOW) ? 1 : 0;
  int btnJoyClick = (digitalRead(joySwPin) == LOW) ? 1 : 0; // NEW: Joystick Click

  // 4. Print as CSV (Now 13 values!)
  Serial.print(joyX); Serial.print(",");
  Serial.print(joyY); Serial.print(",");
  Serial.print(a.acceleration.x); Serial.print(",");
  Serial.print(a.acceleration.y); Serial.print(",");
  Serial.print(a.acceleration.z); Serial.print(",");
  Serial.print(g.gyro.x); Serial.print(",");
  Serial.print(g.gyro.y); Serial.print(",");
  Serial.print(g.gyro.z); Serial.print(",");
  Serial.print(btnIndex); Serial.print(",");
  Serial.print(btnMiddle); Serial.print(",");
  Serial.print(btnRing); Serial.print(",");
  Serial.print(btnPinky); Serial.print(",");
  Serial.println(btnJoyClick); // Moved println to the final value

  delay(10);
}