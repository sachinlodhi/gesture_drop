# Gesture Drop

A proof-of-concept tool for contactless file transfer between computers using hand gestures, inspired by Huawei's Air Gesture File Transfer feature.

## Overview

Gesture Drop allows you to transfer files between computers on the same local network using hand gestures - without physically touching either device. The system uses computer vision to detect and interpret hand gestures for controlling file selection and transfer operations.

## Features

- Contactless file transfer between computers
- Gesture-based control system:
  - Take screenshots of file manager
  - Mark files for transfer
  - Grab selected files
  - Drop files to destination
- Real-time hand gesture recognition
- Local network file transfer

## Project Structure

GESTURE_DROP [GITHUB]
├── receiver_side/
│   ├── gesture_receive.py
│   └── receiver.py
├── sender_side/
│   ├── gesture_send.py
│   └── sender.py
└── requirements.txt

## Prerequisites

- Both sender and receiver must be on the same local network
- Python 3.x
- Required Python packages (listed in requirements.txt)
- Webcam for gesture detection

## Setup

1. Clone the repository
2. Install dependencies:
   pip install -r requirements.txt

## Configuration

Before running the application:

1. On the sender side:
   - Set the correct path to the folder containing files you want to transfer in `sender.py`
   - Configure the receiver's IP address in the sender configuration

2. On the receiver side:
   - Make sure the receiving computer's IP address matches the one configured in the sender

## Usage

1. Start the receiver:
   python receiver_side/gesture_receive.py

2. Start the sender:
   python sender_side/gesture_send.py

3. Use hand gestures to:
   - Take screenshots of your file manager
   - Mark files you want to transfer
   - Grab the files
   - Drop them to transfer to the destination computer

## Important Notes

- Ensure both computers are connected to the same local network
- Verify the correct IP address configuration before starting the transfer
- Keep your hand within the camera's field of view for gesture recognition
- Currently supports local network transfers only

## Contributing

Feel free to submit issues and enhancement requests!


## Acknowledgments

- Inspired by Huawei's Air Gesture File Transfer feature
- Built using Python and computer vision technologies
