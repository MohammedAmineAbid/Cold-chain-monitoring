#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClientSecure.h>
#include <DHT.h>

#define DHTPIN 5
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

// WiFi
const char* ssid = "VIP ROSAMAR 2.4G";
const char* password = "ROSA2024";

// API Django (HTTPS obligatoire)
const char* serverUrl = "https://amineabid.pythonanywhere.com/api/ingest/";

// Token du capteur
const char* SENSOR_TOKEN = "90058e8df4f76b6c155b7f6f7ddc7865";

void setup() {
  Serial.begin(115200);
  dht.begin();

  WiFi.begin(ssid, password);
  Serial.print("Connexion WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\n✅ WiFi connecté !");
}

void loop() {
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("❌ Erreur lecture DHT");
    delay(5000);
    return;
  }

  // 🔐 HTTPS obligatoire
  WiFiClientSecure client;
  client.setInsecure();  // accepte certificat PythonAnywhere

  HTTPClient http;
  http.begin(client, serverUrl);
  http.addHeader("Content-Type", "application/json");

  String payload = "{";
  payload += "\"sensor_token\":\"" + String(SENSOR_TOKEN) + "\",";
  payload += "\"temperature\":" + String(temperature, 1) + ",";
  payload += "\"humidity\":" + String(humidity, 1);
  payload += "}";

  Serial.println("📤 Envoi : " + payload);

  int httpCode = http.POST(payload);

  Serial.print("📡 Code HTTP : ");
  Serial.println(httpCode);

  if (httpCode > 0) {
    Serial.println("📥 Réponse serveur :");
    Serial.println(http.getString());
  } else {
    Serial.println("❌ Erreur HTTP");
  }

  http.end();

  delay(1200000); // envoi toutes les 20 minutes
}