#!/usr/bin/env python

from pygame import mixer

import RPi.GPIO as GPIO
import time

###################################################
# Setup
###################################################

# Board setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# LED setup
colors = [0x00FF00, 0x0000FF, 0xFFFF00, 0x00FFFF, 0xFF00FF, 0xFFFFFF, 0x9400D3]

############## GPIO 20 is broken on my personal board ##############
configuredLines = {
	'line1':{'redPinNum':13, 'greenPinNum':19, 'bluePinNum':26},
	'line2':{'redPinNum':16, 'greenPinNum':4, 'bluePinNum':21},
	'line3':{'redPinNum':17, 'greenPinNum':27, 'bluePinNum':22}
}

for ledLine in configuredLines:
	ledPins = configuredLines[ledLine]
	for i in ledPins:
		GPIO.setup(ledPins[i], GPIO.OUT)
		GPIO.output(ledPins[i], GPIO.HIGH)

	redPin = GPIO.PWM(ledPins['redPinNum'], 2000)
	greenPin = GPIO.PWM(ledPins['greenPinNum'], 2000)
	bluePin = GPIO.PWM(ledPins['bluePinNum'], 2000)
	redPin.start(0)
	greenPin.start(0)
	bluePin.start(0)

	configuredLines[ledLine]['redPin'] = redPin
	configuredLines[ledLine]['greenPin'] = greenPin
	configuredLines[ledLine]['bluePin'] = bluePin 

# Sonar sensor setup
echoPin = 5
triggerPin = 6
GPIO.setup(echoPin, GPIO.IN)
GPIO.setup(triggerPin, GPIO.OUT)

# Servo setup
dutyCycle = 7.5
servoPin = 12
GPIO.setup(servoPin, GPIO.OUT)

pwmServo = GPIO.PWM(servoPin, 50)
pwmServo.start(dutyCycle)

# Audio setup
'''
mixer.init()
mixer.music.load('Get outta here.mp3')
mixer.music.play()
time.sleep(5)
mixer.stop()
#audioSound.set_volume(0.0)
'''
###################################################
# Functions
###################################################

def map(x, in_min, in_max, out_min, out_max):
	return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def setColor(col, configuredLine):
	r_pin = configuredLine['redPin']
	b_pin = configuredLine['bluePin']
	g_pin = configuredLine['greenPin']
	redVal = (col & 0x110000) >> 16
	blueVal = (col & 0x001100) >> 8
	greenVal = (col & 0x000011) >> 0

	redVal = map(redVal, 0, 255, 0, 255)
	blueVal = map(blueVal, 0, 255, 0, 255)
	greenVal = map(greenVal, 0, 255, 0, 255)

	r_pin.ChangeDutyCycle(redVal)
	b_pin.ChangeDutyCycle(blueVal)
	g_pin.ChangeDutyCycle(greenVal)

def distance():
	GPIO.output(triggerPin, GPIO.LOW)

	# Let the sensor settle before sampling distance again
	time.sleep(0.01)

	GPIO.output(triggerPin, GPIO.HIGH)

	time.sleep(0.00001)
	GPIO.output(triggerPin, GPIO.LOW)
	
	StartTime = time.time()
	StopTime = time.time()

	# Save StartTime
	while GPIO.input(echoPin) == 0:
		StartTime = time.time()

	# Save time of arrival
	while GPIO.input(echoPin) == 1:
		StopTime = time.time()

	timeElapsed = StopTime - StartTime

	# Multiply with the sonic speed (34300 cm/s) and divide by 2, because there and back
	distance = (timeElapsed * 34300) / 2

	# Distance is in centimeters
	return distance

###################################################
# Main
###################################################

try:
	colorIndex = 0
	while True:

		# Check to see if there isn't something in front of the house
		if distance() > 100.0:

			# Iterate over all of the LED lines and set them to have different colors
			lineNumber = 0
			for lineName in sorted(configuredLines):
				lineColorIndex = (colorIndex + lineNumber) % len(colors)
				setColor(colors[lineColorIndex], configuredLines[lineName])
				lineNumber += 1

		# Alarm if there is something in front of the house
		else:
			for lineName in configuredLines:
				setColor(0xFF0000, configuredLines[lineName])

		if colorIndex > len(colors) - 1:
			colorIndex = 0
		else:
			colorIndex += 1
		time.sleep(3)

except KeyboardInterrupt:
	print "Terminating: User halted script."
	GPIO.cleanup()

'''
try:
	while True:
		for col in colors:
			for lineName in configuredLines:
				setColor(col, configuredLines[lineName])
				time.sleep(1.0)

except KeyboardInterrupt:
	redPin.stop()
	bluePin.stop()
	greenPin.stop()
	for i in ledPins:
		GPIO.output(ledPins[i], GPIO.HIGH)
	GPIO.cleanup()
'''
'''
try:
	while True:
		dist = distance()
		print "dist:", dist
		time.sleep(0.01)
except KeyboardInterrupt:
	GPIO.cleanup()
'''
'''
try:
	while True:
		dutyCycle = float(input("Enter duty cycle; Left=5; Right = 10:"))
		pwmServo.ChangeDutyCycle(dutyCycle)
except KeyboardInterrupt:
	GPIO.cleanup()
'''
