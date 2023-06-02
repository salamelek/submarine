#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

RF24 radio(9,10); // CE, CSN
const byte address[6] = "00001";
char data[32];

void setup() {
  Serial.begin(9600);

  radio.begin();
  radio.openReadingPipe(1,address);
  radio.setPALevel(RF24_PA_LOW);
  radio.startListening();

  Serial.println("Reciever running...");
}

void loop() {
  if(radio.available()) {
    radio.read(&data, sizeof(data));
    Serial.println(data);
  }
}
