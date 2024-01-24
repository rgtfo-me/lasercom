# lasercom - project example

This is an example project for wireless communication of illumination
measurements between an Arduino board and a comuter. The Arduino (send.cpp)
sends serial data as a laser beam aimed at a phototransistor connected
to a relay-Arduino (receive.cpp) which passes the data onto the computer,
where a python script (process.py) evaluates and visualizes the incoming
data.

### Frame specification:

A single data frame is seven (7) bytes in length, the first three of which
consist of the fixed sequence `0xFF`, `0xFF`, `0x00`. The next byte contains a
checksum generated out of the last three bytes, which contain the actual data.
Here's an implementation in Python/C of said checksum.

```python
def crc8(data):
    crc = 0
    for i in range(len(data)):
        byte = data[i]
        for b in range(8):
            fb_bit = (crc ^ byte) & 0x01
            if fb_bit == 0x01:
                crc = crc ^ 0x18
            crc = (crc >> 1) & 0x7f
            if fb_bit == 0x01:
                crc = crc | 0x80
            byte = byte >> 1
    return crc
```

```C
uint8_t crc8( uint8_t *addr, uint8_t len) {
      uint8_t crc=0;
      for (uint8_t i=0; i<len;i++) {
         uint8_t inbyte = addr[i];
         for (uint8_t j=0;j<8;j++) {
             uint8_t mix = (crc ^ inbyte) & 0x01;
             crc >>= 1;
             if (mix) 
                crc ^= 0x8C;
         inbyte >>= 1;
      }
    }
   return crc;
}
```

The last three data bytes consist of the desk-number as a `uint8_t` and the
respective light level at this desk in lux as a `uint16_t`. The byte-order
is little-endian (most significant byte last).

### Communication specification

As multiple desks will send data to a single receiver in a one-way-manner,
there is no way to synchronize them. Since this is the case, every sender
should send a frame in randomized invervals between two (2) and ten (10)
seconds. Colliding frames will be discarded because of the checksum, in case
the sync-bytes happen to survive such an event.
