# BALBOT
Ball Balancing Robot

## Table of Contents
- [Overview](#overview)
- [Hardware Requirements](#hardware-requirements)
- [Installation & Setup](#installation-and-setup)

## Overview
BALBOT is a Raspberry Pi 5–powered robotic system that uses real-time computer vision and closed-loop servo control to keep a ball balanced at the center of an acrylic plate. A wide-angle camera tracks the ball's position while three precision servos dynamically tilt the plate to maintain equilibrium.

## Hardware Requirements
- [Raspberry Pi 5](https://www.raspberrypi.com/products/raspberry-pi-5/)
- MicroSD card (16 GB or larger)
- 3 x [FS5115M-FB](https://www.pololu.com/product/3443) (or similar feedback-enabled servos)
- External 6V power supply (≥3 Amp recommended)

## Installation & Setup
1. Download [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Flash the `Raspberry Pi OS 64-bit (Debian Bookworm)` to your SD card
3. Insert the SD card and boot the Pi (monitor, keyboard & mouse recommended)
4. Follow [Configuration on first boot](#configureation-on-first-boot) steps
5. Open Terminal and perform system updates
```
sudo apt update && sudo apt upgrade -y
```

### Configuration on first boot
1. Dismiss the welcome screen
2. Configure country, language, time zone and keyboard layout
3. Configure User - (Default: `username: ballbot`, `password: Balance123`)
4. Choose a preferred network and enter password
5. Choose your preffered browser
6. Update software
7. Finish - Restart your Pi & [continue setup](#installation-and-setup)
