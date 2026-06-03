/*******************************************************************************
 * FILENAME:    main.cpp
 * DESCRIPTION: Use this to test the homing of all steppers
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
#define HALL_NUM 8
// ====== Globals ======
const int hall_pins[HALL_NUM] = {48,45,35,36,39,40,41,42};
const bool normally_closed[HALL_NUM] = {true, false, false, true, false, false, true, false};
int hall_stat[HALL_NUM] = {0};

// Function: setup

// ====== Functions ======
void setup(){
	Serial.begin(115200);
	delay(200);

	Serial.println("Displaying hall stats: ");
	for(int i=0; i<HALL_NUM; i++){
		if(normally_closed[i]){
			pinMode(hall_pins[i], INPUT_PULLUP);
		}
		else{
			pinMode(hall_pins[i], INPUT_PULLDOWN);
		}
	}
}

// Function: loop

void loop(){
	for(int i=0; i<HALL_NUM; i++){
		hall_stat[i] = digitalRead(hall_pins[i]);
		Serial.printf("%d=%d\t",i+1,hall_stat[i]);
	}
	Serial.println();
}