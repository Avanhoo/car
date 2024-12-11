# SPDX-FileCopyrightText: 2024 DJDevon3
# SPDX-License-Identifier: MIT

from wifi import radio, Monitor
import ipaddress
from time import sleep
from adafruit_connection_manager import get_radio_socketpool
from adafruit_httpserver import Server, Request, Response, POST, GET
import board
import pwmio
import servo
import digitalio
from analogio import AnalogIn

center = 98 #Servo center angle
turnAngle = 12 # Degrees to turn on turn command

led = digitalio.DigitalInOut(board.LED) # LED
led.direction = digitalio.Direction.OUTPUT

pwm = pwmio.PWMOut(board.GP0, duty_cycle=0, frequency=50)
pwm2 = pwmio.PWMOut(board.GP1, duty_cycle=0, frequency=50)
pwm3 = pwmio.PWMOut(board.GP2, duty_cycle=2 ** 15, frequency=50)
my_servo = servo.Servo(pwm3)
my_servo.angle = center
sleep(.5)

radio.connect("YOUR_WIFI_SSID_HERE","YOUR_WIFI_PASSWORD_HERE")
pool = get_radio_socketpool(radio)
server = Server(pool, "/static", debug=True)


def webpage():
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta http-equiv="Content-type" content="text/html;charset=utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
    html{{font-family: monospace; background-color: white;
    display:inline-block; margin: 0px auto; text-align: center;}}
      h1{{color: black; padding: 2vh; font-size: 35px;}}
      p{{font-size: 1.5rem;}}

      .button{{font-family: monospace;top:0;left:0;
      background-color: black; border: none;
      border-radius: 4px; color: white; padding: 16px 40px;
      text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}}

      .flex-full {{
        display: flex;
        flex-direction: row;
        background-color: grey;
        justify-content: center;
      }}
      .flex-full > div {{
        width: 350px;
        height: 250px; 
        margin: 10px;
        margin-inline: 40px;
      }}

      .flex-left {{
        display: flex;
        flex-direction: row;
        background-color: lightgrey;
        justify-content: center;
      }}
      .flex-left > div {{
        width: 150px;
        height: 200px;
        margin: 10px;
      }}

      .flex-right {{
        display: flex;
        flex-direction: column;
        background-color: lightgray;
        justify-content: center;
      }}
      .flex-right > div {{
        width: 200px;
        height: 250px;
        margin: 5px;
      }}

      .leftButton {{
       width:150px;
       height:225px;
       z-index: 2;
       background: rgb(247, 247, 25); 
       }}
       .rightButton {{
       width:150px;
       height:225px;
       z-index: 2;
       background: lightskyblue; 
       }}
       .fwdButton {{
       width:250px;
       height:120px;
       z-index: 2;
       background: greenyellow; 
       }}
       .revButton {{
       width:250px;
       height:120px;
       z-index: 2;
       background: red; 
       }}


      p.dotted {{margin: auto; height: 50px;
      width: 75%; font-size: 25px; text-align: center;}}
    </style>
    </head>
    <body scroll="no">
    <title>Pico W RC Car</title>
    <h1>Pico W RC Car</h1>
    
    <p class="dotted" id="colorChange">IP: {radio.ipv4_address}</p>

    <div class="flex-full">
      <div class="flex-left">
        <div>
          <button class="leftButton" name="LEFT" ontouchstart="sendData('left', 'yellow', 'LEFT')" ontouchend="sendData('left', 'black', 'STRAIGHT')">LEFT</button></div>
        <div>
          <button class="rightButton" name="RIGHT" ontouchstart="sendData('right', 'blue', 'RIGHT')" ontouchend="sendData('right', 'black', 'STRAIGHT')">RIGHT</button></div>
      </div>
      
      <div class="flex-right">
        <div>
          <button class="fwdButton" name="FORWARD" ontouchstart="sendData('forward', 'lightgreen', 'FORWARD')" ontouchend="sendData('forward', 'black', 'STOP')">FORWARD</button></div>
        <div>
          <button class="revButton" name="BACKWARD" ontouchstart="sendData('backward', 'red', 'BACKWARD')" ontouchend="sendData('backward', 'black', 'STOP')">BACKWARD</button></div>
      </div>
    </div>
    
    <script>
      function sendData(id, color, action) {{
        const elem = document.getElementById("colorChange");
        elem.style.color = color;

        fetch('/', {{
                method: 'POST',
                body: action
            }})
      }}
      
      function mouseUp() {{
        document.getElementById("fwdButton").style.background = "red";
      }}
      </script>

    
    </body></html>

    """
    return html
print("Initiated")

#  route default static IP
@server.route("/")
def base(request: Request):  # pylint: disable=unused-argument
    #  serve the HTML f string
    #  with content type text/html
    return Response(request, f"{webpage()}", content_type='text/html')

#  if a button is pressed on the site
@server.route("/", POST)
def buttonpress(request: Request):#  get the raw text
    
    raw_text = request.raw_request.decode("utf8") # Decode the data into text
    print(f"\nRAW TEXT:\n{raw_text}\nEND")
    if "FORWARD" in raw_text:
      print("Forward")
      pwm.duty_cycle = (0)
      pwm2.duty_cycle = (2 ** 16)-1 # Motor forward
    if "BACKWARD" in raw_text:
      print("Backward")
      pwm.duty_cycle = (2 ** 16)-1 # Motor backward
      pwm2.duty_cycle = (0)
    if "STOP" in raw_text:
      print("Stop")
      pwm.duty_cycle = (0) # Motor coast
      pwm2.duty_cycle = (0)
    if "LEFT" in raw_text: # Turn left
      print("Left")
      my_servo.angle = center - turnAngle
    if "RIGHT" in raw_text: # Turn Right
      print("Right")
      my_servo.angle = center + turnAngle
    if "STRAIGHT" in raw_text: # Go straight
      print("Straight")
      my_servo.angle = center
    

    return Response(request, f"{webpage()}", content_type='text/html')#  reload site



@server.route("/", GET)
def liveparty(request: Request):
    raw_text = request.raw_request.decode("utf8")
    print("LIVE")
    return None

print("serving:")
server.start(str(radio.ipv4_address)) # This will print out the url of the web server

while True: # We must constantly poll the server to see if there are any responses
    server.poll()