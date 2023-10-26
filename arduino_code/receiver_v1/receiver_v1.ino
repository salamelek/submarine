// receiver

#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
#include <Servo.h>

Servo esc;

RF24 radio(9,10); // CE, CSN
const byte address[6] = "00001";
char data[32];

void setup() {
  Serial.begin(230400);

  radio.begin();
  radio.setPayloadSize(9);
  radio.openReadingPipe(1,address);
  radio.setPALevel(RF24_PA_LOW);
  radio.startListening();
  
  esc.attach(8); // Connect the ESC signal wire to pin 8 (D8)

  Serial.println("Receiver running...");
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
  if(radio.available()) {
    unsigned char receivedData[9];                    // Create a buffer to store the received data
    radio.read(&receivedData, sizeof(receivedData));  // Read the received data into the buffer

    // Print the received array
    Serial.print("Received data: ");
    printArray(receivedData, sizeof(receivedData));

    esc.writeMicroseconds(map(receivedData[1], 0, 255, 1000, 2000));
  }
}
