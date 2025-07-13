#include <TinyGPS++.h>
#include <HardwareSerial.h>
#include <SPI.h>
#include <LoRa.h>

// Define pins (adjust based on your board)
#define GPS_RX 16  // GPIO for RX
#define GPS_TX 17  // GPIO for TX
#define LORA_SS 18
#define LORA_RST 14
#define LORA_DIO0 26

TinyGPSPlus gps;
HardwareSerial gpsSerial(1); // Using Serial1 for GPS

String vehicleID = "1";

void setup() {
  Serial.begin(115200);
  gpsSerial.begin(9600, SERIAL_8N1, GPS_RX, GPS_TX);

  // LoRa Init
  Serial.println("Initializing LoRa...");
  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);
  if (!LoRa.begin(433E6)) {
    Serial.println("LoRa init failed. Check connections.");
    while (1);
  }
  Serial.println("LoRa init succeeded.");
}

void loop() {
  // Read GPS data
  while (gpsSerial.available() > 0) {
    gps.encode(gpsSerial.read());
  }

  // Every second, broadcast message
  static unsigned long lastSendTime = 0;
  if (millis() - lastSendTime > 1000) {
    lastSendTime = millis();

    double lat = gps.location.isValid() ? gps.location.lat() : 28.7041;
    double lon = gps.location.isValid() ? gps.location.lng() : 77.1025;
    double speed = gps.speed.kmph();

    // Format message
    String message = "ID:" + vehicleID +
                     ",LAT:" + String(lat, 4) +
                     ",LON:" + String(lon, 4) +
                     ",SPEED:" + String(speed, 2) +
                     ",DIR:N"; // Direction is placeholder for now

    // Send LoRa message
    LoRa.beginPacket();
    LoRa.print(message);
    LoRa.endPacket();

    Serial.println("Sent: " + message);
  }

  // Check for incoming messages
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    String incoming = "";
    while (LoRa.available()) {
      incoming += (char)LoRa.read();
    }
    Serial.println("Received: " + incoming);
  }
}
