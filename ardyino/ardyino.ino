#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>

Adafruit_MPU6050 mpu;

void setup(void) {
  Serial.begin(115200);
  
  while (!Serial)
    delay(10); 

  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip. Check your wiring!");
    while (1) {
      delay(10);
    }
  }
  
  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
  
  Serial.println("MPU6050 Ready! Tilt to test.");
  delay(100);
}

void loop() {
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  float tiltThreshold = 4.0; 

  // --- X-AXIS (Left / Right) ---
  if (a.acceleration.x > tiltThreshold) {
    Serial.println("W");
  } 
  else if (a.acceleration.x < -tiltThreshold) {
    Serial.println("S");
  } 

  // --- Y-AXIS (Up / Down) ---
  if (a.acceleration.y > tiltThreshold) {
    Serial.println("D");
  } 
  else if (a.acceleration.y < -tiltThreshold) {
    Serial.println("A");
  }

  // Wait 100 milliseconds before reading again
  delay(100);
}