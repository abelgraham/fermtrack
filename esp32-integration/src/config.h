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