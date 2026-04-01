#include <DHT.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// Pin definitions
#define DHT_PIN 4
#define DHT_TYPE DHT22
#define ONEWIRE_BUS 2
#define PH_SENSOR_PIN A0

// Sensor objects
DHT dht(DHT_PIN, DHT_TYPE);
OneWire oneWire(ONEWIRE_BUS);
DallasTemperature dallas(&oneWire);

void setup() {
  Serial.begin(115200);
  delay(2000);
  
  Serial.println("FermTrack Sensor Test");
  Serial.println("====================");
  
  // Initialize sensors
  dht.begin();
  dallas.begin();
  
  Serial.printf("Found %d DS18B20 temperature sensors\n", dallas.getDeviceCount());
  Serial.println();
}

void loop() {
  Serial.println("--- Sensor Reading ---");
  
  // Test DHT22
  float humidity = dht.readHumidity();
  float dhtTemp = dht.readTemperature();
  
  if (isnan(humidity) || isnan(dhtTemp)) {
    Serial.println("DHT22: Failed to read sensor!");
  } else {
    Serial.printf("DHT22 - Temperature: %.2f°C, Humidity: %.2f%%\n", dhtTemp, humidity);
  }
  
  // Test DS18B20
  dallas.requestTemperatures();
  float dsTemp = dallas.getTempCByIndex(0);
  
  if (dsTemp == DEVICE_DISCONNECTED_C) {
    Serial.println("DS18B20: Sensor not connected!");
  } else {
    Serial.printf("DS18B20 - Temperature: %.2f°C\n", dsTemp);
  }
  
  // Test pH sensor (raw reading)
  int phRaw = analogRead(PH_SENSOR_PIN);
  float voltage = phRaw * (3.3 / 4095.0);
  
  Serial.printf("pH Sensor - Raw: %d, Voltage: %.3fV\n", phRaw, voltage);
  
  // Simple pH conversion (needs calibration)
  float estimatedPH = 7.0 - ((voltage - 1.65) * 3.0);
  Serial.printf("pH Sensor - Estimated pH: %.2f (uncalibrated)\n", estimatedPH);
  
  Serial.println();
  delay(2000); // Read every 2 seconds for testing
}