/*******************************************************************************
 * FILENAME:    main.cpp
 * DESCRIPTION: Use this to test the hall sensors individually
 * AUTHOR:      Sushant Thakur
 * DATE:        202-05-29
 * VERSION:     1.0.0
 * 
 * COPYRIGHT:   Copyright (c) 2026 Sushant Thakur. All rights reserved.
 ******************************************************************************/

// ============================================================================
// File: main.cpp
// Auto-added section markers and high-level comments
// ============================================================================

// ====== Includes ======
#include <Arduino.h>

// ====== Configuration ======
#define HALL_PIN 1

// Function: setup

// ====== Functions ======
void setup(){
	Serial.begin(115200);

	pinMode(HALL_PIN, INPUT);
}

// Function: loop

void loop(){
	Serial.println(analogRead(HALL_PIN));
	delay(1);
}