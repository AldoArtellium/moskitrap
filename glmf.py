#!/usr/bin/env python
# -*- coding:utf-8 -*-

import thread
from time import sleep, time

from mjpegtools import MjpegParser

import Si7021
import pigpio

import RPi.GPIO as GPIO

from flask import Flask, redirect, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, disconnect


###################################################################################
#                                 Configure GPIO                                  #
###################################################################################

VALVE_IN = 17
VALVE_OUT = 27

WATER_HIGH = 23
WATER_MEDIUM = 24
WATER_LOW = 25

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)


###################################################################################
#                            Humidity Sensor Si7021                               #
###################################################################################

pi = pigpio.pi()

if not pi.connected:
    exit(0)

s = Si7021.sensor(pi)
s.set_resolution(0)

print("[Humidity Sensor] res=" + str(s.get_resolution()))
print("[Humidity Sensor] revision={:x} id1={:08x} id2={:08x}".format(s.firmware_revision(),s.electronic_id_1(), s.electronic_id_2()))

# for i in range(1,20):
#     print("[Humidity Sensor] {:.2f} {:.2f}".format(s.temperature(), s.humidity()))

#     sleep(1)


###################################################################################
#                                    Solenoids                                    #
###################################################################################

GPIO.setup(VALVE_IN, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(VALVE_OUT, GPIO.OUT, initial=GPIO.LOW)


###################################################################################
#                                   Water Sensor                                  #
###################################################################################

GPIO.setup(WATER_HIGH, GPIO.IN)
GPIO.setup(WATER_MEDIUM, GPIO.IN)
GPIO.setup(WATER_LOW, GPIO.IN)


###################################################################################
#                                      Threads                                      #
###################################################################################

def bg(): # Control humidity and temperature
	while True:
		x = round(s.temperature(), 2)
		y = round(s.humidity(), 2) 
		socketio.emit('message', {'temp' : x, 'h2o' : y})
		sleep(1)

def  logic(): # Control solenoids
	State=0
	kill = time() + 100
	while True:
		if(time() >= kill and State == 0):
			State = 1
		
		socketio.emit('logic', {'state' : State, 'kill' : round(kill - time())})
		
		if(State == 0):
			if(not GPIO.input(WATER_MEDIUM)):
				GPIO.output(VALVE_IN, GPIO.LOW)
				GPIO.output(VALVE_OUT, GPIO.LOW)
			elif(not GPIO.input(WATER_HIGH)):
				GPIO.output(VALVE_IN, GPIO.LOW)
				GPIO.output(VALVE_OUT, GPIO.HIGH)
			elif(not GPIO.input(WATER_LOW)):
				GPIO.output(VALVE_IN, GPIO.HIGH)
				GPIO.output(VALVE_OUT, GPIO.LOW)
			else:
				GPIO.output(VALVE_IN, GPIO.HIGH)
				GPIO.output(VALVE_OUT, GPIO.LOW)
		elif(State == 1):
			GPIO.output(VALVE_IN, GPIO.LOW)
			GPIO.output(VALVE_OUT, GPIO.HIGH)
			
			while GPIO.input(WATER_LOW):
				sleep(5)
			
			kill= time() + 100
			State = 0
		sleep(1)
		
###################################################################################
#                                       Flask Server Start                                      #
###################################################################################

app = Flask(__name__)
socketio = SocketIO(app)

app.debug = True
thread.start_new_thread(bg, ())
thread.start_new_thread(logic, ())

@app.route('/')
def home():
	return render_template('home.html', titre='Page d\'accueil')
	
@app.route('/direct-stream')
def stream_direct():
  cam = MjpegParser(url='http://youripadress/videostream.cgi?user=admin&pwd=password&resolution=8&rate=0')
  cam.quality = 20
  return cam.serve().as_flask_mjpeg()

@socketio.on('safety')
def safety(data):
	print(data['data'])
	
@socketio.on('kaka')
def kaka(data):
	print(data['data'])
	if data['data'] in 'ntm':
		State= 1
		print(str(State))

@socketio.on('connect')
def test_connect():
	emit('osef', {'data' : 'Connected', 'count' : 0})
	
@socketio.on('disconnect')
def test_disconnect():
	print('[Flask] Client Disconnected')


###################################################################################
#                                       Post                                      #
###################################################################################

if __name__ == '__main__': # start app
	socketio.run(app)

s.cancel()
pi.stop()
