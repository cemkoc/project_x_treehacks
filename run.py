from flask import Flask, request, redirect
from twilio.rest import TwilioRestClient
import twilio.twiml
import urllib2
import json
import re
app = Flask(__name__)

@app.route('/abcd')
def caller():
	response = 'hi'
	return str(response) 

@app.route("/", methods=['GET', 'POST'])
def startApplicationMonkey():
    from_number = request.values.get('From', None)
    cem = "+14152983952"
    can = "+14158025332"
    received_message = request.values.get('Body', None)

    auth_token = "267478d679e713a9c97bccf6cadb4b0b"
    account_sid = "ACdb5fb6ce8be1e4b949cee8255148af50"
    client = TwilioRestClient(account_sid, auth_token)

    if not received_message:
    	#client.messages.create(to=alan, from_="+17324791835", body='nothing received_message')
        #return 'nothing received'
        received_message = 'Go from berkeley to stanford driving'
    else:
        if type(received_message) != str:
            received_message = str(received_message)
    
    returnedString = route_request(received_message)
    client.messages.create(to=can, from_="+14804050163", body=returnedString)
    return returnedString
    
def route_request(message):

	keyWord = map(lambda x: x.upper(), message.split())[0]
	handle = {
        "GO": textDirection,
        "NEWS": getNews,
        "WEATHER": getWeather,
        "MAP": getMap,
        "STATUS": sendStatusUpdate }

	return handle[keyWord](message)

def textDirection(body):
	if body == None:
		body = 'Go from dwinelle to 1555 oxford avenue transit'
	indexFrom = body.find(' from ')
	indexTo = body.find(' to ')
	modeType = body.split()[-1].strip()
	indexMode = body.find(modeType)
	startAddr = body[indexFrom+6:indexTo].strip()
	endAddr = body[indexTo + 4:indexMode].strip()
	return getDirection(startAddr, endAddr, modeType)

def getDirection(origin, destination, mode='walking'):

    if origin:
    	origin = origin.strip().replace(' ', '+')

    if destination:
    	destination = destination.strip().replace(' ', '+')

	response = urllib2.urlopen('https://maps.googleapis.com/maps/api/directions/json?origin=' + origin + '&destination='+destination+'&mode=' + mode + '&key=AIzaSyAMShh7VdTHP_NDUPRW-dI0kCyFa84d9ko')
	html = response.read()
	data = json.loads(html)
	print 'HELLO LOG'
	directionList = []
	start = "Starting from " + data['routes'][0]['legs'][0]['start_address']
	end = "Ending at " + data['routes'][0]['legs'][0]['end_address']
	directionList.append(start)
	directionList.append(end)

	for x in data['routes'][0]['legs'][0]['steps']:
		direction= x['html_instructions']
		distance = x['distance']['text']
		directionList.append(re.sub(r'<.*?>', '', direction) + ' (' + distance +') ')

	count = 1
	directionString = directionList[0] + ' and ' + directionList[1] + ' ' + mode + '\n '
	for x in directionList[2:]:
		directionString = directionString + str(count) + ': ' + x + '\n'
		count = count + 1
	return directionString

def getNews(message):
    return None

def getWeather(message):
    return None

def getMap(message):
    return None

def sendStatusUpdate(message):
    return None	

if __name__ == "__main__":
    app.run(debug=True)

