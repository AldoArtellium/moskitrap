# moskitrap
Another way to fight against mosquitoes

This is a project for my first year of high school

The principle is simple, we have mosquitoes that lay eggs in a standing water.
The standing water get evacuate under the ground and get replaced with new water. This way we dont touch current wildlife.
For this project to be effective it is needed to put it were there is no water nearby.

We are using mainly python for the main process and some html for the layout of the page with javascript to socket the server.
For the web gui we have used python modules flask and flask-socketio to host the web server. To use the humidity sensor we were needed to use a special python library (Si7021). In order to comunicate with all the component we have use native raspberry gpio (RPi.GPIO)


COMPONENT LIST:
  - Raspberry pi 3 (x1) -- 
  - Solenoid (x2) -- 450mA - 12V - 5.4W
  - Relay (x2) -- 
  - Webcam (x1) -- 5V - 100mA - 0.5W
  - Liquid Level Switch (x3) -- 5.5V - 100mA - 0.55W
  - Humidity Sensor (x1) -- 200µA - 5,5V - 0.0011W
  
You can make it as a nomad machine with solar panels and a battery but we are limited in the time so it's on your own
