#define HALL_PIN 39

void setup(){
  Serial.begin(115200);
  pinMode(HALL_PIN, INPUT_PULLUP);
}

void loop(){
  Serial.println(digitalRead(HALL_PIN));
  delay(1);
}
