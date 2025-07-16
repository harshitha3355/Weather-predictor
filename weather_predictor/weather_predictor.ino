#include <Wire.h>
#include <Adafruit_BMP085.h>
#include <DHT.h>
#include <LiquidCrystal_I2C.h>
#include <ESP8266WiFi.h>

// Hardware Config
#define DHTPIN D4
#define DHTTYPE DHT11
#define RAIN_SENSOR A0

// ThingSpeak Config
const char* ssid = "mmm";
const char* password = "123456789";
const char* server = "api.thingspeak.com";
String apiKey = "2ILFSOB3VVA5D69A";
String channelID = "3003731";

// Initialize Sensors/LCD
DHT dht(DHTPIN, DHTTYPE);
Adafruit_BMP085 bmp;
LiquidCrystal_I2C lcd(0x27, 16, 2); // I2C address 0x27 for 16x2 LCD

void setup() {
  Serial.begin(115200);
  dht.begin();
  bmp.begin();
  lcd.init();
  lcd.backlight();
  
  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("WiFi connected");
}

void loop() {
  
  // Read Sensors
  float temp = dht.readTemperature();      // °C
  float humidity = dht.readHumidity();     // %
  float pressure = bmp.readPressure() / 100.0; // hPa
  float rain = analogRead(RAIN_SENSOR);    // 0-1023 (higher = drier)

  // Display on LCD
  lcd.setCursor(0, 0);
  lcd.print("T:" + String(temp) + "C H:" + String(humidity) + "%");
  lcd.setCursor(0, 1);
  lcd.print("P:" + String(pressure) + "hPa");

  // Send to ThingSpeak
  sendToThingSpeak(temp, humidity, pressure, rain);
  
  // Fetch ML Prediction (every 10 minutes)
  static unsigned long lastPredictionTime = 0;
  if (millis() - lastPredictionTime > 600000) {
    fetchPrediction();
    lastPredictionTime = millis();
  }

  delay(2000); // Wait 2 sec between readings
}

// Send data to ThingSpeak
void sendToThingSpeak(float temp, float humidity, float pressure, float rain) {
  WiFiClient client;
  if (client.connect(server, 80)) {
    String postStr = apiKey;
    postStr += "&field1=" + String(temp);
    postStr += "&field2=" + String(humidity);
    postStr += "&field3=" + String(pressure);
    postStr += "&field4=" + String(rain);
    postStr += "\r\n\r\n";

    client.print("POST /update HTTP/1.1\n");
    client.print("Host: api.thingspeak.com\n");
    client.print("Connection: close\n");
    client.print("X-THINGSPEAKAPIKEY: " + apiKey + "\n");
    client.print("Content-Type: application/x-www-form-urlencoded\n");
    client.print("Content-Length: ");
    client.print(postStr.length());
    client.print("\n\n");
    client.print(postStr);
  }
  client.stop();
}

// Fetch ML prediction from ThingSpeak (Field 5)
void fetchPrediction() {
  WiFiClient client;
  if (client.connect(server, 80)) {
    client.print("GET /channels/" + channelID + "/fields/5/last.txt HTTP/1.1\n");
    client.print("Host: api.thingspeak.com\n");
    client.print("Connection: close\n\n");

    delay(500);
    String response = client.readString();
    int prediction = response.charAt(response.length() - 1) - '0'; // Get last char (0 or 1)

    lcd.setCursor(12, 1);
    lcd.print("Rain:" + String(prediction == 1 ? "Y" : "N"));
  }
  client.stop();
}