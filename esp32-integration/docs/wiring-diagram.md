# ESP32 Wiring Diagram for FermTrack

## Hardware Components

### Required Components
- ESP32 Development Board (ESP32-DevKitC or similar)
- DHT22 Temperature/Humidity Sensor
- DS18B20 Waterproof Temperature Sensor (recommended for fermentation)
- pH Sensor Module (analog output)
- Breadboard and jumper wires
- 4.7kΩ resistor (for DS18B20)

### Optional Components
- 16x2 LCD Display (I2C)
- Status LEDs
- Buzzer for alerts
- External power supply (5V/2A)

## Pin Connections

### ESP32 Pin Assignments
```
GPIO 4  - DHT22 Data Pin
GPIO 2  - DS18B20 Data Pin (OneWire)
GPIO A0 - pH Sensor Analog Output
GPIO 21 - I2C SDA (for LCD - optional)
GPIO 22 - I2C SCL (for LCD - optional)
GPIO 18 - Status LED (optional)
3.3V    - Sensor VCC
GND     - Common Ground
```

### DHT22 Connections
```
DHT22 Pin 1 (VCC) → ESP32 3.3V
DHT22 Pin 2 (Data) → ESP32 GPIO 4
DHT22 Pin 3 (NC) → Not connected
DHT22 Pin 4 (GND) → ESP32 GND
```

### DS18B20 Connections
```
DS18B20 Red (VCC) → ESP32 3.3V
DS18B20 Yellow (Data) → ESP32 GPIO 2 + 4.7kΩ resistor to 3.3V
DS18B20 Black (GND) → ESP32 GND

Note: 4.7kΩ pull-up resistor between Data and VCC is required
```

### pH Sensor Module Connections
```
pH Module VCC → ESP32 3.3V (or 5V depending on module)
pH Module GND → ESP32 GND
pH Module OUT → ESP32 GPIO A0 (ADC pin)
```

## Sensor Placement Considerations

### Temperature Sensors
- DS18B20: Waterproof, place directly in fermentation vessel
- DHT22: Keep in ambient air near fermentation vessel
- Avoid direct sunlight and heat sources

### pH Sensor
- Requires proper calibration with pH 4.0 and pH 7.0 solutions
- Keep probe clean and hydrated
- Some modules require 5V power supply

### Installation Tips
- Use food-grade materials for sensors in contact with fermentation
- Secure all connections to prevent moisture damage
- Consider using a weatherproof enclosure
- Test all sensors before installation

## Power Requirements
- ESP32: 3.3V, ~240mA during WiFi transmission
- DHT22: 3.3V, ~2.5mA
- DS18B20: 3.3V, ~1.5mA
- pH Module: 3.3V-5V, varies by model

Total estimated power consumption: ~300-400mA at 3.3V

## Safety Notes
- Use GFCI protection near water/fermentation vessels
- Ensure all electrical connections are properly insulated
- Do not use non-food-grade materials in contact with fermentation
- Test system thoroughly before deployment