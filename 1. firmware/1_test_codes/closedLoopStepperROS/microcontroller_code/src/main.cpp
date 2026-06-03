/*******************************************************************************
 * FILENAME:    main.cpp
 * DESCRIPTION: Use this code to run your stepper in closed loop mode
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
#include <AS5600.h>
#include <AccelStepper.h>
#include <Wire.h>

// ── PINS ───────────────────────────────────────────────────────────────
// ====== Configuration ======
#define I2C_SDA         15
#define I2C_SCL         16
#define HALL_PIN        12
#define DIR_PIN         4
#define STEP_PIN        3    

// ── STEPPER & MOVEMENT ─────────────────────────────────────────────────
#define STEP_SPEED         -2000     // max speed [steps/s]
#define STEPS_PER_REV      400      // your microstepping setting × steps/rev
#define ACCELERATION       1200

// ── ENCODER ────────────────────────────────────────────────────────────
#define ENCODER_RESOLUTION  4096
#define MAX_ANGLE_CHANGE    360      // jump protection
#define ANGLE_UPDATE_MS     1
#define ANGLE_CORRECTION -1

// ── HOMING ─────────────────────────────────────────────────────────────
#define HALL_NORMALLY_OPEN  false
#define HOMING_SPEED       -1400.0
#define BACKOFF_SPEED       900.0
#define APPROACH_SPEED     -600.0
#define BACKOFF_STEPS       200      

// ── GLOBALS ────────────────────────────────────────────────────────────
AS5600 as5600;
AccelStepper stepper(AccelStepper::DRIVER, STEP_PIN, DIR_PIN);
// ====== Globals ======
byte hallActiveState;

TaskHandle_t angle_h;
TaskHandle_t step_h;

int zeroPosition = 0;
int target_pos = 0;
int current_pos = 0;

bool angleTaskStart = false;

// Function: isHallTriggered
// ====== Functions ======
bool isHallTriggered(){
	return digitalRead(HALL_PIN) == hallActiveState;
}

// Function: debounceHall
bool debounceHall() {
	if (!isHallTriggered()) return false;
	delayMicroseconds(50);
	if (!isHallTriggered()) return false;
	delayMicroseconds(50);
	return isHallTriggered();
}

// Function: homeStepper
void homeStepper(){
	Serial.println("Started Homing");

	stepper.setSpeed(STEP_SPEED);
	while(!debounceHall()){
		stepper.runSpeed();
	}
	stepper.stop();
	Serial.println("Hall hit once");

	stepper.move(BACKOFF_STEPS);
	stepper.setMaxSpeed(abs(BACKOFF_SPEED));
	while(stepper.distanceToGo() != 0){
		stepper.run();
	}
	Serial.println("Stepper backed off");
	stepper.setSpeed(APPROACH_SPEED);
	while(!debounceHall()){
		stepper.runSpeed();
	}
	stepper.stop();
	stepper.setCurrentPosition(0);
	stepper.moveTo(90);
	while(stepper.distanceToGo()!=0){
		stepper.run();
	}
	stepper.setCurrentPosition(0);
	Serial.println("Stepper homing complete. ");
}

// Function: encoderSetup
void encoderSetup(){
	// AS5600 Setup
	Wire.begin(I2C_SDA, I2C_SCL);
	Wire.setClock(100000);
	Wire.setTimeOut(500);
	as5600.begin(1);
	as5600.setDirection(AS5600_CLOCK_WISE);
	// esp_log_level_set("i2c.master", ESP_LOG_NONE);

	bool corrected = false;

	while (!corrected){
		if(as5600.isConnected()){
			zeroPosition = as5600.getCumulativePosition();
			corrected = true;
		}
	}
	angleTaskStart = true;
}

// Function: angle_t
void angle_t(void *pvParameters){
	static uint32_t last_read = 0;
	static int last_angle = 0;

	while(angleTaskStart) {
		if (millis() - last_read >= ANGLE_UPDATE_MS){
			last_read = millis();

			int angle = 0;

			if (as5600.isConnected()){
				int cumulative = as5600.getCumulativePosition() - zeroPosition;
				int rev = as5600.getRevolutions();
				angle = (map(cumulative - ENCODER_RESOLUTION * rev, 0, ENCODER_RESOLUTION, 0, 360) + 360 * rev) * ANGLE_CORRECTION;
				last_angle = angle;
				// if (abs(angle - last_angle) < MAX_ANGLE_CHANGE) {
					last_angle = angle;
				// }
				current_pos = angle;
				int del = target_pos - current_pos;
				int moveTo = stepper.currentPosition();
				if (del <= 4) {
					moveTo = stepper.currentPosition() + (del * STEPS_PER_REV / 360);
					stepper.moveTo(moveTo);
				}
				Serial.printf("Cum: %d, Angle: %d, CP: %d, del: %d moveTo: %d\n", cumulative, angle, stepper.currentPosition(), del, moveTo);
			}
			// Serial.printf("CF: %d, Angle: %d, Pos: %d, Distance: %d\n",zeroPosition, last_angle, stepper.currentPosition(), stepper.distanceToGo());
		}
		vTaskDelay(1/portTICK_PERIOD_MS);
	}
}

// Function: step_t
void step_t(void *pvParameters) 
{
  vTaskDelay(1000 / portTICK_PERIOD_MS);
  while (true) {
    stepper.run();
    current_pos = stepper.currentPosition();
    // vTaskDelay(1 / portTICK_PERIOD_MS);
  }
}

// Function: setup

void setup(){
	esp_log_level_set("*", ESP_LOG_ERROR);
	Serial.begin(115200);
	Serial.println("STARTED");

	if (HALL_NORMALLY_OPEN) {
		pinMode(HALL_PIN, INPUT_PULLDOWN);
		hallActiveState = HIGH;
	} else {
		pinMode(HALL_PIN, INPUT_PULLDOWN);
		hallActiveState = LOW;
	}

	// Stepper Setup
	stepper.setMaxSpeed(STEP_SPEED);
	stepper.setAcceleration(ACCELERATION);
	stepper.setCurrentPosition(0);

	homeStepper();
	delay(1000);
	encoderSetup();
	delay(2000);
	// stepper.moveTo(415);

	xTaskCreatePinnedToCore(
		angle_t,
		"angle_t",
		10000,
		NULL,
		0,
		&angle_h,
		0
	);

  	xTaskCreatePinnedToCore(
		step_t,
		"step_t",
		10000,
		NULL,
		1,
		&step_h,
		1
	);

}

// Function: loop

void loop(){
	stepper.run();
}
