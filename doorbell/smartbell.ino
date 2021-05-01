#include <ArduinoOTA.h>
#include <ESPmDNS.h>
#include <NTPClient.h>
#include <PubSubClient.h>
#include <WiFi.h>
#include <WiFiUdp.h>

#include "smartbell_secrets.h"
const char* ssid = SECRET_MAIN_SSID;
const char* pass = SECRET_MAIN_PASS;
const char* ssidFallback = SECRET_FALLBACK_SSID;
const char* passFallback = SECRET_FALLBACK_PASS;


// Important: Passwords and OTA
// This code is designed to run on a secure private network. Normally, the
// device should be connected to your secured local network and only allows
// for an OTA update if you enable this function via MQTT (see command below)
// This is a problem if you want to change your Wifi password or if your MQTT
// broker moves to a different address and you want to update the smart bell
// with new credentials or addresses. Therefore, if the device cannot connect
// to your Wifi or cannot connect to the MQTT broker for a few times it will
// start its own Wifi with the credentials below. You probably want to change
// them to be unique to your device and you want to save them somewhere in
// case you need to recover the smart bell. In this fallback mode it will only
// allow an OTA update so you can set new credentials. After a minute it will
// try again to connect to your regular network, so it will not stay down too
// long after a short outage of your infrastructure.

const char* hostname = "smartbell";
const char* mqttTopicLast = "smartbell/last";
const char* mqttTopicLastRequest = "smartbell/last/get";
const char* mqttTopicOTA = "smartbell/ota";
const char* mqttTopicRinging = "smartbell/ringing";
const char* mqttTopicStatus = "smartbell/status";
const char* mqttTopicStatusRequest = "smartbell/status/get";
const char* mqttTopicTest = "smartbell/test";

const byte    pinRinging = 18;
IPAddress     myip;
IPAddress     mqttServer;
int           mqttPort;
boolean       otaEnabled;
boolean       isRinging;
unsigned long lastTime = 0;
unsigned long ringDebounce;

WiFiClient    wifiClient;
WiFiUDP       ntpUDP;

// Zero offset from UTC, 10 hour refresh of system time (in ms)
NTPClient timeClient(ntpUDP, "europe.pool.ntp.org", 0, 36000000);
PubSubClient mqttClient(wifiClient);


void setup() {
  Serial.begin(115200);
  Serial.println("Starting...");

  pinMode(pinRinging, INPUT_PULLUP);

  WiFi.hostname(hostname);
  ArduinoOTA.setHostname(hostname);

  mqttClient.setCallback(mqttCallback);
}

