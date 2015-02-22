from flask import Flask, request, redirect
from twilio.rest import TwilioRestClient
import twilio.twiml
import urllib2
import json
import re
app = Flask(__name__)

import yelpSearch


@app.route("/", methods=['GET', 'POST'])
def startApplicationMonkey():
    from_number = request.values.get('From', None)
    #alan = "+17329252682"
    print from_number
    received_message = request.values.get('Body', None)

    auth_token = "267478d679e713a9c97bccf6cadb4b0b"
    account_sid = "ACdb5fb6ce8be1e4b949cee8255148af50"
    client = TwilioRestClient(account_sid, auth_token)
    
    print "sadasdasdasd!!!!! ", received_message

    if not from_number:
    	return 'not handled. no phone number'
    if not received_message:
    	#client.messages.create(to=alan, from_="+17324791835", body='nothing received_message')
        #return 'nothing received'
        received_message = 'unhandled'
        client.messages.create(to=from_number, from_="+14804050163", body=received_message)
        return received_message

    else:
        if type(received_message) != str:
            received_message = str(received_message)
    # print "asdasdasdasdasdas!!!!!!!!" , received_message
    route_request(received_message, client, from_number)
    
    # return 'handled'

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
        "STATUS": sendStatusUpdate,
        "YELP": yelpIt }

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
		client.messages.create(to=person, from_="+14804050163", body=sorry)
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
		client.messages.create(to=person, from_="+14804050163", body=sorry)
	else:
		client.messages.create(to=person, from_="+14804050163", body=directionString)

def getNews(message, client, person):
    return None

def getWeather(message, client, person):
    return None
def yelpIt(message, client, person):
    if message == None:
        message = 'Yelp for dinner near San Francisco, CA'
    indexFor = message.find(' for ')
    indexNear = message.find(' near ')
    term = message[indexFor+5:indexNear].strip()
    location = message[indexNear+6:].strip()
    getYelpSearch(term, location, client, person)

def getYelpSearch(term, location, client, person):
    data = yelpSearch.query_api(term, location)
    name = data['businesses'][0]['name']
    rating = data['businesses'][0]['rating']
    phone = data['businesses'][0]['display_phone']
    image_url = data['businesses'][0]['image_url']
    is_Closed = data['businesses'][0]['is_closed']
    address = ''
    for x in data['businesses'][0]['location']['display_address']:
        address = address + x  

    to_respond = 'Yelp Search found: \n' + name + '\n' + 'with rating: ' + rating + '\n' + 'phone number: ' + phone + '\n' + 'is it Closed? ' + is_Closed
    to_respond = to_respond + '\n address is: ' + address
    client.messages.create(to=person, from_='+14804050163', body=to_respond)




def getMap(message, client, person):
	#map Berkeley CA. Sends MMS
    if not message:
    	client.messages.create(to=person, from_="+14804050163", body='Sorry, could not process your request')
    else:
    	message = message.strip()
    	message = message[4:]
    	address = message.replace(' ', '+')
    	mapUrl = "https://maps.googleapis.com/maps/api/staticmap?center=" + address + "&zoom=16&size=600x300&maptype=roadmap"
    	media_url=[mapUrl]
    	client.messages.create(to=person, from_="+14804050163", body=message, media_url=[mapUrl])


def sendStatusUpdate(message, client, person):
    return None	

if __name__ == "__main__":
    app.run(debug=True)

