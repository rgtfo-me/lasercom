#include <Arduino.h>
#include <SoftwareSerial.h>

SoftwareSerial softwareSerial(2, 3, true);

struct Frame {
    uint8_t start1;
    uint8_t start2;
    uint8_t start3;
    uint8_t crc;
    uint8_t ap;
    uint16_t lux;
} __attribute__((__packed__));

uint8_t crc8(uint8_t *addr, uint8_t len) {
    uint8_t crc = 0;
    for (uint8_t i = 0; i < len; i++) {
        uint8_t inbyte = addr[i];
        for (uint8_t j = 0; j < 8; j++) {
            uint8_t mix = (crc ^ inbyte) & 0x01;
            crc >>= 1;
            if (mix)
                crc ^= 0x8C;
            inbyte >>= 1;
        }
    }
    return crc;
}

void setup() {
    Serial.begin(300);
    softwareSerial.begin(300);
}

void loop() {
    struct Frame frame = {.start1 = 0xff, .start2 = 0xff, .start3 = 0x00, .crc = 0, .ap = 11, .lux = (uint16_t) random(1, 10000)};
    frame.crc = crc8(((uint8_t *) &frame) + 4, 3);
    for (uint8_t i = 0; i < sizeof(frame); i++) {
        softwareSerial.write(((uint8_t *) &frame)[i]);
        Serial.write(((uint8_t *) &frame)[i]);
//        delay(100);
    }
    delay(random(1000, 3000));
}