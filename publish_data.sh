#!/bin/bash

while :
do 
	python2 scripts/wifi_rssi.py
	python2 scripts/mpu6050.py
done
