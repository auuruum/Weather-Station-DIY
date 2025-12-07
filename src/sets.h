#pragma once

#define PROJECT_NAME "Weather Station"

// Pin definitions
#define LED_PIN 2
#define DHT11_PIN  15

// Constants for temperature and humidity ranges
#define MAX_TEMP_C 50
#define MIN_TEMP_C 0

#define MAX_HUMIDITY 100
#define MIN_HUMIDITY 0

#define COMFORT_MIN 20.0
#define COMFORT_MAX 24.0

// Other constants
#define DHT_READ_INTERVAL 3000  // milliseconds
#define API_PORT 81 // Dont set to 80, it is used by settings server

// Dont touch below this line
extern float tempC;
extern float humidity;

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