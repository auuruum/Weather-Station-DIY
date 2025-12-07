#include <Arduino.h>

#include "sets.h"

#include <DHT.h>

DHT dht11(DHT11_PIN, DHT11);

#include <GTimer.h>

#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>

static AsyncWebServer server(API_PORT);

GTimer<millis> dhtTimer(DHT_READ_INTERVAL, true);

void setup() {
    Serial.begin(115200);
    Serial.println();

    sett_begin();

    server.begin();

    Serial.println(db[kk::wifi_ssid]);

    Serial.print("SETUP | LED is now ");
    Serial.println(db[kk::switch_state] ? "ON" : "OFF");

    server.on("/", HTTP_GET, [](AsyncWebServerRequest *request){
        request->send(200, "text/plain", "API is online. Use /weather");
    });

    server.on("/weather", HTTP_GET, [](AsyncWebServerRequest *request){
        if (isnan(tempC) || isnan(humidity)) {
            request->send(500, "text/plain", "Failed to read from sensor");
            return;
        }

        String json = "{";
        json += "\"temp\": " + String(tempC) + ",";
        json += "\"humidity\": " + String(humidity);
        json += "}";

        request->send(200, "application/json", json);
    });
}

void loop() {
    if (dhtTimer.tick()) {
        tempC = dht11.readTemperature();
        humidity = dht11.readHumidity();
    }

    sett_loop();
}