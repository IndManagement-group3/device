#!/usr/bin/env python
import paho.mqtt.client as mqtt

turned = 0
power = 0

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
	print("Connected with result code", str(rc))

	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.
	client.subscribe("/fan/turn")
	client.subscribe("/fan/power")
	client.subscribe("/fan/update")

	send_status(client)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
	global turned, power

	if msg.topic == "/fan/turn":
		turned = int(msg.payload.decode("utf-8"))

		if turned == 1:
			state = "on"
		else:
			state = "off"

		print("Fan is turned", state)


	elif msg.topic == "/fan/power":
		power = int(msg.payload.decode("utf-8"))

		print("Power is {0}%".format(power))

	send_status(client)

def send_status(client):
	global turned, power

	status = "{0};{1}".format(turned, power)
	print(status)
	client.publish("/fan/status", payload=status, retain=True)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.31.26")

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()