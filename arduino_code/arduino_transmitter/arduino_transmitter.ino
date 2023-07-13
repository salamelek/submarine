#include <Arduino.h>

void setup() {
  Serial.begin(9600);
}

void loop() {
  if (Serial.available()) {
    String receivedData = Serial.readStringUntil('\n');   // Read the received string
    receivedData.trim();                                  // Remove leading/trailing whitespace
    receivedData.substring(0, 30);                        // Extract the actual string portion (first 10 characters in this example)

    // Do something with the received string
    // ...

    receivedData = "";
  }
}
