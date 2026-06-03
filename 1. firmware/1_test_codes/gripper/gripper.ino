/*******************************************************************************
 * FILENAME:    gripper.ino
 * DESCRIPTION: Use this to test the gripper
 * AUTHOR:      Sushant Thakur
 * DATE:        202-05-29
 * VERSION:     1.0.0
 * 
 * COPYRIGHT:   Copyright (c) 2026 Sushant Thakur. All rights reserved.
 ******************************************************************************/

// ============================================================================
// File: gripper.ino
// Auto-added section markers and high-level comments
// ============================================================================

// ====== Includes ======
#include <AccelStepper.h>

// ====== Configuration ======
#define STEP_PIN 3
#define DIR_PIN 4
#define FSR_PIN 10
#define FSR_THRESHOLD 3600

AccelStepper stepper(AccelStepper::DRIVER, STEP_PIN, DIR_PIN);

// Function: setup

// ====== Functions ======
void setup(){
  Serial.begin(115200);
  stepper.setMaxSpeed(2000);
  stepper.setSpeed(-200);
  pinMode(FSR_PIN, INPUT);
  delay(5000);
}

// Function: loop

void loop(){
  if(analogRead(FSR_PIN)<FSR_THRESHOLD){
    stepper.runSpeed();
  }
}