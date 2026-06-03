/*******************************************************************************
 * FILENAME:    main.cpp
 * DESCRIPTION: The actual code running on esp32 in the final project
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
#include <AccelStepper.h>

// ────────────────────────────────────────────────
// Configuration
// ────────────────────────────────────────────────

// ====== Configuration ======
#define STEPPER_COUNT       9
#define SERIAL_BAUD        115200
#define SERIAL_TIMEOUT_MS   50   // how long to wait for full command

// Pin arrays (make sure these match your wiring!)
// ====== Globals ======
const uint8_t DIR_PINS[STEPPER_COUNT]  = {4, 5, 6, 7, 17, 18, 8, 3, 38};
const uint8_t STEP_PINS[STEPPER_COUNT] = {9,10,11,12,13,14,21,47,37};

// Per-motor tuning (steps/s and steps/s²)
const float MAX_SPEEDS[STEPPER_COUNT]      = {1000, 1200, 1000, 800, 1000, 1000, 1000, 1000, 1000};
const float ACCELERATIONS[STEPPER_COUNT]   = {500, 500, 500, 500, 500, 500, 500, 500, 500};

// Default / home position (in steps)
const long DEFAULT_POSE[STEPPER_COUNT] = {0, 3000, 0, 1500, 0, 1000, 0, 0, 0};

// Gripper specifics
const long GRIPPER_OPEN_POS = 0;
const long GRIPPER_MAX_CLOSE_POS = -400; // Large negative value to keep moving until FSR triggers
const int FSR_PIN = 1;
const int FSR_THRESHOLD = 1000;

// ────────────────────────────────────────────────
// Globals
// ────────────────────────────────────────────────

AccelStepper steppers[STEPPER_COUNT] = {
    AccelStepper(AccelStepper::DRIVER, STEP_PINS[0], DIR_PINS[0]),
    AccelStepper(AccelStepper::DRIVER, STEP_PINS[1], DIR_PINS[1]),
    AccelStepper(AccelStepper::DRIVER, STEP_PINS[2], DIR_PINS[2]),
    AccelStepper(AccelStepper::DRIVER, STEP_PINS[3], DIR_PINS[3]),
    AccelStepper(AccelStepper::DRIVER, STEP_PINS[4], DIR_PINS[4]),
    AccelStepper(AccelStepper::DRIVER, STEP_PINS[5], DIR_PINS[5]),
    AccelStepper(AccelStepper::DRIVER, STEP_PINS[6], DIR_PINS[6]),
    AccelStepper(AccelStepper::DRIVER, STEP_PINS[7], DIR_PINS[7]),
    AccelStepper(AccelStepper::DRIVER, STEP_PINS[8], DIR_PINS[8]),
};

long target_positions[STEPPER_COUNT] = {0};

// ────────────────────────────────────────────────
// Compute the expected move time (in seconds) for a given acceleration, max speed, and distance
// ────────────────────────────────────────────────
// Function: compute_move_time
// ====== Functions ======
double compute_move_time(float accel, float max_speed, long distance) {
    distance = abs(distance);
    if (distance == 0) return 0.0;

    float ramp_distance = (max_speed * max_speed) / accel;

    if ((float)distance <= ramp_distance) {
        // Triangular profile (doesn't reach max speed)
        return 2.0 * sqrt((double)distance / accel);
    } else {
        // Trapezoidal profile
        double ramp_time = max_speed / accel;
        double const_distance = distance - ramp_distance;
        double const_time = const_distance / max_speed;
        return 2.0 * ramp_time + const_time;
    }
}

// ────────────────────────────────────────────────
// Fast atoi that handles negative numbers
// ────────────────────────────────────────────────
// Function: fast_atoi
inline long fast_atoi(const char *str) {
    long value = 0;
    bool negative = false;

    if (*str == '-') {
        negative = true;
        str++;
    }

    while (*str >= '0' && *str <= '9') {
        value = value * 10 + (*str - '0');
        str++;
    }

    return negative ? -value : value;
}

// ────────────────────────────────────────────────
// Serial command parser
// ────────────────────────────────────────────────
// Function: read_serial_command
void read_serial_command() {
    if (Serial.available() == 0) return;

    static char buffer[160];
    size_t len = Serial.readBytesUntil('\n', buffer, sizeof(buffer) - 1);

    if (len == 0) return;

    buffer[len] = '\0';

    // Trim leading whitespace
    char *start = buffer;
    while (*start == ' ' || *start == '\t') start++;

    int motor_index = 0;
    char *token = strtok(start, ", ");

    bool valid = true;
    long new_targets[STEPPER_COUNT - 1];
    int gripper_state = 0;

    while (token != nullptr && motor_index < STEPPER_COUNT) {
        if (motor_index < STEPPER_COUNT - 1) {
            new_targets[motor_index] = fast_atoi(token);
        } else {
            gripper_state = fast_atoi(token);
            if (gripper_state != 0 && gripper_state != 1) {
                valid = false;
            }
        }
        motor_index++;
        token = strtok(nullptr, ", ");
    }

    // Check if we got the correct number of values
    if (motor_index != STEPPER_COUNT || token != nullptr) {
        Serial.printf("ERR: expected %d values (8 positions + gripper state 0/1), received %d\n", STEPPER_COUNT, motor_index);
        valid = false;
    }

    if (valid) {
        // Set gripper target based on state
        if (gripper_state == 0) {
            target_positions[8] = GRIPPER_OPEN_POS;
        } else {  // gripper_state == 1
			target_positions[8] = GRIPPER_MAX_CLOSE_POS;
            // int fsr_value = analogRead(FSR_PIN);
            // if (fsr_value > FSR_THRESHOLD) {
            //     target_positions[8] = steppers[8].currentPosition();
            // } else {
            //     target_positions[8] = GRIPPER_MAX_CLOSE_POS;
            // }
        }

        // Compute distances (including gripper for consistency, but exclude from sync)
        long distances[STEPPER_COUNT];
        for (int i = 0; i < STEPPER_COUNT; i++) {
            if (i < STEPPER_COUNT - 1) {
                distances[i] = labs(new_targets[i] - steppers[i].currentPosition());
            } else {
                distances[i] = labs(target_positions[i] - steppers[i].currentPosition());
            }
        }

        // Compute natural move times for the first 8 steppers only
        double natural_times[STEPPER_COUNT];
        double max_time = 0.0;
        for (int i = 0; i < STEPPER_COUNT - 1; i++) {
            natural_times[i] = compute_move_time(ACCELERATIONS[i], MAX_SPEEDS[i], distances[i]);
            if (natural_times[i] > max_time) {
                max_time = natural_times[i];
            }
        }

        // Update the first 8 targets
        memcpy(target_positions, new_targets, sizeof(long) * (STEPPER_COUNT - 1));

        // Scale parameters for each of the first 8 motors to match the max time
        for (int i = 0; i < STEPPER_COUNT - 1; i++) {
            if (distances[i] == 0) {
                steppers[i].moveTo(target_positions[i]);  // Redundant but harmless
                continue;
            }

            double r = max_time / natural_times[i];
            float scaled_speed = MAX_SPEEDS[i] / r;
            float scaled_accel = ACCELERATIONS[i] / (r * r);

            steppers[i].setMaxSpeed(scaled_speed);
            steppers[i].setAcceleration(scaled_accel);
            steppers[i].moveTo(target_positions[i]);
        }

        // For gripper, use default parameters (no scaling)
        if (distances[8] == 0) {
            steppers[8].moveTo(target_positions[8]);  // Redundant but harmless
        } else {
            steppers[8].setMaxSpeed(MAX_SPEEDS[8]);
            steppers[8].setAcceleration(ACCELERATIONS[8]);
            steppers[8].moveTo(target_positions[8]);
        }

        if (Serial) {
            Serial.print("OK target → ");
            for (int i = 0; i < STEPPER_COUNT - 1; i++) {
                Serial.print(target_positions[i]);
                Serial.print(",");
            }
            Serial.print(gripper_state);
            Serial.println();
        }
    }
}

// ────────────────────────────────────────────────
// SETUP
// ────────────────────────────────────────────────
// Function: setup

void setup() {
    Serial.begin(SERIAL_BAUD);
    delay(200);  // give serial time to settle

    Serial.println("\n=== 9-Axis Stepper Controller (8 + Gripper) ===");
    Serial.println("Send 9 comma-separated values (8 positions + gripper state 0/1), e.g.:");
    Serial.println("  0,1200,-800,0,500,0,-300,1000,1");
    Serial.println("Negative values move opposite direction.\n");

    for (int i = 0; i < STEPPER_COUNT; i++) {
        pinMode(DIR_PINS[i],  OUTPUT);
        pinMode(STEP_PINS[i], OUTPUT);

        steppers[i].setMaxSpeed(MAX_SPEEDS[i]);
        steppers[i].setAcceleration(ACCELERATIONS[i]);
        steppers[i].setCurrentPosition(0);           // assume start at zero
    }

    // Optional: move to default/home pose on boot (uncomment if wanted)
    // memcpy(target_positions, DEFAULT_POSE, sizeof(target_positions));
    // Serial.println("Moving to default pose on startup...");
}

// ────────────────────────────────────────────────
// MAIN LOOP
// ────────────────────────────────────────────────
// Function: loop

void loop() {
    read_serial_command();

    // Run all steppers (non-blocking)
    for (int i = 0; i < STEPPER_COUNT; i++) {
        steppers[i].run();
    }

    // // Check FSR for gripper (only when closing in negative direction)
    // int fsr_value = analogRead(FSR_PIN);
    // if (steppers[8].distanceToGo() < 0 && fsr_value > FSR_THRESHOLD) {
    //     steppers[8].stop();
    //     target_positions[8] = steppers[8].currentPosition();
    // }
}
