from flask import Flask, request, redirect, session
import twilio.twiml

import urllib2
import json
import re
from pprint import pprint


callers = {
    "+14158675309": "Curious George",
    "+14158675310": "Boots",
    "+14158675311": "Virgil",
    "+14158025332": "Can Koc"
}

SECRET_KEY = "BEINSANE"
app = Flask(__name__)
app.config.from_object(__name__)
 
@app.route("/", methods=['GET', 'POST'])
def hello_monkey():
    from_number = request.values.get('From', None)
    received_message = request.values.get('Body', None)
 
    resp = twilio.twiml.Response()

    directions = textDirection(received_message)

    to_respond = ''
    
    for el in directions:
        to_respond = to_respond + '\n' + el
    resp.message(to_respond)
 
    return str(resp)
 
@app.route("/handle-key", methods=['GET', 'POST'])
def handle_key():
    """Handle key press from a user."""
 
    # Get the digit pressed by the user
    digit_pressed = request.values.get('Digits', None)
    if digit_pressed == "1":
        resp = twilio.twiml.Response()
        # Dial (310) 555-1212 - connect that number to the incoming caller.
        resp.message("Hello Monkey")
        # If the dial fails:
        resp.say("The call failed, or the remote party hung up. Goodbye.")
 
        return str(resp)
 
    # If the caller pressed anything but 1, redirect them to the homepage.
    else:
        return redirect("/")

 
# @app.route("/", methods=['GET', 'POST'])
# def hello_monkey():
#     """Respond to incoming calls with a simple text message."""
 
#     resp = twilio.twiml.Response()
#     resp.message("Hello, Mobile Monkey")
#     return str(resp)

def getDirection(origin, destination, mode='walking'):
    if origin:
        origin = origin.strip().replace(' ', '+')
    if destination:
        destination = destination.strip().replace(' ', '+')
    response = urllib2.urlopen('https://maps.googleapis.com/maps/api/directions/json?origin=' + origin + '&destination='+ destination +'&mode=' + mode + '&key=AIzaSyAMShh7VdTHP_NDUPRW-dI0kCyFa84d9ko')
    html = response.read()
    data = json.loads(html)
    directionList = []
    # print data
    for x in data['routes'][0]['legs'][0]['steps']:
        direction= x['html_instructions']
        directionList.append(re.sub(r'<.*?>', '', direction))
    
    return directionList

def textDirection(body):
    if body == None:
        body = 'Go from stanford to palo alto '
    indexFrom = body.find(' from ')
    indexTo = body.find(' to ')
    startAddr = body[indexFrom+6:indexTo].strip()
    endAddr = body[indexTo + 4:].strip()
    return getDirection(startAddr, endAddr)

if __name__ == "__main__":
    app.run(debug=True)

