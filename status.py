import paho.mqtt.client as mqtt

def on_message(client, userdata, msg):
    print(msg.payload)


if __name__ == "__main__":
    print "Start"
    broker="broker.hivemq.com"
    client = mqtt.Client()
    client.connect(broker, 1883)
    client.subscribe("/status")
    client.on_message = on_message

    client.loop_forever()

