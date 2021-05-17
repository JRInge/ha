# Smart Doorbell Interface
![Arduino_ESP32](https://img.shields.io/badge/Arduino-ESP32-9cf?logo=Arduino)

Custom interface to wifi-enable a standard 9V door chime, so that it can be used as a trigger for Home Assistant automations. The interface is based on an ESP32 wifi-enabled MCU, communicating with Home Assistant via MQTT. The ESP32 is programmed to automatically detect the MQTT broker, and announce itself to Home Assistant for easy configuration.

## Hardware

### Schematic
![doorbell_schematic](https://user-images.githubusercontent.com/7988512/117694484-1d155180-b1b7-11eb-98c5-7bfbc8cb109f.png)

### Parts list

* 1 x [AZDelivery D1 Mini ESP32 NodeMCU](https://www.az-delivery.de/en/products/esp32-d1-mini)
* 1 x [4N32 optocoupler](https://media.digikey.com/pdf/Data%20Sheets/Vishay%20Semiconductors/4N32_4N33_Rev_Mar_2017.pdf)
* 1 x [1N5817 Schottky diode](https://www.vishay.com/docs/88525/1n5817.pdf)
* * 2 x 1kΩ resistors
* 1 x 10kΩ resistor

## Software

See [smartbell/smartbell.ino](https://github.com/JRInge/ha/blob/master/doorbell/smartbell/smartbell.ino)
