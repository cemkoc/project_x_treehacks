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
    # print "asdasdasdasdasdas!!!!!!!!" , received_message
    route_request(received_message, client, from_number)
    
    # return 'handled'    
def route_request(message, client, person):

	keyWord = map(lambda x: x.upper(), message.split())[0]
	handle = {
        "GO": textDirection,
        "NEWS": getNews,
        "WEATHER": getWeather,
        "MAP": getMap,
        "TRANSLATE": translateText,
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

	response = urllib2.urlopen('https://maps.googleapis.com/maps/api/directions/json?origin=' + origin + '&destination='+destination+'&mode=' + mode.lower() + '&key=AIzaSyAMShh7VdTHP_NDUPRW-dI0kCyFa84d9ko')
	html = response.read()
	data = json.loads(html)
	if (len(data['routes']) == 0):
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
    response = urllib2.urlopen('http://api.openweathermap.org/data/2.5/weather?q=' + city+ ',' + state + '&units=imperial')
    html = response.read()
    data = json.loads(html)
    windspeed = str(data['wind']['speed']) + ' mph'
    weather = data['weather'][0]['main']
    description = data['weather'][0]['description']
    current = str(data['main']['temp']) + ' Fahrenheit'
    finalWeather = "\nToday's Weather: \n" + weather + ': ' + description + '\nCurrent: '
    finalWeather += current + '\nWindspeed: ' + windspeed
    client.messages.create(to=person, from_="+17324791835", body=finalWeather)

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
    if is_Closed == True:
        is_Closed = 'Yes'
    elif is_Closed == False:
        is_Closed = 'No'
    address = ''
    for x in data['businesses'][0]['location']['display_address']:
        address = address + x  


    to_respond = 'Yelp search found: ' + '\n' + str(name) + '\n' + ' With rating: ' + str(rating) + '\n' + ' Phone number: ' + str(phone) + '\n' +' Is it Closed? ' + str(is_Closed)
    to_respond = to_respond + '\n' + 'Address is: ' + str(address)
    client.messages.create(to=person, from_='+17324791835', body=to_respond)



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


def translateText(message, client, person):

    message_as_list = message.split()
	    
    if len(message_as_list) < 5 or not message:
    	translate_error = "Please use this format: \n" + "Translate, <text>, from, <source_language>, to, <target_language>"
    	client.messages.create(to=person, from_="+19253266546", body=email_error)
    
    text = ' '.join(message_as_list[1:]).split(' FROM ')[0]
    src_lang = ' '.join(message_as_list[1:]).split(' FROM ')[1].split(' TO ')[0]
    target_lang = ' '.join(message_as_list[1:]).split(' FROM ')[1].split(' TO ')[1]
    src_mapper = src_lang[0].upper() + src_lang[1:]
    target_mapper = target_lang[0].upper() + target_lang[1:]

    language_mapper = {
    	'Afrikaans':'af',
		'Albanian':'sq',
		'Arabic':'ar',
		'Azerbaijani':'az',
		'Basque':'eu',
		'Bengali': 'bn',
		'Belarusian':'be',
		'Bulgarian':'bg',
		'Catalan':'ca',
		'Chinese simplified':'zh-CN',
		'Chinese traditional':'zh-TW',
		'Croatian':'hr',
		'Czech':'cs',
		'Danish':'da',
		'Dutch':'nl',
		'English':'en',
		'Esperanto':'eo',
		'Estonian':'et',
		'Filipino':'tl',
		'Finnish':'fi',
		'French':'fr',
		'Galician':'gl',
		'Georgian':'ka',
		'German':'de',
		'Greek':'el',
		'Gujarati':'gu',
		'Haitian Creole':'ht',
		'Hebrew':'iw',
		'Hindi':'hi',
		'Hungarian':'hu',
		'Icelandic':'is',
		'Indonesian':'id',
		'Irish':'ga',
		'Italian':'it',
		'Japanese':'ja',
		'Kannada':'kn',
		'Korean':'ko',
		'Latin':'la',
		'Latvian':'lv',
		'Lithuanian':'lt',
		'Macedonian':'mk',
		'Malay':'ms',
		'Maltese':'mt',
		'Norwegian':'no',
		'Persian':'fa',
		'Polish':'pl',
		'Portuguese':'pt',
		'Romanian':'ro',
		'Russian':'ru',
		'Serbian':'sr',
		'Slovak':'sk',
		'Slovenian':'sl',
		'Spanish':'es',
		'Swahili':'sw',
		'Swedish':'sv',
		'Tamil':'ta',
		'Telugu':'te',
		'Thai':'th',
		'Turkish':'tr',
		'Ukrainian':'uk',
		'Urdu':'ur',
		'Vietnamese':'vi',
		'Welsh':'cy',
		'Yiddish':'yi'
    }
    text = '%20'.join(text.split())
    response = urllib2.urlopen("https://www.googleapis.com/language/translate/v2?key=AIzaSyAxyoJ2r8Ife2a2cs69wL8hku_Iog9c0Zc&source="+
    	language_mapper[src_mapper]+"&target="+language_mapper[target_lang]+"&q="+text)
    html = response.read()
    data = json.loads(html)
    if html.find('error') != -1:
    	client.messages.create(to=person, from_="+17324791835", body="client id expired")
    	return
    else:
	    translatedText = data['data']['translations'][0]['translatedText']
	    client.messages.create(to=person, from_="+17324791835", body=translatedText)


if __name__ == "__main__":
    app.run(debug=True)

