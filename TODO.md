# For next board revision
* Connect MCU reset to the programming header, it's not possible to flash the MCU when it's in sleep mode
* RFU consumes around 500 uA when pins are floating in sleep mode - tie Reset and all SPI pins to vcc with a resistor - interestingly, the power consumption rises from 100 uA to 500 uA slowly when no resistors are used
* Add a pull down to L96 wakeup pin
* Issue between schematic and PCB - L96 reset pin is connected to BATT+ on PCB, but not in schematic
* connect all unused MCU pins to ground to reduce power consumption due to noise
* put 0R resistors in power line of each device for measuring the power consumption of each piece

# Next software revision
* Consider sending AGPS data over lora to device to speed up the GPS fix
