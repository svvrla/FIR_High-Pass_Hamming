const int EMG_PIN = A0;

void setup() {
    Serial.begin(115200);
}

void loop() {

    int emg = analogRead(EMG_PIN);

    Serial.println(emg);

    delayMicroseconds(1000);      // sekitar 1000 Hz sampling
}