#include <Arduino.h>

#include "sets.h"

#include <DHT.h>

DHT dht11(DHT11_PIN, DHT11);

#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP280.h>

Adafruit_BMP280 bmp;

#include <GTimer.h>

#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>

static AsyncWebServer server(API_PORT);

GTimer<millis> SensorTimer(SENSOR_READ_INTERVAL, true);

void setup() {
    Serial.begin(115200);
    Serial.println();

    sett_begin();

    server.begin();

    Wire.begin(BMP280_SDA_PIN, BMP280_SCL_PIN);

    Serial.println(db[kk::wifi_ssid]);

    Serial.print("SETUP | LED is now ");
    Serial.println(db[kk::switch_state] ? "ON" : "OFF");

    if (!bmp.begin(0x76)) {
        Serial.println("Could not find a valid BMP280 sensor, check wiring!");
        while (1);
    }
    
    Serial.println("BMP280 sensor found!");

    bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,
                    Adafruit_BMP280::SAMPLING_X2,
                    Adafruit_BMP280::SAMPLING_X16,
                    Adafruit_BMP280::FILTER_X16,  
                    Adafruit_BMP280::STANDBY_MS_500);

    server.on("/", HTTP_GET, [](AsyncWebServerRequest *request){
        request->send(200, "text/plain", "API is online. Use /weather");
    });

    server.on("/weather", HTTP_GET, [](AsyncWebServerRequest *request){
        if (isnan(tempC) || isnan(humidity) || isnan(pressure)) {
            request->send(500, "text/plain", "Failed to read from sensor");
            return;
        }

        String json = "{";
        json += "\"temp\": " + String(tempC) + ",";
        json += "\"humidity\": " + String(humidity) + ",";
        json += "\"pressure\": " + String(pressure);
        json += "}";

        request->send(200, "application/json", json);
    });
}

void loop() {
    if (SensorTimer.tick()) {
        tempC = bmp.readTemperature();
        humidity = dht11.readHumidity();
        pressure = bmp.readPressure() / 100.0F;
    }

    sett_loop();
}