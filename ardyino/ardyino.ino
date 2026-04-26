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
const byte address[6] = "00001"; 
  
// --- Pin Assignments ---
const int VRxPin = A0;
const int VRyPin = A1;
const int joySwPin = 10;      

const int btnIndexPin = 3;
const int btnMiddlePin = 4;
const int btnRingPin = 6;    
const int btnPinkyPin = 7;   

// --- The Data Packet ---
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

DataPacket gloveData; 

// --- Timer for Serial Printing ---
unsigned long lastPrintTime = 0;
const int printInterval = 200; // Print every 200ms

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10); // Wait for Serial Monitor to open

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
  radio.setPALevel(RF24_PA_LOW); 
  radio.setDataRate(RF24_1MBPS);
  radio.stopListening(); 

  Serial.println("Glove Transmitter Initialized.");
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

  // 3. Read Buttons (Convert LOW/Pressed to 1)
  gloveData.btnIndex = (digitalRead(btnIndexPin) == LOW) ? 1 : 0;
  gloveData.btnMiddle = (digitalRead(btnMiddlePin) == LOW) ? 1 : 0;
  gloveData.btnRing = (digitalRead(btnRingPin) == LOW) ? 1 : 0;
  gloveData.btnPinky = (digitalRead(btnPinkyPin) == LOW) ? 1 : 0;
  gloveData.btnJoyClick = (digitalRead(joySwPin) == LOW) ? 1 : 0;
  
  // 4. Send Data Wirelessly
  // radio.write returns true if the packet was acknowledged by the receiver
  bool report = radio.write(&gloveData, sizeof(DataPacket));

  // 5. Debug Printing (Limited so it doesn't slow down the loop)
  if (millis() - lastPrintTime >= printInterval) {
    lastPrintTime = millis();

    if (report) {
      Serial.print("[OK] ");
    } else {
      Serial.print("[FAIL] ");
    }

    Serial.print("JX:"); Serial.print(gloveData.joyX);
    Serial.print(" JY:"); Serial.print(gloveData.joyY);
    Serial.print(" GX:"); Serial.print(gloveData.gyroX, 1);
    Serial.print(" GY:"); Serial.print(gloveData.gyroY, 1);
    Serial.print(" BTNS:");
    Serial.print(gloveData.btnIndex);
    Serial.print(gloveData.btnMiddle);
    Serial.print(gloveData.btnRing);
    Serial.print(gloveData.btnPinky);
    Serial.println(gloveData.btnJoyClick);
  }

  // Loop delay for ~100Hz frequency
  delay(10); 
}