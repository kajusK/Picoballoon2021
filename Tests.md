# Development tests
* Send GPS to sleep, measure supply current dropped significantly, wake it up, make sure NMEA data are coming
* Send all devices to sleep/suspend, measure the current is in range of uA
* Make sure the GPS is able to get fix in the first fix scenario
* Make sure the GPS gets fix within 10 seconds if had fix before and was sleeping for 30 minutes afterwards


# Prod tests
* Connect battery, the device should initialize, measure all required data and send it over LoRa to cloud
* Make sure the current drops to uA range
* Make sure the device wakes up after 30 minutes and sends data again
* Make sure the device times out waiting for GPS if no GPS signal is available
* Put device in freezer for a week, make sure it continues to operate for the whole time
