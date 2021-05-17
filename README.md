# Home Automation
 Home Assistant configuration and helper scripts

[![Yaml Lint](https://github.com/JRInge/ha/actions/workflows/yaml.yml/badge.svg)](https://github.com/JRInge/ha/actions/workflows/yaml.yml) [![Python checks](https://github.com/JRInge/ha/actions/workflows/python.yml/badge.svg)](https://github.com/JRInge/ha/actions/workflows/python.yml)

This repo gathers together bits of code, configuration, etc. that I use in my home automation system, based on [Home Assistant Core](https://www.home-assistant.io/). Implementation notes are in the [wiki](https://github.com/JRInge/ha/wiki).

Main features:
* Home-brew smart doorbell interface. This wifi-enables a conventional 9V door chime to let it trigger events in Home Assistant via MQTT. The interface is coded to plug-and-play, auto-discovering its MQTT broker and announcing itself to Home Assistant.
* Efergy e2 Energy Monitor. Hooked up via an RTL-SDR radio.
* COVID-19 infection rate sensors. Using UK government data for my local area.
* Recycling day sensors. Using data from my local council to check which bins to put out each week.
