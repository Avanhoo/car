# SPDX-FileCopyrightText: 2024 DJDevon3
# SPDX-License-Identifier: MIT

from wifi import radio, Monitor
import ipaddress
from adafruit_connection_manager import get_radio_socketpool
from adafruit_httpserver import Server, Request, Response, POST, GET
import board
import pwmio
import digitalio
from analogio import AnalogIn


led = digitalio.DigitalInOut(board.LED) # LED
led.direction = digitalio.Direction.OUTPUT

pwm = pwmio.PWMOut(board.GP0, duty_cycle=2 ** 15, frequency=50)
pwm2 = pwmio.PWMOut(board.GP1, duty_cycle=2 ** 15, frequency=50)

radio.connect("AG5","studytime")
pool = get_radio_socketpool(radio)
server = Server(pool, "/static", debug=True)


font_family = "monospace" # Credit to Liz Clark, Adafruit
data1 = "lightly salted gravel"
def webpage():
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta http-equiv="Content-type" content="text/html;charset=utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
    html{{font-family: {font_family}; background-color: white;
    display:inline-block; margin: 0px auto; text-align: center;}}
      h1{{color: black; padding: 2vh; font-size: 35px;}}
      p{{font-size: 1.5rem;}}

      .button{{font-family: {font_family};top:0;left:0;
      background-color: black; border: none;
      border-radius: 4px; color: white; padding: 16px 40px;
      text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}}

      .leftButton {{
       top:25%;
       left:5%;
       width:150px;
       height:225px;
       position: absolute;
       z-index: 2;
       background: lightblue; 
       }}
       .rightButton {{
       top:25%;
       left:25%;
       width:150px;
       height:225px;
       position: absolute;
       z-index: 2;
       background: lightblue; 
       }}
       .fwdButton {{
       top:25%;
       right:15%;
       width:250px;
       height:100px;
       position: absolute;
       z-index: 2;
       background: greenyellow; 
       }}
       .revButton {{
       top:42%;
       right:15%;
       width:250px;
       height:100px;
       position: absolute;
       z-index: 2;
       background: red; 
       }}


      p.dotted {{margin: auto; height: 50px;
      width: 75%; font-size: 25px; text-align: center;}}
    </style>
    </head>
    <body scroll="no" style="overflow": hidden;position: fixed;>
    <title>Pico W RC Car</title>
    <h1>Pico W RC Car</h1>
    
    <p class="dotted">IP: {radio.ipv4_address}</p>

        
    <form accept-charset="utf-8" method="POST">
    <button class="leftButton" name="LEFT" value="ON" type="submit">LEFT</button></a></p></form>
    
    <p><form accept-charset="utf-8" method="POST">
    <button class="rightButton" name="RIGHT" value="OFF" type="submit">RIGHT</button></a></p></form>
    
    <p><form accept-charset="utf-8" method="POST">
    <button class="fwdButton" name="FORWARD" type="submit">FORWARD</button></a></p></form>

    <p><form accept-charset="utf-8" method="POST">
      <button class="revButton" name="BACKWARD" type="submit">BACKWARD</button></a></p></form>
    
    </body></html>

    """
    return html
print("Initiated")

#  route default static IP
@server.route("/")
def base(request: Request):  # pylint: disable=unused-argument
    #  serve the HTML f string
    #  with content type text/html
    return Response(request, f"{{webpage()}}", content_type='text/html')

#  if a button is pressed on the site
@server.route("/", POST)
def buttonpress(request: Request):
    #  get the raw text
    raw_text = request.raw_request.decode("utf8")
    print(f"\nRAW TEXT:\n{{raw_text}}\nEND")
    #  if the led on button was pressed
    if "ON" in raw_text:
        #  turn on the onboard LED
        pwm2.duty_cycle = (2 ** 16)-1
        led.value = True
    #  if the led off button was pressed
    if "OFF" in raw_text:
        #  turn the onboard LED off
        pwm2.duty_cycle = (2 ** 15)
        led.value = False
    #  if the party button was pressed
    if "party" in raw_text:
        print("PARTY")
    #  reload site
    return Response(request, f"{{webpage()}}", content_type='text/html')

@server.route("/", GET)
def liveparty(request: Request):
    raw_text = request.raw_request.decode("utf8")
    print("LIVE")
    return None

print("serving:")

server.start(str(radio.ipv4_address))
while True:
    server.poll()