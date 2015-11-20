import requests
import json
import datetime
import sys
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()
from tabulate import tabulate
from HTMLParser import HTMLParser

YES_OPTIONS = ['yes', 'YES', 'Yes', 'y', 'Y', 'yo']
NO_OPTIONS = ['no', 'NO', 'No', 'n', 'N']
TRANSIT_MODES = {'b': 'bicycling', 'w': 'walking', 't': 'transit'}

directions_key = 'AIzaSyCl_7phc2HQOSimmScmS09NW_A9dlQklqw'
#places_key = 'AIzaSyAAVTbGtg6q-4ioZF4gqM8pqXaLPxBILsM'
places_key = 'AIzaSyDF1YIjBPwXLcrxCIKGa9otfMYf6B0B3z4'

CLICKTIME_ADDRESS = '282 2nd St, San Francisco, CA 94105'


# Attribution for MLStripper class
# http://stackoverflow.com/questions/753052/strip-html-from-strings-in-python

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ' '.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


class places :
	def __init__(self,name,place_id,rating,price_level,time_taken):
		self.name=name
		self.place_id=place_id
		self.rating=rating
		self.price_level=price_level
		self.time_taken=time_taken

	def __repr__(self):
		return self.name
		
	def placeid_to_address(self):
		return AddressLookup(self.place_id)
		
	def summary(self):
		price_level = self.price_level
		if self.price_level != 'N/A':
			price_level = '$' * int(self.price_level)
		return [self.name, str(self.rating), price_level, str(datetime.timedelta(seconds=self.time_taken))]
		 

	
def Summary(origin,destination,mode,mode_type):
	transport = TRANSIT_MODES[mode_type]
	url='https://maps.googleapis.com/maps/api/directions/json?origin={0}&destination={1}&mode={2}&key={3}'.format(origin, destination,transport,directions_key)
	r=requests.get(url)
	x=json.loads(r.text)
	legs=x['routes'][0]['legs']
	time=0
	if mode=='summary':
		return x['routes'][0]['summary']
	if mode=='time' :
		#return legs[0]['duration']['text']
		for leg in legs:
			time=time+leg['duration']['value']
		return time


def ShowAddress(location):
	url='https://maps.googleapis.com/maps/api/place/autocomplete/json?input={0}&radius=500&key={1}'.format(location,places_key)
	r=requests.get(url)
	x=json.loads(r.text)
	references=x['predictions']
	search_result=1
	places=[]
	for i, ref in enumerate(references):
		print i+1, ref['description']
		places.append(ref['place_id'])
	if not places:
		print('Could not find a starting address on google maps')
		sys.exit()

	x = int(raw_input("Choose your starting point from the above search results. :- \n"))	
	while x not in range(1, len(places) + 1):
		x = int(raw_input("Please enter a valid number from the list \n"))
		
	#Reverse Address Lookup needs to be done because directions API won't accept special characters
	return AddressLookup(places[x-1])

	

def AddressLookup(placeid):
	url='https://maps.googleapis.com/maps/api/place/details/json?placeid={0}&key={1}'.format(placeid,places_key)
	r=requests.get(url)
	x=json.loads(r.text)
	return x['result']['formatted_address']
	

