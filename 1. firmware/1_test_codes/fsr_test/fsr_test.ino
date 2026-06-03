/*******************************************************************************
 * FILENAME:    fsr_test.ino
 * DESCRIPTION: Use this to test FSR
 * AUTHOR:      Sushant Thakur
 * DATE:        202-05-29
 * VERSION:     1.0.0
 * 
 * COPYRIGHT:   Copyright (c) 2026 Sushant Thakur. All rights reserved.
 ******************************************************************************/

// ============================================================================
// File: fsr_test.ino
// Auto-added section markers and high-level comments
// ============================================================================

// ====== Configuration ======
#define FSR_PIN 18

// ====== Globals ======
int last_value = 0;
int current_value = 0;
float change_rate = 0.02;

// Function: setup

// ====== Functions ======
void setup(){
  Serial.begin(115200);
  pinMode(FSR_PIN, INPUT);
}

// Function: loop

void loop(){
  int serial_read = analogRead(FSR_PIN);
  
  current_value = (serial_read*change_rate) + (last_value*(1-change_rate));
  Serial.println(current_value);
  last_value = current_value;
  delay(1);
}