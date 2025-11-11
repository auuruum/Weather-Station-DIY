#pragma once

#define PROJECT_NAME "Weather Station"

#define LED_PIN 2

#define DHT11_PIN  15

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