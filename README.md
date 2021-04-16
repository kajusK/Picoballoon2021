Picoballoon Challenge 2021, Deadbadger probe
============================================

This probe was designed [Picoballoon Challenge](https://www.hvezdarna.cz/novinky/picoballoon-challenge-2021/)
organised by Brno Observatory and Planetarium. A goal of this competition
is to make a probe under 20 grams that would be launched on ballon to altitudes
around 5-15 km. Only requirement except weight is sending current altitude of the probe.

![probe](img/probe.jpg)

A detailed description is available at [deadbadger.cz](https://deadbadger.cz/projects/picoballoon-2021),
tracking site is at [bal.deadbadger.cz](https://bal.deadbadger.cz).

The probe contains
  * STM32F051 MCU
  * MS5607 Pressure and temperature sensor
  * Quectel L96 GPS module with integrated antenna
  * RFM95 LoRa Transceiver
  * MCP1640 based 3.3V boost regulator

Firmware
--------
As the commonly used [LMIC](https://github.com/matthijskooijman/arduino-lmic/tree/master/src)
library is quite bulky and far from perfect, I wrote my own LoRaWan library
inspired by [TinyLoRa](https://github.com/adafruit/TinyLoRa).

The main loop does about this:
  * Power up, initialize peripherals
  * Measure system voltages, pressure
  * Wait for GPS data or timeout
  * Power off GPS
  * Send data over LoRa (ABP, unconfirmed uplink)
  * Power off RFM95 trancesiver
  * Power off for 30 minutes
  * Repeat (GPS is powered on every 4th cycle)

Hardware
--------
The board was designed for 0.6 mm thick two sided PCB to reduce weight as
much as possible. Using thicker boards (usually 1.6 mm) changes the antenna
trace impedance, but it should not be that significant.

The programming and debug uart connectors are separated from the main layout
and this piece of the PCB will be snapped off before launch to reduce weight.

Frontend
--------
Data received by [TTN](https://www.thethingsnetwork.org/) are sent over
HTTP integration to custom web server that verifies the
auth header and stores data in sqlite database.

User frontend is written in python, it shows all received packets, flight route
and current position on a [map](https://api.mapy.cz).
