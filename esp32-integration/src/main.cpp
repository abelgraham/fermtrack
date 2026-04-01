/*
FermTrack - Fermentation Tracking System - ESP32 Integration
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

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include "config.h"

// Sensor objects
DHT dht(DHT_PIN, DHT_TYPE);
OneWire oneWire(ONEWIRE_BUS);
DallasTemperature dallas(&oneWire);

// Timing variables
unsigned long lastSensorRead = 0;
unsigned long lastPhRead = 0;
unsigned long lastWifiCheck = 0;

// Sensor data structure
struct SensorData {
  float temperature;
  float humidity;
  float ph;
  String timestamp;
  String deviceId;
  String batchId;
};

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("FermTrack ESP32 Sensor Node Starting...");
  
  // Initialize sensors
  dht.begin();
  dallas.begin();
  
  // Connect to WiFi
  connectToWiFi();
  
  Serial.println("Setup complete. Starting sensor monitoring...");
}

void loop() {
  unsigned long currentTime = millis();
  
  // Check WiFi connection periodically
  if (currentTime - lastWifiCheck >= WIFI_RETRY_DELAY) {
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("WiFi disconnected. Reconnecting...");
      connectToWiFi();
    }
    lastWifiCheck = currentTime;
  }
  
  // Read sensors and send data
  if (currentTime - lastSensorRead >= SENSOR_READ_INTERVAL) {
    SensorData data = readSensors();
    
    if (ENABLE_SERIAL_DEBUG) {
      printSensorData(data);
    }
    
    if (WiFi.status() == WL_CONNECTED && strlen(BATCH_ID) > 0) {
      sendDataToFermTrack(data);
    } else {
      Serial.println("WiFi not connected or batch ID not set. Data not sent.");
    }
    
    lastSensorRead = currentTime;
  }
  
  delay(1000); // Main loop delay
}

void connectToWiFi() {
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to WiFi");
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.print("Connected! IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println();
    Serial.println("Failed to connect to WiFi");
  }
}

SensorData readSensors() {
  SensorData data;
  
  // Read DHT22 sensor
  data.humidity = dht.readHumidity();
  float dhtTemp = dht.readTemperature();
  
  // Read DS18B20 sensor (more accurate for fermentation)
  dallas.requestTemperatures();
  float dsTemp = dallas.getTempCByIndex(0);
  
  // Use DS18B20 if available, fallback to DHT22
  if (dsTemp != DEVICE_DISCONNECTED_C) {
    data.temperature = dsTemp + TEMP_CALIBRATION_OFFSET;
  } else {
    data.temperature = dhtTemp + TEMP_CALIBRATION_OFFSET;
  }
  
  // Read pH sensor (analog reading converted to pH)
  int phRaw = analogRead(PH_SENSOR_PIN);
  data.ph = convertToPH(phRaw) + PH_CALIBRATION_OFFSET;
  
  // Set metadata
  data.deviceId = DEVICE_ID;
  data.batchId = BATCH_ID;
  data.timestamp = getCurrentTimestamp();
  
  return data;
}

float convertToPH(int rawValue) {
  // Convert analog reading to pH value
  // This is a basic conversion - calibrate for your specific sensor
  float voltage = rawValue * (3.3 / 4095.0); // ESP32 ADC
  float ph = 3.3 * voltage; // Basic linear conversion
  return constrain(ph, 0.0, 14.0);
}

String getCurrentTimestamp() {
  // For now, use millis(). In production, sync with NTP server
  return String(millis());
}

void sendDataToFermTrack(SensorData data) {
  HTTPClient http;
  http.begin(String(FERMTRACK_BASE_URL) + FERMTRACK_API_ENDPOINT);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("Authorization", "Bearer " + String(JWT_TOKEN));
  
  // Create JSON payload
  DynamicJsonDocument doc(1024);
  doc["device_id"] = data.deviceId;
  doc["batch_id"] = data.batchId;
  doc["timestamp"] = data.timestamp;
  doc["temperature"] = data.temperature;
  doc["humidity"] = data.humidity;
  doc["ph"] = data.ph;
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  int httpResponseCode = http.POST(jsonString);
  
  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.printf("HTTP Response: %d - %s\n", httpResponseCode, response.c_str());
  } else {
    Serial.printf("HTTP Error: %d\n", httpResponseCode);
  }
  
  http.end();
}

void printSensorData(SensorData data) {
  Serial.println("=== Sensor Reading ===");
  Serial.printf("Device ID: %s\n", data.deviceId.c_str());
  Serial.printf("Batch ID: %s\n", data.batchId.c_str());
  Serial.printf("Temperature: %.2f°C\n", data.temperature);
  Serial.printf("Humidity: %.2f%%\n", data.humidity);
  Serial.printf("pH: %.2f\n", data.ph);
  Serial.printf("Timestamp: %s\n", data.timestamp.c_str());
  Serial.println("====================");
}