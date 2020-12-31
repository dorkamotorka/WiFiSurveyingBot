from flask import Flask
from flask import render_template, request
import RPi.GPIO as GPIO
import time

app = Flask(__name__)

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
pwm_r.start(25)
pwm_l.start(25)
print "Values reseted"

a=1
@app.route("/")
def index():
    return render_template('robot.html')

@app.route('/left_side')
def left_side():
    data1="LEFT"
    GPIO.output(15, True)
    GPIO.output(18, True)
    return 'true'

@app.route('/right_side')
def right_side():
   data1="RIGHT"
   GPIO.output(13, True)
   GPIO.output(16, True)
   return 'true'

@app.route('/up_side')
def up_side():
   data1="FORWARD"
   GPIO.output(15, True)
   GPIO.output(16, True)
   return 'true'

@app.route('/down_side')
def down_side():
   data1="BACK"
   GPIO.output(13, True)
   GPIO.output(18, True)
   return 'true'

@app.route('/stop')
def stop():
   data1="STOP"
   GPIO.output(13, 0)
   GPIO.output(15, 0)
   GPIO.output(16, 0)
   GPIO.output(18, 0)
   return  'true'

if __name__ == "__main__":
 print "Start"
 app.run(host='192.168.50.216',port=5010)
