import requests
import json
import datetime
import sys
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()
from tabulate import tabulate
from HTMLParser import HTMLParser
import unittest

YES_OPTIONS = ['yes', 'YES', 'Yes', 'y', 'Y', 'yo', 'yES','YeS']
NO_OPTIONS = ['no', 'NO', 'No', 'n', 'N','nO']
TRANSIT_MODES = {'b': 'bicycling', 'w': 'walking', 't': 'transit','f':'flying'}

#directions_key = 'AIzaSyCl_7phc2HQOSimmScmS09NW_A9dlQklqw'
#places_key = 'AIzaSyDF1YIjBPwXLcrxCIKGa9otfMYf6B0B3z4'

directions_key = 'AIzaSyC5EBT95BFn_AfLj5kNDHyeyn6VnVazmus'
places_key = 'AIzaSyCBXi_thAe29Mg9e3JJrVJCB6Hm2TKp3rg'

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


class NavigateException(Exception):
	"""Class for exceptions raised in this module """

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
        return address_lookup(self.place_id)
        
    def summary(self):
        price_level = self.price_level
        if self.price_level != 'N/A':
            price_level = '$' * int(self.price_level)
        return [self.name, str(self.rating), price_level, str(datetime.timedelta(seconds=self.time_taken))]
    
class GoToClickTime(object) :
    def __init__(self):
        pass
    def Summary(self,origin,destination,mode,mode_type):
         mode_type=mode_type
         origin=origin
         destination=destination
         mode=mode
         transport = TRANSIT_MODES[mode_type]
         url='https://maps.googleapis.com/maps/api/directions/json?origin={0}&destination={1}&mode={2}&key={3}'.format(origin,destination,transport,directions_key)
         r=requests.get(url)
         x=json.loads(r.text)
         
         if not x['routes']  :
         	return -1
         else:
         	legs=x['routes'][0]['legs']
		time=0
		if mode=='summary':
		        return x['routes'][0]['summary']
		if mode=='time' :
		        #return legs[0]['duration']['text']
		        for leg in legs:
		                time=time+leg['duration']['value']
		        return time


def show_address(location):
    url='https://maps.googleapis.com/maps/api/place/autocomplete/json?input={0}&radius=50000&key={1}'.format(location,places_key)
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
    return address_lookup(places[x-1])

    

def address_lookup(placeid):
    url='https://maps.googleapis.com/maps/api/place/details/json?placeid={0}&key={1}'.format(placeid,places_key)
    r=requests.get(url)
    x=json.loads(r.text)
    return x['result']['formatted_address']
    

def get_options(origin,destination,mode):
    destination=CLICKTIME_ADDRESS
    food='coffee and donuts near '+destination
    if mode=='t':
        bike_or_walk=raw_input("Do you have a bike? Yes/No\n")
    print("Searching for Coffee and Donut options around your destination.... : \n" )
    url='https://maps.googleapis.com/maps/api/place/textsearch/json?query={0}&key={1}'.format(food,places_key)
    r=requests.get(url)
    x=json.loads(r.text)
    results=x['results']
    place_objects=[]
    option_obj=GoToClickTime()
    for i,r in enumerate(results):
        #print r['name']
        name=r['name']  
        place_id=r['place_id']
        rating = r.get('rating', 'N/A')
        price_level=r.get('price_level','N/A')
        if mode=='t':
            new_destination=address_lookup(place_id)
            time_taken=option_obj.Summary(origin,new_destination,'time',mode)
            if bike_or_walk in YES_OPTIONS :
                time_taken=time_taken+option_obj.Summary(new_destination,destination,'time','b')
            else :
                time_taken=time_taken+option_obj.Summary(new_destination,destination,'time','w')
        else:
            new_destination=destination+"&waypoints="+address_lookup(place_id)
            time_taken=option_obj.Summary(origin,new_destination,'time',mode)
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
                        navigate_me(origin,TRANSIT_MODES[mode],dest=waypoint)
                        navigate_me(waypoint,TRANSIT_MODES['b'],dest=destination)
                    else :
                        navigate_me(origin,TRANSIT_MODES[mode],dest=waypoint)
                        navigate_me(waypoint,TRANSIT_MODES['w'],dest=destination)
                    break
                else:   
                    navigate_me(origin, TRANSIT_MODES[mode],waypoints=waypoint)
                break
            

