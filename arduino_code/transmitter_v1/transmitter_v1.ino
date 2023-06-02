// gets data from pc serial and sends it

#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

RF24 radio(9,10); // CE, CSN
const byte address[6] = "00001";

void setup() {
  Serial.begin(9600);

  // initialise radio
  radio.begin();
  radio.openWritingPipe(address);
  radio.setPALevel(RF24_PA_LOW);
  radio.stopListening();
  
  Serial.println("Transmitter running...");
}

void loop() {
  if (Serial.available()) {
    char command = Serial.read();
    
    radio.write(&command, sizeof(command));
  }
}
