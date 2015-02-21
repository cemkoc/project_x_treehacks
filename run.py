from flask import Flask, request, redirect, session
import twilio.twiml
 


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
    to_respond = request.values.get('Body', None)
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
    resp.message(str(to_respond) + " counter: " + str(counter))
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
 
if __name__ == "__main__":
    app.run(debug=True)

