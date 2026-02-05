#include <AccelStepper.h>

#define STEP_PIN 3
#define DIR_PIN 4
#define FSR_PIN 10
#define FSR_THRESHOLD 3600

AccelStepper stepper(AccelStepper::DRIVER, STEP_PIN, DIR_PIN);

void setup(){
  Serial.begin(115200);
  stepper.setMaxSpeed(2000);
  stepper.setSpeed(-200);
  pinMode(FSR_PIN, INPUT);
  delay(5000);
}

void loop(){
  if(analogRead(FSR_PIN)<FSR_THRESHOLD){
    stepper.runSpeed();
  }
}