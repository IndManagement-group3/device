#!/usr/bin/env python
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time

pwmpin = 12
pwmfreq = 1000
timeout = 1 #in seconds

devid = "fan"

turned = 0
power = 0
keepalivesync = 0

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD) #pins are numbered according to their physical order on the header
GPIO.setup(pwmpin, GPIO.OUT)
pwm = GPIO.PWM(pwmpin, pwmfreq)
pwm.start(0)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
	print("Connected with result code", str(rc))

	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.
	client.subscribe("/{0}/turn".format(devid))
	client.subscribe("/{0}/power".format(devid))
	client.subscribe("/{0}/update".format(devid))
	client.subscribe("/{0}/keepalive".format(devid))

	update_status(client)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
	global turned, power, keepalivesync

	if msg.topic == "/{0}/keepalive".format(devid):
		keepalivesync = time.clock_gettime(time.CLOCK_REALTIME)

	elif msg.topic == "/{0}/turn".format(devid):
		turned = int(msg.payload.decode("utf-8"))

		if turned == 1:
			state = "on"
		else:
			state = "off"

		print("Fan is turned", state)


	elif msg.topic == "/{0}/power".format(devid):
		power = int(msg.payload.decode("utf-8"))

		print("Power is {0}%".format(power))

	update_status(client)

def update_status(client):
	global turned, power

	pwm.ChangeDutyCycle(power * turned)

	status = "{0};{1}".format(turned, power)
	print(status)
	client.publish("/{0}/status".format(devid), payload=status, retain=True)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set(devid, password="lamepassword")

client.connect("172.16.0.1")

while True:
	for i in range(0,2):
		client.loop()
	
	if (time.clock_gettime(time.CLOCK_REALTIME) - keepalivesync) > timeout:
		turned = 0
		update_status(client)

	#print((time.clock_gettime(time.CLOCK_REALTIME) - keepalivesync))


