import urllib2
import json
import re
from pprint import pprint

def readUrl(origin, destination, mode='walking'):
	response = urllib2.urlopen('https://maps.googleapis.com/maps/api/directions/json?origin=' + origin + '&destination='+destination+'&mode=' + mode + '&key=AIzaSyAMShh7VdTHP_NDUPRW-dI0kCyFa84d9ko')
	html = response.read()
	data = json.loads(html)
	directionList = []
	for x in data['routes'][0]['legs'][0]['steps']:
		direction= x['html_instructions']
		directionList.append(re.sub(r'<.*?>', '', direction))
	
	return directionList
