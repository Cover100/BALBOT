# BALBOT
Ball Balancing Robot

## Table of Contents
- [Overview](#overview)
- [Hardware Requirements](#hardware-requirements)
- [Installation and Setup](#installation-and-setup)

## Overview
BALBOT is a Raspberry Pi 5–powered robotic system that uses real-time computer vision and closed-loop servo control to keep a ball balanced at the center of an acrylic plate. A wide-angle camera tracks the ball's position while three precision servos dynamically tilt the plate to maintain equilibrium.

## Hardware Requirements
- [Raspberry Pi 5](https://www.raspberrypi.com/products/raspberry-pi-5/)
- MicroSD card (16 GB or larger)
- 3 x [FS5115M-FB](https://www.pololu.com/product/3443) (or similar feedback-enabled servos)
- External 6V power supply (≥3 Amp recommended)

## Installation and Setup
1. Download [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Flash the `Raspberry Pi OS 64-bit (Debian Bookworm)` to your SD card
3. Insert the SD card and boot the Pi (monitor, keyboard & mouse recommended)
4. Follow [Configuration on first boot](#configuration-on-first-boot) steps
5. **Terminal** -> Perform System Updates
```
sudo apt update && sudo apt upgrade -y
```
6. **Terminal** -> Install required project libraries
```
sudo apt install python3-numpy python3-pigpio python3-spidev python3-opencv v4l2loopback-dkms
```
7. **Terminal** -> Enable and start the `pigpiod` daemon
```
sudo systemctl enable pigpiod
sudo systemctl start pigpiod
```
8. [Connect the Pi Camera](#connect-the-pi-camera)
9. **Terminal** -> Stream the Pi Camera to a Virtual Webcam
```
rpicam-vid --width 640 --height 480 --framerate 30 --codec yuv420 --inline --flush --timeout 0 --output - | \
ffmpeg -f rawvideo -pix_fmt yuv420p -s 640x480 -i - -f v4l2 /dev/video10
```

### Configuration on first boot
This section assumes connection to a monitor with a mouse and keyboard connected to the Raspberry Pi 5

1. Dismiss the welcome screen
2. Configure country, language, time zone and keyboard layout
3. Configure User - (Default: `username: ballbot`, `password: Balance123`)
4. Choose a preferred network and enter password
5. Choose your preffered browser
6. Update software
7. Continue [setup](#installation-and-setup)

### Connect the Pi Camera
Depending on your camera you may need a ribbon adapter (The Pi 5 features a slimline connection port compared to older cameras and Pis)

1. **Terminal** -> Shut down the Pi
```
sudo shutdown now
```
2. Wait until the status LEDs turn on and the fan (if present) stops
3. Gently lift the **black locking tab** on the camera connector (CSI port)
4. Insert the ribbon cable with the metal contacts facing the correct direction:
  - On Raspberry Pi 5, contacts should face the Ethernet port.
5. Push the locking tab back down to secure it
6. Power the Pi back on
7. **Terminal** -> Test the camera is functioning (2 second burst)
```
rpicam-vid -- framerate 60 --timeout 2000
``` 
