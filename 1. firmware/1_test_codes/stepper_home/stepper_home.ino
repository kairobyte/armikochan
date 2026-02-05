#include <AS5600.h>
#include <AccelStepper.h>

#define HALL_PIN 40
#define DIR_PIN    18
#define STEP_PIN   14

// Set to true if hall is Normally Open (pull-down), false if Normally Closed (pull-up)
#define HALL_NORMALLY_OPEN true

// Homing direction: negative = towards home hall
const float HOMING_SPEED = -200.0;        // steps per second (negative = towards home)
const float BACKOFF_SPEED = 500.0;        // positive speed to move away from hall
const float APPROACH_SPEED = -200.0;       // slow speed for final approach

const int BACKOFF_STEPS = 50;            // fixed steps to back off

AccelStepper stepper(AccelStepper::DRIVER, STEP_PIN, DIR_PIN);

byte hallActiveState;

void setup() {
  Serial.begin(115200);

  // Configure hall pin and determine active state
  if (HALL_NORMALLY_OPEN) {
    pinMode(HALL_PIN, INPUT_PULLDOWN);
    hallActiveState = HIGH;
  } else {
    pinMode(HALL_PIN, INPUT_PULLUP);
    hallActiveState = LOW;
  }

  stepper.setMaxSpeed(3000);
  stepper.setAcceleration(100000);

  homeStepper();

  Serial.println("Homing complete. Ready for movement.");
  Serial.println("Send 'm100' to move to position 100, 'm0' to return home, etc.");

  stepper.moveTo(0);
  while(stepper.distanceToGo() !=0 ){
    stepper.run();
  }
  stepper.setCurrentPosition(0);
}

void loop() {
  // Handle serial commands (optional)
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd.startsWith("m")) {
      long pos = cmd.substring(1).toInt();
      stepper.moveTo(pos);
      Serial.print("Moving to ");
      Serial.println(pos);
    }
  }

  // Normal accelerated movement
  stepper.run();
}

bool isHallTriggered() {
  return digitalRead(HALL_PIN) == hallActiveState;
}

bool debounceHall() {
  if (!isHallTriggered()) return false;
  
  delayMicroseconds(200);  // short debounce
  if (!isHallTriggered()) return false;
  
  delayMicroseconds(200);
  return isHallTriggered();
}

void homeStepper() {
  Serial.println("Starting homing sequence...");

  // Step 1: Fast approach toward home hall
  stepper.setSpeed(HOMING_SPEED);
  while (!debounceHall()) {
    stepper.runSpeed();
  }
  stepper.stop();  // optional: decelerate if acceleration enabled
  Serial.println("Home hall hit (fast approach)");

  // Step 2: Back off a fixed number of steps
  stepper.move(BACKOFF_STEPS);  // uses acceleration if set
  stepper.setMaxSpeed(abs(BACKOFF_SPEED));
  while (stepper.distanceToGo() != 0) {
    stepper.run();
  }
  Serial.println("Backed off from hall");

  // Step 3: Slow final approach for precision
  stepper.setSpeed(APPROACH_SPEED);
  while (!debounceHall()) {
    stepper.runSpeed();
  }
  Serial.println("Home hall hit (precise approach)");

  // Step 4: Set current position as zero
  stepper.setCurrentPosition(0);
  Serial.println("Homing complete. Position = 0");
}