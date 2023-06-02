/*
ARDUINO - PC

code by salamelek (and chatGPT xd)
*/

const int ledPin = 9; // Pin number of the built-in LED

void setup() {
  Serial.begin(9600); // Set the baud rate to match the one on the PC
  pinMode(ledPin, OUTPUT); // Set the LED pin as an output
}

void loop() {
  if (Serial.available()) {
    char command = Serial.read();

    Serial.println(command);

    if (command == 'a') {
      digitalWrite(ledPin, HIGH); // Turn on the LED
    }
    if (command == 'b') {
      digitalWrite(ledPin, LOW); // Turn on the LED
    }
  }
}
