#include <Arduino.h>

#define HALL_PIN 1

void setup(){
	Serial.begin(115200);

	pinMode(HALL_PIN, INPUT);
}

void loop(){
	Serial.println(analogRead(HALL_PIN));
	delay(1);
}