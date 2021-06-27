# For next board revision
* Connect MCU reset to the programming header, it's not possible to flash the MCU when it's in sleep mode
* RFU consumes around 500 uA when pins are floating in sleep mode - tie Reset and all SPI pins to vcc with a resistor - interestingly, the power consumption rises from 100 uA to 500 uA slowly when no resistors are used
* Issue between schematic and PCB - L96 reset pin is connected to BATT+ on PCB, but not in schematic, should be floating or tied to vcc
* connect all unused MCU pins to ground to reduce power consumption due to noise
* put 0R resistors in power line of each device for measuring the power consumption of each piece
* Remove GPS fencing pin and connect EXTINT0 pin for entering GPS standby immediately after powering up the MCU.
* add pull down to FORCE_ON GPS pin
* Test if L96 works, was not able to get first fix below 20min on the prototype

# Next software revision
* Consider sending AGPS data over lora to device to speed up the GPS fix
