# For next board revision
* Connect MCU reset to the programming header, it's not possible to flash the MCU when it's in sleep mode
* Add a pull up to the RFM CS pin to avoid increased power consumption when MCU is in sleep (pins are floating)
* Add a pull down to L96 wakeup pin
* Issue between schematic and PCB - L96 reset pin is connected to BATT+ on PCB, but not in schematic

# Next software revision
* Consider sending AGPS data over lora to device to speed up the GPS fix
