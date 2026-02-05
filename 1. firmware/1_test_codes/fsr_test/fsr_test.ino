#define FSR_PIN 18

int last_value = 0;
int current_value = 0;
float change_rate = 0.02;

void setup(){
  Serial.begin(115200);
  pinMode(FSR_PIN, INPUT);
}

void loop(){
  int serial_read = analogRead(FSR_PIN);
  
  current_value = (serial_read*change_rate) + (last_value*(1-change_rate));
  Serial.println(current_value);
  last_value = current_value;
  delay(1);
}