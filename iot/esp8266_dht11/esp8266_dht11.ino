#include <ArduinoJson.h>
#include <DHT.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266WiFi.h>

// Environment variables (update in docs)
const char *WIFI_SSID = "YOUR_WIFI";
const char *WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char *API_URL = "http://192.168.1.10:8000/api/ingest/";
const char *SENSOR_TOKEN = "YOUR_SENSOR_TOKEN";

#define DHTPIN D4
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

void connectWifi() {
  if (WiFi.status() == WL_CONNECTED) {
    return;
  }
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  uint8_t retries = 0;
  while (WiFi.status() != WL_CONNECTED && retries < 20) {
    delay(500);
    retries++;
  }
}

void setup() {
  Serial.begin(115200);
  dht.begin();
  connectWifi();
}

void sendMeasurement(float temperature, float humidity) {
  if (WiFi.status() != WL_CONNECTED) {
    connectWifi();
  }
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi not available, skipping payload");
    return;
  }

  WiFiClient client;
  HTTPClient http;

  if (!http.begin(client, API_URL)) {
    Serial.println("HTTP begin failed");
    return;
  }

  http.addHeader("Content-Type", "application/json");

  StaticJsonDocument<256> payload;
  payload["sensor_token"] = SENSOR_TOKEN;
  payload["temperature"] = temperature;
  payload["humidity"] = humidity;

  String json;
  serializeJson(payload, json);

  int status = http.POST(json);

  if (status > 0) {
    Serial.printf("Measurement sent. Status: %d\n", status);
    Serial.println(http.getString());
  } else {
    Serial.printf("HTTP error: %d\n", status);
  }

  http.end();
}

void loop() {
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Failed to read from DHT sensor!");
    delay(10000);
    return;
  }

  sendMeasurement(temperature, humidity);

  // Wait 20 minutes
  for (int i = 0; i < 1200; i++) {
    delay(1000);
    if (WiFi.status() != WL_CONNECTED) {
      connectWifi();
    }
  }
}
