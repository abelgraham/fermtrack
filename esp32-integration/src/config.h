/*
FermTrack - Fermentation Tracking System - ESP32 Configuration
Copyright (C) 2026 FermTrack Contributors

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
*/

#ifndef CONFIG_H
#define CONFIG_H

// WiFi Configuration
#define WIFI_SSID "YOUR_WIFI_SSID"
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"

// FermTrack Backend Configuration
#define FERMTRACK_BASE_URL "http://192.168.1.100:5000"
#define FERMTRACK_API_ENDPOINT "/api/sensors/data"

// JWT Token (get from frontend login)
#define JWT_TOKEN "your_jwt_token_here"

// Sensor Pin Definitions
#define DHT_PIN 4
#define DHT_TYPE DHT22
#define PH_SENSOR_PIN A0
#define ONEWIRE_BUS 2

// Timing Configuration (milliseconds)
#define SENSOR_READ_INTERVAL 30000    // 30 seconds
#define PH_READ_INTERVAL 120000       // 2 minutes
#define WIFI_RETRY_DELAY 5000         // 5 seconds
#define API_RETRY_DELAY 10000         // 10 seconds

// Sensor Calibration
#define PH_CALIBRATION_OFFSET 0.0
#define TEMP_CALIBRATION_OFFSET 0.0

// Device Settings
#define DEVICE_ID "fermtrack_esp32_001"
#define BATCH_ID ""  // Set via web interface or serial command

// Debug Settings
#define ENABLE_SERIAL_DEBUG true
#define ENABLE_LOCAL_DISPLAY false

#endif // CONFIG_H