def GetOptions(origin,destination,mode):
	food='coffee and donuts near '+destination
	if mode=='t':
		bike_or_walk=raw_input("Do you have a bike? \n")
	print("Searching for Coffee and Donut options around your destination.... : \n" )
	url='https://maps.googleapis.com/maps/api/place/textsearch/json?query={0}&key={1}'.format(food,places_key)
	r=requests.get(url)
	x=json.loads(r.text)
	results=x['results']
	place_objects=[]
	for i,r in enumerate(results):
		#print r['name']
		name=r['name']	
		place_id=r['place_id']
		rating = r.get('rating', 'N/A')
		price_level=r.get('price_level','N/A')
		if mode=='t':
			new_destination=AddressLookup(place_id)
			time_taken=Summary(origin,new_destination,'time',mode)
			if bike_or_walk in YES_OPTIONS :
				time_taken=time_taken+Summary(new_destination,destination,'time','b')
			else :
				time_taken=time_taken+Summary(new_destination,destination,'time','w')
		else:
			new_destination=destination+"&waypoints="+AddressLookup(place_id)
			time_taken=Summary(origin,new_destination,'time',mode)
		place_objects.append(places(name,place_id,rating,price_level,time_taken))
		if (i+1)%10==0:
			place_objects.sort(key=lambda place:place.time_taken)
			rows=[]
			for j,place_object in enumerate(place_objects):
				rows.append([str(j+1)] + place_object.summary())
			columns=['No', 'Name', 'Rating', 'Price Level', 'Time']
			print  tabulate(rows, headers=columns)
		
			more_options=raw_input("Do you want more options? Yes or No \n")
			if more_options in NO_OPTIONS:
				final_option=int(raw_input("Which place would you like to go to ? \n"))
				print place_objects[final_option-1]
				waypoint=place_objects[final_option-1].placeid_to_address()
				if mode=='t' :
					if bike_or_walk in YES_OPTIONS:
						NavigateMe(orgin,TRANSIT_MODE[mode],dest=waypoint)
						NavigateMe(waypoint,TRANSIT_MODE['b'],dest=destination)
					else :
						NavigateMe(origin,TRANSIT_MODE[mode],dest=waypoint)
						NavigateMe(waypoint,TRANSIT_MODE['w'],dest=destination)
					break
				else:	
					NavigateMe(origin, TRANSIT_MODES[mode],waypoints=waypoint)
				break
			

def NavigateMe(origin,transport,dest=None, waypoints=None):
	if not dest:
		dest = CLICKTIME_ADDRESS
	if not waypoints:
		url='https://maps.googleapis.com/maps/api/directions/json?origin={0}&mode={1}&destination={2}&key={3}'.format(origin, transport, dest, directions_key)
	else:
		url='https://maps.googleapis.com/maps/api/directions/json?origin={0}&mode={1}&destination={2}&key={3}&waypoints={4}'.format(origin, transport, dest, directions_key, waypoints)
	r=requests.get(url)
	x=json.loads(r.text)
	with open('/home/sandhya/steps', 'w') as somefile:
		somefile.write(json.dumps(x, indent=4))
	legs=x['routes'][0]['legs']
	print origin
	all_instructions = []
	for leg in legs:
		steps=leg['steps']
		for step in steps:
			if step['travel_mode'] != 'TRANSIT':
				all_instructions.append(strip_tags(step['html_instructions']))
			else:
				msg = "Take {0} {1} {2}".format(step['transit_details']['line'].get('short_name', ''), step['html_instructions'], step['transit_details']['line'].get('name', ''))
				all_instructions.append(msg)
		print '\n'.join(all_instructions)
		print "You have now reached ",leg['end_address'] 


location=raw_input("Enter your location\n")
location=location.replace(" ","")
location=ShowAddress(location)

print "Calculating best time summaries...."
walking_summary ="Walking via {0} : {1}".format(Summary(location,CLICKTIME_ADDRESS,'summary','w'),str(datetime.timedelta(seconds=Summary(location,CLICKTIME_ADDRESS,'time','w'))))
biking_summary="Bicycling via {0} : {1} ".format(Summary(location,CLICKTIME_ADDRESS,'summary','b'),str(datetime.timedelta(seconds=Summary(location,CLICKTIME_ADDRESS,'time','b'))))
transit_summary="Transit by Public transport {0} : {1} ".format(Summary(location,CLICKTIME_ADDRESS,'summary','t'),str(datetime.timedelta(seconds=Summary(location,CLICKTIME_ADDRESS,'time','t'))))

print "Best Time Summaries:"
print "\n".join([walking_summary,biking_summary,transit_summary])

option=raw_input("How do you want to commute? (w)alking , (b)icycling , (t)ransit \n")
while option not in TRANSIT_MODES.keys():
	option = raw_input('Please enter a valid transport option \n')

opt_for_snacks=raw_input("Do you want to buy some coffee/donuts? Yes/No\n")

if opt_for_snacks in YES_OPTIONS:
	GetOptions(location,CLICKTIME_ADDRESS,option)
else :	
	NavigateMe(location,TRANSIT_MODES[option],dest=CLICKTIME_ADDRESS)
