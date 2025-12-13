#include <ArduinoJson.h>
#include <DHT.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266WiFi.h>

const char *WIFI_SSID = "YOUR_WIFI";
const char *WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// USE INGEST ENDPOINT (IMPORTANT)
const char *API_URL = "http://YOUR_WIFI_IP:8000/api/ingest/";

// PUT THE SENSOR TOKEN FROM DJANGO ADMIN
const char *SENSOR_TOKEN = "YOUR_SENSOR_TOKEN";

#define DHTPIN D4
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

void connectWifi() {
  if (WiFi.status() == WL_CONNECTED) return;

  Serial.print("Connecting to WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println(" Connected!");
}

void sendMeasurement(float temperature, float humidity) {
  if (WiFi.status() != WL_CONNECTED) connectWifi();

  WiFiClient client;
  HTTPClient http;

  http.begin(client, API_URL);
  http.addHeader("Content-Type", "application/json");

  StaticJsonDocument<200> payload;
  payload["sensor_token"] = SENSOR_TOKEN;
  payload["temperature"] = temperature;
  payload["humidity"] = humidity;

  String json;
  serializeJson(payload, json);

  Serial.println("Sending: " + json);

  int status = http.POST(json);
  Serial.print("Response code: ");
  Serial.println(status);

  if (status > 0) {
    Serial.println(http.getString());
  }

  http.end();
}

void setup() {
  Serial.begin(115200);
  dht.begin();
  connectWifi();
}

void loop() {
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("Failed to read DHT");
    delay(5000);
    return;
  }

  sendMeasurement(temperature, humidity);
  delay(10000);
}
