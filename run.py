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
    counter = session.get('counter', 0)
    counter += 1
    session['counter'] = counter
    from_number = request.values.get('From', None)
    received_message = request.values.get('Body', None)
    if from_number in callers:
        caller = callers[from_number]
    else:
        caller = "Monkey"
 
    resp = twilio.twiml.Response()
    # Greet the caller by name
    # resp.say("Hello " + caller)
    
    
    counter = session.get('counter', 0)
    counter += 1
    session['counter'] = counter
    # if from_number in callers:
    # Play an mp3
    # resp.play("http://demo.twilio.com/hellomonkey/monkey.mp3")
 
    # Say a command, and listen for the caller to press a key. When they press
    # a key, redirect them to /handle-key.
    # resp.message("Original Message: \n" + str(to_respond) + "\ncounter: " + str(counter))
    if received_message == None:
        # app.logger.warning('received message : ')
        received_message2 = 'Stanford Berkeley'
    else:
        received_message2 = str(received_message)
    # print received_message

    # resp.message("hiiiii")
    # To = []
    # From = []
    # Mode = []
    # i1 = received_message.split().index('To')
    # i2 = received_message.split().index('From')
    # i3 = received_message.split().index('Mode')
    # if len(received_message.split()) < 6 :
    #     return str(resp)
    # To = received_message[i1+1:i2]
    # From = received_message[i2+1: i3]
    # Mode = received_message[i3+1:]
    # To = received_message2[1:4]
    # From = received_message2[4:8]
    # Mode = received_message2[8:]
    # arg1 = ''
    # arg2 = ''
    # arg3 = ''

    # for el in To:
    #     arg1 = arg1 + el
    # for el in From:
    #     arg2 = arg2 + el
    # for el in Mode:
    #     arg3 = arg3 + el
    # resp.message(())       
    directions = readUrl(received_message2)
    #directions is a list
    to_respond = ''
    for el in directions:
        to_respond = to_respond + '\n' + el
    resp.message(to_respond)

    with resp.gather(numDigits=1, action="/handle-key", method="POST") as g:
        g.say("To speak to a real monkey, press 1. Press any other key to start over.")
 
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

def readUrl(s, mode='walking'):
    # if s == 'None':
    #     s = "Stanford Berkeley"

    origin = s.split()[0]
    destination = s.split()[1]
    response = urllib2.urlopen('https://maps.googleapis.com/maps/api/directions/json?origin=' + origin + '&destination='+destination+'&mode=' + mode + '&key=AIzaSyAMShh7VdTHP_NDUPRW-dI0kCyFa84d9ko')
    html = response.read()
    data = json.loads(html)
    directionList = []
    print data
    for x in data['routes'][0]['legs'][0]['steps']:
        direction= x['html_instructions']
        directionList.append(re.sub(r'<.*?>', '', direction))
    
    return directionList

if __name__ == "__main__":
    app.run(debug=True)

