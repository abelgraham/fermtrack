# FermTrack ESP32 Integration

This directory contains ESP32 firmware and integration code for the FermTrack fermentation monitoring system.

## Overview

The ESP32 integration provides:
- Temperature and humidity sensor readings
- pH sensor monitoring  
- Wireless connectivity to FermTrack backend
- Real-time data transmission
- Local sensor calibration
- Power management features

## Hardware Requirements

- ESP32 development board
- Temperature/humidity sensor (DHT22 or DS18B20)
- pH sensor module
- Optional: LCD display for local readouts
- WiFi connectivity

## Directory Structure

```
esp32-integration/
├── src/                 # Main source code
├── lib/                 # Custom libraries
├── examples/            # Example sketches
├── docs/                # Hardware specs and wiring diagrams
├── platformio.ini       # PlatformIO configuration
└── README.md           # This file
```

## API Integration

The ESP32 firmware communicates with the FermTrack backend via REST API:
- POST sensor readings to `/api/sensors/data`
- GET batch configuration from `/api/batches/{batch_id}/config`
- Authentication via JWT tokens

## Getting Started

1. Install PlatformIO or Arduino IDE
2. Configure WiFi credentials in `src/config.h`
3. Set FermTrack backend URL
4. Upload firmware to ESP32
5. Monitor serial output for connection status

## Sensor Configuration

- Temperature: Every 30 seconds
- pH: Every 2 minutes  
- Humidity: Every 30 seconds
- Batch association via web interface

Licensed under AGPL v3 - see main project LICENSE