def navigate_me(origin,transport,dest=None, waypoints=None):
    if not dest:
        dest = CLICKTIME_ADDRESS
    if not waypoints:
        url='https://maps.googleapis.com/maps/api/directions/json?origin={0}&mode={1}&destination={2}&key={3}'.format(origin, transport, dest, directions_key)
    else:
        url='https://maps.googleapis.com/maps/api/directions/json?origin={0}&mode={1}&destination={2}&key={3}&waypoints={4}'.format(origin, transport, dest, directions_key, waypoints)
    r=requests.get(url)
    x=json.loads(r.text)
    legs=x['routes'][0]['legs']
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


def main():
	location=raw_input("Enter your location\n")
	location=location.replace(" ","")
	location=show_address(location)

	g=GoToClickTime()

	print "Calculating best time summaries...."

	walking_time=g.Summary(location,CLICKTIME_ADDRESS,'summary','w')
	biking_time=g.Summary(location,CLICKTIME_ADDRESS,'summary','b')
	transit_time=g.Summary(location,CLICKTIME_ADDRESS,'summary','t')

	walking_summary ="Walking via {0} : {1}".format(walking_time,str(datetime.timedelta(seconds=g.Summary(location,CLICKTIME_ADDRESS,'time','w'))))
	biking_summary="Bicycling via {0} : {1} ".format(biking_time,str(datetime.timedelta(seconds=g.Summary(location,CLICKTIME_ADDRESS,'time','b'))))
	transit_summary="Transit by Public transport {0} : {1} ".format(transit_time,str(datetime.timedelta(seconds=g.Summary(location,CLICKTIME_ADDRESS,'time','t'))))

	if transit_time!= -1 and biking_time!= -1 and walking_time!=-1   :    
			print "Best Time Summaries:"
			print "\n".join([walking_summary,biking_summary,transit_summary])
			option=raw_input("How do you want to commute? (w)alking , (b)icycling , (t)ransit (f)lying \n")
			while option not in TRANSIT_MODES.keys():
	    			option = raw_input('Please enter a valid transport option \n')
	else :
		print "You may want to take a flight ..... \n"
		option='f'

	if option=='f' :
	    new_location="Airport San Francisco"
	    print "Checking airports near ClickTime office ....\n"
	    location=show_address(new_location)
	    navigate_now_or_later=raw_input("Do you want steps of navigation from airport now? Yes/No \n")
	    if navigate_now_or_later in NO_OPTIONS :
		print "Goodbye! :)"
		sys.exit()
	    if navigate_now_or_later in YES_OPTIONS :
	    	print "Best time summaries from the airport to  Click Time office....\n"
	    	walking_summary ="Walking via {0} : {1}".format(g.Summary(location,CLICKTIME_ADDRESS,'summary','w'),str(datetime.timedelta(seconds=g.Summary(location,CLICKTIME_ADDRESS,'time','w'))))
		biking_summary="Bicycling via {0} : {1} ".format(g.Summary(location,CLICKTIME_ADDRESS,'summary','b'),str(datetime.timedelta(seconds=g.Summary(location,CLICKTIME_ADDRESS,'time','b'))))
		transit_summary="Transit by Public transport {0} : {1} ".format(g.Summary(location,CLICKTIME_ADDRESS,'summary','t'),str(datetime.timedelta(seconds=g.Summary(location,CLICKTIME_ADDRESS,'time','t'))))
		print "\n".join([walking_summary,biking_summary,transit_summary])
	    	option=raw_input("How do you want to commute from airport ? (w)alking , (b)icycling , (t)ransit \n")
	    	
	    	
	opt_for_snacks=raw_input("Do you want to buy some coffee/donuts? Yes/No\n")

	if opt_for_snacks in YES_OPTIONS:
	    get_options(location,CLICKTIME_ADDRESS,option)
	else :  
	    navigate_me(location,TRANSIT_MODES[option],dest=CLICKTIME_ADDRESS)
	    
	    
if __name__ == '__main__':
	main()
