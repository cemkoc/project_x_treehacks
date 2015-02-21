from flask import Flask
import twilio.twiml

app = Flask(__name__)

callers = {
	"+14152983952": "Jem Koch"
}

@app.route("/", methods=['GET', 'POST'])
def hello_monkey():
	# Get the caller's phone number from imcoming Twilio request
	from_number = request.values.get('From', None)
	resp = twilio.twiml.Response()

	if from_number in callers:
		resp.say("Well hello there " + callers[from_number])
	else:
		resp.say("Hello Stranger")

	return str(resp)


if __name__ == "__main__":
	app.run(debug=True)