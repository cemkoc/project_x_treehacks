from flask import Flask, request, redirect
from twilio.rest import TwilioRestClient
import twilio.twiml
import urllib2
import json
import re
app = Flask(__name__)
 

@app.route("/", methods=['GET', 'POST'])
def startApplicationMonkey():
    from_number = request.values.get('From', None)
    #alan = "+17329252682"
    print from_number
    received_message = request.values.get('Body', None)

    auth_token = "10736f5b33ef8e1855961379b2cb67b3"
    account_sid = "ACd9ea80cb5247395f43f6b1eea438b8dc"
    client = TwilioRestClient(account_sid, auth_token)

    if not from_number:
    	return 'not handled. no phone number'
    if not received_message:
    	#client.messages.create(to=alan, from_="+17324791835", body='nothing received_message')
        #return 'nothing received'
        received_message = 'unhandled'
        client.messages.create(to=from_number, from_="+17324791835", body=received_message)
        return received_message

    else:
        if type(received_message) != str:
            received_message = str(received_message)
    
    route_request(received_message, client, from_number)
    
    return 'handled'

# def getMap():
#     if body:
#     	address = body.strip().replace(' ', '+')
#     else:
#     	address = '269+Candlewyck+Court' #nonetype handler.
#     mapUrl = "https://maps.googleapis.com/maps/api/staticmap?center=" + address + "&zoom=16&size=600x300&maptype=roadmap"
    
def route_request(message, client, person):

	keyWord = map(lambda x: x.upper(), message.split())[0]
	handle = {
        "GO": textDirection,
        "NEWS": getNews,
        "WEATHER": getWeather,
        "MAP": getMap,
        "STATUS": sendStatusUpdate }

	handle[keyWord](message, client, person)

def textDirection(body, client, person):
	if body == None:
		body = 'Go from dwinelle to 1555 oxford avenue transit'
	indexFrom = body.find(' from ')
	indexTo = body.find(' to ')
	modeType = body.split()[-1].strip()
	indexMode = body.find(modeType)
	startAddr = body[indexFrom+6:indexTo].strip()
	endAddr = body[indexTo + 4:indexMode].strip()
	getDirection(startAddr, endAddr, modeType, client, person)

def getDirection(origin, destination, mode, client, person):

    if origin:
    	origin = origin.strip().replace(' ', '+')

    if destination:
    	destination = destination.strip().replace(' ', '+')

	response = urllib2.urlopen('https://maps.googleapis.com/maps/api/directions/json?origin=' + origin + '&destination='+destination+'&mode=' + mode + '&key=AIzaSyAMShh7VdTHP_NDUPRW-dI0kCyFa84d9ko')
	html = response.read()
	data = json.loads(html)
	if (data['status']=='ZERO_RESULTS'):
		sorry = 'Sorry, no directions were found. Could you please specify City in your address?'
		client.messages.create(to=person, from_="+17324791835", body=sorry)
		return
	
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
	if len(directionString) > 1500:
		sorry = 'Sorry, no directions were found. Could you please specify City in your address?'
		client.messages.create(to=person, from_="+17324791835", body=sorry)
	else:
		client.messages.create(to=person, from_="+17324791835", body=directionString)

def getNews(message, client, person):
    return None

def getWeather(message, client, person):
	commaIndex = message.find(',')
	if commaIndex == -1: #not found
		pleaseComma = 'Please put comma between town and city like this: Berkeley, California'
		client.messages.create(to=person, from_="+17324791835", body=pleaseComma)
		return
	city = message[8:commaIndex].strip().replace(' ', '+')
	state = message[commaIndex+1:].strip().replace(' ', '+')
	#print 'url', 'http://api.openweathermap.org/data/2.5/weather?q=' + city+ ',' + state + '&units=imperial'
	response = urllib2.urlopen('http://api.openweathermap.org/data/2.5/weather?q=' + city+ ',' + state + '&units=imperial')
	html = response.read()
	data = json.loads(html)
	windspeed = str(data['wind']['speed']) + ' mph'
	weather = data['weather'][0]['main']
	description = data['weather'][0]['description']
	# maxTemp = str(data['main']['temp_max']) + ' Fahrenheit'
	# minTemp = str(data['main']['temp_min']) + ' Fahrenheit'
	current = str(data['main']['temp']) + ' Fahrenheit'
	finalWeather = "\nToday's Weather: \n" + weather + ': ' + description + '\nCurrent: '
	finalWeather += current + '\nWindspeed: ' + windspeed
	client.messages.create(to=person, from_="+17324791835", body=finalWeather)

def getMap(message, client, person):
	#map Berkeley CA. Sends MMS
    if not message:
    	client.messages.create(to=person, from_="+17324791835", body='Sorry, could not process your request')
    else:
    	message = message.strip()
    	message = message[4:]
    	address = message.replace(' ', '+')
    	mapUrl = "https://maps.googleapis.com/maps/api/staticmap?center=" + address + "&zoom=16&size=600x300&maptype=roadmap"
    	media_url=[mapUrl]
    	client.messages.create(to=person, from_="+17324791835", body=message, media_url=[mapUrl])


def sendStatusUpdate(message, client, person):
    return None	

if __name__ == "__main__":
    app.run(debug=True)

