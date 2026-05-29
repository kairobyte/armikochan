/*******************************************************************************
 * FILENAME:    main.cpp
 * DESCRIPTION: Use this to test the 8 channel mux
 * AUTHOR:      Sushant Thakur
 * DATE:        202-05-29
 * VERSION:     1.0.0
 * 
 * COPYRIGHT:   Copyright (c) 2026 Sushant Thakur. All rights reserved.
 ******************************************************************************/

#include <Arduino.h>
#include <Wire.h>
#include <AS5600.h>   // Rob Tillaart's library

#define SDA_PIN         15
#define SCL_PIN         16
#define MUX_ADDRESS     0x70
#define ENCODER_COUNT   8

// Create one AS5600 instance per encoder
AS5600 encoders[ENCODER_COUNT];

void selectMultiplexerChannel(uint8_t channel) {
  if (channel >= ENCODER_COUNT) return;

  Wire.beginTransmission(MUX_ADDRESS);
  Wire.write(1 << channel);   // select channel 0..7
  Wire.endTransmission();
  delay(1);                   // small delay for reliability (optional but helps)
}

void setup() {
  Serial.begin(115200);
  delay(200);                 // give serial time to connect
  while (!Serial) {}

  Serial.println("\n=== 8 × AS5600 Encoders via TCA9548A Multiplexer ===\n");

  Wire.begin(SDA_PIN, SCL_PIN);
  Wire.setClock(400000);      // 400 kHz is usually fine and faster

  bool allGood = true;

  for (int i = 0; i < ENCODER_COUNT; i++) {
    selectMultiplexerChannel(i);

    // Optional: set direction pin if you use hardware DIR pin (255 = not used)
    bool success = encoders[i].begin(255);   // or encoders[i].begin() if no DIR pin

    Serial.print("Encoder ");
    Serial.print(i + 1);
    Serial.print(" on channel ");
    Serial.print(i);
    Serial.print(" : ");

    if (success && encoders[i].isConnected()) {
      Serial.println("OK");
      // Optional: configure if needed
      // encoders[i].setDirection(AS5600_CLOCK_WISE);
    } else {
      Serial.println("FAILED - check wiring / magnet / power");
      allGood = false;
    }
  }

  if (allGood) {
    Serial.println("\nAll 8 encoders initialized successfully!\n");
  } else {
    Serial.println("\nOne or more encoders failed. Check connections.\n");
  }
}

void loop() {
  // Example: read and print raw angles from all encoders every 500 ms
  for (int i = 0; i < ENCODER_COUNT; i++) {
    selectMultiplexerChannel(i);

    uint16_t raw = encoders[i].rawAngle();          // 0 .. 4095
    float degrees = encoders[i].readAngle() * (360.0 / 4096.0);  // or use .getAngle()

    Serial.print(i + 1);
    Serial.print(":");
    Serial.print(raw);
    Serial.print("=");
    Serial.print(degrees, 1);
    Serial.print("d\t");
  }
  Serial.println();

  delay(50);
}