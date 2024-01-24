import time
import serial

import pygame
from pygame.locals import *

import threading

# EDITABLE AREA START ============

PORT = "/dev/cu.usbserial-10"
BAUD = 115200
FPS = 120

# change the following window-relative coordinates based on the classroom layout; the list can be of any length
COORDINATES = [(0.1, 0.1), (0.1, 0.3), (0.1, 0.5), (0.1, 0.7), (0.3, 0.8), (0.7, 0.8), (0.9, 0.65), (0.9, 0.4), (0.9, 0.15), (0.6, 0.3), (0.6, 0.5), (0.4, 0.3), (0.4, 0.5)]

# EDITABLE AREA END ==============

ser = serial.Serial(PORT)
ser.baudrate = BAUD
ser.bytesize = 8
ser.parity  ='N'
ser.stopbits = 1
time.sleep(1)

COORDINATES.insert((-100, -100), 0) # dummy desk, since desk numbers start at 1
luxes = [0 for i in range(len(COORDINATES))]
run = True

# returns once sync bytes are received correctly; following 4 bytes should be data
def sync():
    buf = [b'\xaa', b'\xaa', b'\xaa']
    while True:
        buf[2] = buf[1]
        buf[1] = buf[0]
        buf[0] = ser.read()
        if buf == [b'\x00', b'\xff', b'\xff']:
            break

# returns a one-byte-checksum for a byte array of any length
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

# independent serial communication thread
def reader():
    while run:
        sync()
        frame = ser.read(4)
        crc = crc8(frame[1:4])
        if frame[0] != crc:
            print(f"Error! CRC mismatch (received: {frame[0]}, calculated: {crc})")
            continue
        ap = int.from_bytes(frame[1:2], byteorder='little');
        lux = int.from_bytes(frame[2:4], byteorder='little');
        print(f"Success! data frame received (crc: {str(frame[0]).zfill(3)} | arbeitsplatz: {str(ap).zfill(3)} | lux: {str(lux).zfill(6)})")
        luxes[ap] = lux

t = threading.Thread(target=reader)
t.daemon = True
t.start()

pygame.init()

fpsClock = pygame.time.Clock()
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption('LUX RADAR')

font = pygame.font.Font(None, HEIGHT//10)
font2 = pygame.font.Font(None, HEIGHT//20)
numbers = [font.render(f"{i}", True, (255, 255, 255), None) for i in range(len(COORDINATES))]

# game loop
while True:

    # handle events
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            run = False
            break
        elif event.type == pygame.VIDEORESIZE:
            WIDTH = event.w
            HEIGHT = event.h
            print(F"{WIDTH} {HEIGHT}")
            font = pygame.font.Font(None, HEIGHT//10)
            numbers = [font.render(f"{i}", True, (255, 255, 255), None) for i in range(len(COORDINATES))]
    if run == False:
        break  # escape the loop before rendering a final time

    # draw desks
    screen.fill((0, 0, 0))
    for i in range(len(COORDINATES)):
        cords = (COORDINATES[i][0] * WIDTH, COORDINATES[i][1] * HEIGHT)
        r = Rect(0, 0, WIDTH/12, HEIGHT/12)
        r.center = cords
        pygame.draw.rect(screen, (255, 0, 0), r)
        r.x += WIDTH/80
        r.y += HEIGHT/80
        screen.blit(numbers[i], r)
        r.x += 40
        r.y += 40
        screen.blit(font2.render(f"{luxes[i]}", True, (255, 255, 255), None), r)

    # render and time
    pygame.display.flip()
    fpsClock.tick(FPS)