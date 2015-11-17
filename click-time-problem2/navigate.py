import requests
import json

def NavigateMe(origin):
	destination = 'SanFrancisco'
	key = 'AIzaSyCl_7phc2HQOSimmScmS09NW_A9dlQklqw'
	url='https://maps.googleapis.com/maps/api/directions/json?origin={0}&destination={1}&key={2}'.format(origin, destination, key)
	r=requests.get(url)
	x=json.loads(r.text)
	legs=x['routes'][0]['legs']
	steps=legs[0]['steps']
	
#	instructions=steps[0]['html_instructions']
	print steps[0].keys()
	#print len(steps),steps[0].keys()
	#print len(legs),legs[0].keys()
	all_instructions = [x['html_instructions'] for x in steps]
	print '\n'.join(all_instructions)

#print "enter your location"
#location=raw_input()
#location=location.replace(" ","")
location = 'SanJose'
NavigateMe(location)
