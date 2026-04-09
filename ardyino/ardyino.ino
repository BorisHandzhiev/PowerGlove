#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>

Adafruit_MPU6050 mpu;

// --- Radio Setup ---
// CE is on 9, CSN is on 8
RF24 radio(9, 8); 
const byte address[6] = "00001"; // The "channel" we are broadcasting on

// --- Pin Assignments ---
const int VRxPin = A0;
const int VRyPin = A1;
const int joySwPin = 10;      // Moved to 5 because Pinky is on 7!

const int btnIndexPin = 3;
const int btnMiddlePin = 4;
const int btnRingPin = 6;    // Updated!
const int btnPinkyPin = 7;   // Updated!

// --- The Data Packet ---
// This is the exact package we will send over the air.
// The receiver Arduino MUST have this exact same struct to decode it.
struct DataPacket {
  int joyX;
  int joyY;
  float gyroX;
  float gyroY;
  byte btnIndex;
  byte btnMiddle;
  byte btnRing;
  byte btnPinky;
  byte btnJoyClick;
};

DataPacket gloveData; // Create a variable to hold our data

void setup() {
  Serial.begin(115200);

  // 1. Initialize MPU6050
  if (!mpu.begin()) {
    Serial.println("Error: MPU6050 not found!");
    while (1) delay(10);
  }
  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

  // 2. Initialize Buttons (Using internal pull-ups)
  pinMode(btnIndexPin, INPUT_PULLUP);
  pinMode(btnMiddlePin, INPUT_PULLUP);
  pinMode(btnRingPin, INPUT_PULLUP);
  pinMode(btnPinkyPin, INPUT_PULLUP);
  pinMode(joySwPin, INPUT_PULLUP);

  // 3. Initialize NRF24L01 Radio
  if (!radio.begin()) {
    Serial.println("Error: NRF24 not responding! Check wiring.");
    while (1) delay(10);
  }
  
  radio.openWritingPipe(address);
  // Using LOW power is CRITICAL since we aren't using a capacitor on the 3.3V line.
  // This prevents power spikes from crashing the MPU6050.
  radio.setPALevel(RF24_PA_LOW); 
  radio.setDataRate(RF24_1MBPS);
  radio.stopListening(); // Tell it to act as a Transmitter
}

void loop() {
  // 1. Read Joystick
  gloveData.joyX = analogRead(VRxPin);
  gloveData.joyY = analogRead(VRyPin);

  // 2. Read MPU6050 Gyro
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);
  gloveData.gyroX = g.gyro.x;
  gloveData.gyroY = g.gyro.y;

  // 3. Read Buttons (Convert LOW to 1 for "Pressed")
  gloveData.btnIndex = (digitalRead(btnIndexPin) == LOW) ? 1 : 0;
  gloveData.btnMiddle = (digitalRead(btnMiddlePin) == LOW) ? 1 : 0;
  gloveData.btnRing = (digitalRead(btnRingPin) == LOW) ? 1 : 0;
  gloveData.btnPinky = (digitalRead(btnPinkyPin) == LOW) ? 1 : 0;
  gloveData.btnJoyClick = (digitalRead(joySwPin) == LOW) ? 1 : 0;

  // 4. Send Data Wirelessly!
  radio.write(&gloveData, sizeof(DataPacket));

  // Run at ~100Hz
  delay(1000); 
}