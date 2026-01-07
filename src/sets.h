#pragma once

// Can easly be modified to suit your project
#define PROJECT_NAME "Weather Station"
#define LOCATION_ALTITUDE 112 // meters above sea level (112 for Vilnius)

// Pin definitions
#define LED_PIN 2
#define DHT11_PIN  15

#define BMP280_SDA_PIN 21
#define BMP280_SCL_PIN 22

// Constants for temperature and humidity ranges
#define MAX_TEMP_C 50
#define MIN_TEMP_C 0

#define MAX_HUMIDITY 100
#define MIN_HUMIDITY 0

// Pressure range for BMP280 (atmospheric pressure in hPa)
// BMP280 typical full-scale range: 300..1100 hPa (datasheet)
#define MIN_PRESSURE 300
#define MAX_PRESSURE 1100

#define COMFORT_MIN 20.0
#define COMFORT_MAX 24.0

// Other constants
#define SENSOR_READ_INTERVAL 3000  // milliseconds
#define API_PORT 81 // Dont set to 80, it is used by settings server
#define SEALEVELPRESSURE_HPA (1013.25)
constexpr char32_t FORECASTER_INTERVAL_MS = 30UL * 60UL * 1000UL;   // 30 minutes

// Dont touch below this line
extern float tempC;
extern float humidity;
extern float pressure;

#include <GyverDBFile.h>
#include <SettingsGyver.h>

extern GyverDBFile db;
extern SettingsGyver sett;

void sett_begin();
void sett_loop();

DB_KEYS(
    kk,
    wifi_ssid,
    wifi_pass,
    close_ap,
    switch_state
);