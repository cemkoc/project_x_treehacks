from flask import Flask, request, redirect
import twilio.twiml

app = Flask(__name__)

callers = {
	"+14152983952": "Jem Koch"
}

@app.route("/", methods=['GET', 'POST'])
def hello_monkey():
	# Get the caller's phone number from imcoming Twilio request
	from_number = request.values.get('From', None)
	body = request.values.get('Body', None)
	resp = twilio.twiml.Response()

	if from_number in callers:
		resp.message("Well hello there " + callers[from_number])

	else:
		resp.message("Hello Stranger")

	# with resp.gather(numDigits=1, action="/handle-key", method="POST") as g:
	# 	g.say("To speak to a real person, please press 1. Press any other key to start over.")

	resp.message("You sent me: " + body)
	return str(resp)
@app.route("/handle-key", methods=['GET', 'POST'])
def handle_key():
	""" Handle key when pressed by a caller."""

	#Get the digit pressed by the caller
	pressed_digit = request.values.get('Digits', None)
	if pressed_digit == "1":
		resp = twilio.twiml.Response()
		#Dial an actual number
		# resp.dial("+14152983952")
		resp.say("The call failed or hung up.")

		return str(resp)
	# caller pressed any other key
	else: 
		return redirect("/")


if __name__ == "__main__":
	app.run(debug=True)