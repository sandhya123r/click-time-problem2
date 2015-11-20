import requests
import json
import datetime
import sys
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

class places :
	def __init__(self,name,place_id,rating,price_level,time_taken):
		self.name=name
		self.place_id=place_id
		self.rating=rating
		self.price_level=price_level
		self.time_taken=time_taken
	

	
def Summary(origin,destination,mode,mode_type):
	if mode_type=='w':
		transport='walking'
	if mode_type=='b' :
		transport='bicycling'
	if mode_type=='t'  :
		transport='transit'
	key = 'AIzaSyCl_7phc2HQOSimmScmS09NW_A9dlQklqw'	
	url='https://maps.googleapis.com/maps/api/directions/json?origin={0}&destination={1}&mode={2}&key={3}'.format(origin, destination,transport,key)
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

def AddressLookup(placeid,key):
	url='https://maps.googleapis.com/maps/api/place/details/json?placeid={0}&key={1}'.format(placeid,key)
	r=requests.get(url)
	x=json.loads(r.text)
	return x['result']['formatted_address']
	

def GetOptions(origin,destination,mode):
	food='coffee and donuts near '+destination
	key = 'AIzaSyAAVTbGtg6q-4ioZF4gqM8pqXaLPxBILsM'
	print("Coffee and Donut options around you are : \n" )
	url='https://maps.googleapis.com/maps/api/place/textsearch/json?query={0}&key={1}'.format(food,key)
	r=requests.get(url)
	x=json.loads(r.text)
	results=x['results']
	place_objects=[]
	print "Displaying some results \n"
	for i,r in enumerate(results):
		#print r['name']
		name=r['name']	
		place_id=r['place_id']
		rating = r.get('rating', 'N/A')
		price_level=r.get('price_level','N/A')
		new_destination=destination+"&waypoints="+AddressLookup(place_id,key)
		time_taken=Summary(origin,new_destination,'time',mode)
		place_objects.append(places(name,place_id,rating,price_level,time_taken))
		if (i+1)%10==0:
			sorted(place_objects,key=lambda place:place.time_taken)
			for j,place_object in enumerate(place_objects):
				print j+1," ",place_object.name," ",place_object.rating," ", place_object.price_level,"",str(datetime.timedelta(seconds=place_object.time_taken))
			more_options=raw_input("Do you want more options? Yes or No \n")
			if more_options=='No' or more_options=='no':
				final_option=raw_input("Which place would you like to go to ? \n")
				break
			
		
	

		
	#print i+1," : ", r['name'],time_taken,"minutes" , "Rating ", rating, price_level
	#places.append((i,(place_id,r['name'])))
	#if ((i+1)%10==0) :
	#	more_options=raw_input("Do you want more options? Yes or No \n")
	#	if more_options=='No' or more_options=='no':
	#		final_option=raw_input("Which place would you like to go to ? \n")
	#		return 0;
			
	#maintain a list of donut and coffee shops using their place_ids
		
	

def NavigateMe(origin,transport,waypoints):
	destination = '282 2nd Street 4th floor, San Francisco, CA 94105'
	key = 'AIzaSyCl_7phc2HQOSimmScmS09NW_A9dlQklqw'
	GetOptions(destination)
	url='https://maps.googleapis.com/maps/api/directions/json?origin={0}&mode={1}&destination={2}&key={3}'.format(origin, transport, destination, key)
	r=requests.get(url)
	x=json.loads(r.text)
	legs=x['routes'][0]['legs']
	steps=legs[0]['steps']
	
	#instructions=steps[0]['html_instructions']
	#print steps[0].keys()
	#print len(steps),steps[0].keys()
	#print len(legs),legs[0].keys()
	all_instructions = [x['html_instructions'] for x in steps]
	print '\n'.join(all_instructions)


location=raw_input("Enter your location\n")
location=location.replace(" ","")
destination = '282 2nd Street 4th floor, San Francisco, CA 94105'
print "Best Times Summary\n"
print "Walking via ",Summary(location,destination,'summary','w')," : ",str(datetime.timedelta(seconds=Summary(location,destination,'time','w')))," \n"
print "Bicycling via ",Summary(location,destination,'summary','b')," : ",str(datetime.timedelta(seconds=Summary(location,destination,'time','b')))," \n"
print "Transit by Public transport ",Summary(location,destination,'summary','t')," : ",str(datetime.timedelta(seconds=Summary(location,destination,'time','t')))," \n"

option=raw_input("Which option do you prefer ? w for walking , b for bicycling , t for transit \n")
opt_for_snacks=raw_input("Do you want to buy some coffee/donuts?y for yes,n for no \n")
if opt_for_snacks=='y':
	GetOptions(location,destination,option)
	
#if ans == 'y':
#	transport='bicycling'
#	NavigateMe(location,transport)
#else :
	#print "Walking from your location to office takes ",str(datetime.timedelta(seconds=CalculateDuration(location,'w')))," \n"
	#print " Transit time with public transport takes ", str(datetime.timedelta(seconds=CalculateDuration(location,'t')))," \n"
#	ans=raw_input("Do you want to walk or take public transport ? Enter w or t \n")
#	if ans == 'w' :
#		transport='walking'
#		GetOptions(location,destination,ans)
#		NavigateMe(location,transport)
#	if ans=='t'   :
#		transport='transit'
#		GetOptions(location,destination,ans)
#		NavigateMe(location,transport)


