import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(15, GPIO.OUT)
GPIO.setup(16, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)
GPIO.output(13 , 0)
GPIO.output(15 , 0)
GPIO.output(16, 0)
GPIO.output(18, 0)
pwm_r = GPIO.PWM(22, 500)
pwm_l = GPIO.PWM(11, 500)
pwm_r.start(35)
pwm_l.start(35)
print "Values reseted"

def on_message(client, userdata, msg):
    maneuvers['stop']()
    maneuvers[str(msg.payload.decode("UTF-8"))]()

def counter():
    print("Counterwise")
    GPIO.output(15, True)
    GPIO.output(18, True)

def clockwise():
    print("Clockwise")
    GPIO.output(13, True)
    GPIO.output(16, True)

def forward():
    print("Forward")
    GPIO.output(15, True)
    GPIO.output(16, True)

def backward():
    print("Backward")
    GPIO.output(13, True)
    GPIO.output(18, True)
                                            
def stop():
    print("Stop")
    GPIO.output(13, False)
    GPIO.output(15, False)
    GPIO.output(16, False)
    GPIO.output(18, False)

maneuvers = {
 'backward': backward,
 'forward': forward,
 'stop': stop,
 'counter': counter,
 'clockwise': clockwise,
}

if __name__ == "__main__":
    print "Start"
    broker="broker.hivemq.com"	
    client = mqtt.Client()
    client.connect(broker, 1883)
    client.subscribe("/control_cmd")
    client.on_message = on_message

    client.loop_forever()
