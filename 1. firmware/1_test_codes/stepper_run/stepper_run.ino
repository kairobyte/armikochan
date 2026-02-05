#include <AccelStepper.h>

#define dir_pin 4
#define step_pin 9

AccelStepper stepper(AccelStepper::DRIVER, step_pin, dir_pin);

int speed = -100;

void setup(){
  Serial.begin(115200);
  stepper.setMaxSpeed(2000);
  stepper.setSpeed(speed);
  Serial.println("Setup Done.");
}

void loop(){
  if(Serial.available()>0){
    char read = Serial.read();
    // Serial.println(read);
    if (read == 'f'){
      speed = 1000;
      Serial.println("Speed = 1000");
    }
    else if (read == 's'){
      speed = 100;
      Serial.println("Speed = 100");
    }
    else if (read == 'r'){
      speed *= -1;
      Serial.println(speed);
      Serial.println("Speed Reversed");
    }
    else if (read == 'm'){
      speed = 2000;
      Serial.println("Speed = 2000");
    }
  }
  stepper.setSpeed(speed);
  stepper.runSpeed();
}