#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

// --- Radio Setup ---
// CE is on 9, CSN is on 8 (Must match wiring!)
RF24 radio(9, 8); 
const byte address[6] = "00001"; // Must match the transmitter's address

// --- The Data Packet ---
// This MUST be completely identical to the struct in the Transmitter code
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

DataPacket receivedData;

void setup() {
  Serial.begin(115200);
  
  if (!radio.begin()) {
    Serial.println("Error: NRF24 Receiver not responding!");
    while (1) delay(10);
  }
  
  radio.openReadingPipe(0, address);
  radio.setPALevel(RF24_PA_LOW); 
  radio.setDataRate(RF24_1MBPS);
  radio.startListening(); // Tell it to act as a Receiver
}

void loop() {
  if (radio.available()) {
    // Read the incoming wireless packet
    radio.read(&receivedData, sizeof(DataPacket));
    
    // Print the data out as a CSV string to the PC
    // We are now sending exactly 9 values
    Serial.print(receivedData.joyX); Serial.print(",");
    Serial.print(receivedData.joyY); Serial.print(",");
    Serial.print(receivedData.gyroX); Serial.print(",");
    Serial.print(receivedData.gyroY); Serial.print(",");
    Serial.print(receivedData.btnIndex); Serial.print(",");
    Serial.print(receivedData.btnMiddle); Serial.print(",");
    Serial.print(receivedData.btnRing); Serial.print(",");
    Serial.print(receivedData.btnPinky); Serial.print(",");
    Serial.println(receivedData.btnJoyClick); // println for the last value
  }
}