#include <Arduino.h>
#include <SoftwareSerial.h>

// EDITABLE AREA START ============

#define RXPIN 7
#define TXPIN 8
#define COMPUTERBAUD 115200
#define LASERBAUD 300

// EDITABLE AREA END ==============

SoftwareSerial Laser(RXPIN, TXPIN);

void setup() {
    Serial.begin(COMPUTERBAUD);
    Laser.begin(LASERBAUD);
}

void loop() {
    while (Laser.available()) {
        Serial.write(Laser.read());
    }
}