void loop() {
  //Normal state: Connect to Wifi infrastructure and MQTT broker
  int wifiStatus = WiFi.begin(ssid, pass);
  int retries = 0;
  char mqtt[25];
  unsigned long timeout;

  while (retries < 3) {
    retries++;
    Serial.print("Connecting to Wifi, try ");
    Serial.print(retries);
    Serial.print("... ");

    timeout = millis();
    while (wifiStatus != WL_CONNECTED && millis()-timeout < 20000) {
      delay(100);
      wifiStatus = WiFi.status();
    }
    myip = WiFi.localIP();
    Serial.println("[OK]");

    Serial.print("Starting mDNS... ");
    if (!MDNS.begin(hostname)) {
        Serial.println("[Fail]");
    } else {
        Serial.println("[OK]");
        Serial.print("Searching for MQTT server... ");
        int responses = MDNS.queryService("mqtt", "tcp");
        if (responses == 0) {
          Serial.println("[Fail]");
        } else {
          mqttServer = MDNS.IP(0);
          mqttPort = MDNS.port(0);
          sprintf(mqtt, "[%d.%d.%d.%d:%d]", mqttServer[0], mqttServer[1], mqttServer[2], mqttServer[3], mqttPort);
          mqttClient.setServer(mqttServer, mqttPort);
          Serial.println(mqtt);
        }
    }

    Serial.print("Starting ntp... ");
    timeClient.begin();
    if (timeClient.forceUpdate()) {
      Serial.print(timeClient.getFormattedTime());
      Serial.println(" [OK]");
    } else {
      Serial.println("[Fail]");
    }
    
    while (wifiStatus == WL_CONNECTED) {
      Serial.print("Trying MQTT... ");
      timeout = millis();
      while (!mqttClient.connected() && millis()-timeout < 10000) {
        mqttClient.connect(hostname);
        delay(1000);
      }
      if (!mqttClient.connected()) {
        Serial.println("[Fail]");
        break;
      }
      Serial.println("[OK]");
      retries = 0;
      normalSetup();
      Serial.println("Entering normal loop.");
      while (mqttClient.connected() && WiFi.status() == WL_CONNECTED) {
        normalLoop();
        yield();
      }
      Serial.println("Disconnected.");
    }
  }
  mqttClient.disconnect();
  MDNS.end();
  WiFi.disconnect();

  //Fallback: Offer a hotspot to allow for an OTA update
  Serial.println("Setting up AP as fallback.");
  if (WiFi.softAP(ssidFallback, passFallback)) {
    ArduinoOTA.begin();
    timeout = millis();
    while (millis() - timeout < 60000) {
      ArduinoOTA.handle();
      yield();
    }
  }
  Serial.println("Let's see if our Wifi is back...");
  ESP.restart();
}

void normalSetup() {
  Serial.print("Setup for normal mode... ");
  isRinging = false;
  ringDebounce = millis();
  otaEnabled = false;
    mqttClient.subscribe(mqttTopicOTA);
  mqttClient.subscribe(mqttTopicLastRequest);
  mqttClient.subscribe(mqttTopicStatusRequest);
  mqttClient.subscribe(mqttTopicTest);
  Serial.println("[Done]");
}

void normalLoop() {
  mqttClient.loop();
  timeClient.update();
  checkRinging();
  if (otaEnabled) {
    ArduinoOTA.handle();
  }
}

bool checkRinging() {
  char status[80];
  bool nowRinging = (digitalRead(pinRinging) == HIGH); //Pulled low by optocoupler if ringing

  if (nowRinging && !isRinging && millis() - ringDebounce > 3000) {
    ringDebounce = millis();
    lastTime = timeClient.getEpochTime();
    Serial.println("Palim, palim!");
    sprintf(status, "{\"time\": %lu, \"type\": \"Doorbell\"}", lastTime);
    mqttClient.publish(mqttTopicRinging, status);
  }
  isRinging = nowRinging;
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
    char status[80];
    Serial.print("Received MQTT topic ");
    Serial.println(topic);
    if (strcmp(topic, mqttTopicLastRequest) == 0) {
      sprintf(status, "%d", lastTime);
      mqttClient.publish(mqttTopicLast, status);
    } else if (strcmp(topic, mqttTopicOTA) == 0) {
      otaEnabled = payload[0] == '1';
      if (otaEnabled)
        ArduinoOTA.begin();
      else
        ESP.restart();
      Serial.print("OTA update set to ");
      Serial.println(otaEnabled);
    } else if (strcmp(topic, mqttTopicStatusRequest) == 0) {
      sprintf(status, "%s: %d.%d.%d.%d: MQTT: %d.%d.%d.%d:%d OTA: %d", hostname, myip[0], myip[1], myip[2], myip[3], mqttServer[0], mqttServer[1], mqttServer[2], mqttServer[3], mqttPort, otaEnabled);
      mqttClient.publish(mqttTopicStatus, status);
    } else if (strcmp(topic, mqttTopicTest) == 0) {
      lastTime = timeClient.getEpochTime();
      sprintf(status, "{\"time\": %lu, \"type\": \"Test\"}", lastTime); 
      mqttClient.publish(mqttTopicRinging, status);
    }
}
