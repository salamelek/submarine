// gets serial data and streams it via RF24

#include <Arduino.h>
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

RF24 radio(9,10); // CE, CSN
const byte address[6] = "00001";

unsigned char digitsArray[9];

void setup() {
  Serial.begin(9600);

  // initialise radio
  radio.begin();
  radio.openWritingPipe(address);
  radio.setPALevel(RF24_PA_LOW);
  radio.stopListening();

  Serial.println("Transmitter running...");
}

void printArray(unsigned char *arr, int size) {
  Serial.print("[");
  for (int i = 0; i < size; i++) {
    Serial.print(arr[i]);
    if (i < size - 1) {
      Serial.print(", ");
    }
  }
  Serial.println("]");
}

void loop() {
  if (Serial.available()) {
    String receivedData = Serial.readStringUntil('\n');   // Read the received string
    receivedData.trim();                                  // Remove leading/trailing whitespace
    receivedData.substring(0, 27);                        // Extract the actual string portion (first 9 characters in this example)

    for (int i = 0; i < 9; i++) {
      digitsArray[i] = receivedData.substring(i * 3, i * 3 + 3).toInt();
    }

    radio.write(&digitsArray, sizeof(digitsArray));

    printArray(digitsArray, sizeof(digitsArray));
  }
}
