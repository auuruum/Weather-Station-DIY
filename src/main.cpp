#include <Arduino.h>

#include "sets.h"

#include <DHT.h>

DHT dht11(DHT11_PIN, DHT11);

void setup() {
    Serial.begin(115200);
    Serial.println();

    sett_begin();

    Serial.println(db[kk::wifi_ssid]);

    Serial.print("SETUP | LED is now ");
    Serial.println(db[kk::switch_state] ? "ON" : "OFF");
}

void loop() {
    humidity = dht11.readHumidity();
    tempC = dht11.readTemperature();
    
    sett_loop();
}