
# A collection of data scrapers for pulling time series popularity metrics for an input list of artists.
# This data was then compiled by hard to make a number of visualizations attempting to find high-impact venues across the country.
# In case you were wondering, the Billboard API is kinda really bad.
#
# Co-coded with Jon Culver for Dan Cosley's Learning from Web Data course at Cornell University


import urllib, simplejson, csv
import unicodedata
from datetime import date
import datetime
import time as timee
import pickle
from operator import itemgetter
import socket
import csv
import sys

fmkey=""
fmkey="714125979824dcab638818d8101f96db" # Erase before publication
if fmkey=="":
	fmkey="b25b959554ed76058ac220b7b2e0a026"

bkey=""
bkey="api_key=pehg5b9dxjpfswdfe9vmwxny"	# Erase before publication
if bkey=="":
	bkey="api_key=bvk4re5h37dzvx87h7rf5dqz"


## Helper method for adding/incrementing dict values
def addToDict(d, key, value):
	if key in d:
		d[key]+=[value]
	else:
		d[key]=[value]
	return d;

# A helper method for neatly converting simplejson objects to strong
def printJson(json):
	#this code lifted from simplejson.readthedocs.org
	s = simplejson.dumps(json, sort_keys=True, indent=4 * ' ')
	print '\n'.join([l.rstrip() for l in  s.splitlines()])

# An all purpose method for making queries to the last.fm API. Takes in the query string, which will include
# the query method and all needed variables.
def lastfmQuery(query):
	url= "http://ws.audioscrobbler.com/2.0/?method="
	key="&format=json&api_key="+fmkey
	print url+query+key
	try:
		search_results = urllib.urlopen(url+query+key)
	except IOError:
		print "Socket Error: Delay Period Passed, Retying Query "+url+query+key
		return lastfmQuery(query)
	return simplejson.loads(search_results.read())

# Gets the last.fm event list for the artist, retrieving the most recent 500 events 
# (we might need to raise that...). Returns in the format of list[dict{date, title, city, country, long/lat}],
# so each list entry is a dict with those keys mapping to their respective values	
def getEvents(artist):
	print "Get Events query for "+artist
	json = lastfmQuery("artist.getpastevents&limit=100&artist="+artist)
	json = json["events"]["event"]
	shows = []
	for event in json:
		if not int(event["cancelled"]):
			show={}
			dateinfo = event["startDate"].split()
			# Below is my least favorite line of code ever. strptime is a finicky bastard.
			show["date"]= int(timee.mktime(timee.strptime(str(event["startDate"][5:-9]), "%d %b %Y")))
			show["title"]= (event["title"])
			loc= event["venue"]["location"] #Just to make below cleaner
			show["city"]= (loc["city"])
			show["country"]= (loc["country"])			
			show["long"]= str((loc["geo:point"]["geo:long"]))
			show["lat"] = str((loc["geo:point"]["geo:lat"]))
			if show["country"]==(u'United States') and not show["long"]=='':
				shows+=[show]
			
	shows = sorted(shows, key=itemgetter('date'))
	return shows	

# Gets the top tag for a given artist.
def getTopTag(artist):
	json = lastfmQuery("artist.gettoptags&artist="+artist)
	return str(json["toptags"]["tag"][0]["name"])

# Gets the available time frames for the imput tag.
def getTagTimes(tag):
	json = lastfmQuery("tag.getweeklychartlist&limit=500&tag="+tag)
	json = json["weeklychartlist"]["chart"]
	times = []
	for time in json:
		times+=[(int(time["from"]))]
	times.sort()
	return times


# Creates a dict of artist:topTag pairs, and dumps it to a pickle file
def storeTags(artists, output):
	tags = dict((artist, getTopTag(artist)) for artist in artists)
	pickle.dump(tags, open(output, 'w'))
	return tags

# Creates a dict of tag:availableTagTimes pairs, and dumps it to a pickle file
def storeTagTimes(tags, output):
	times = dict((tag, getTagTimes(tag)) for tag in tags)
	pickle.dump(times, open(output, 'w'))
	return times

# Creates a dict of artist:eventList pairs, and dumps it to a pickle file
def storeEvents(artists, output):
	events = dict((artist, getEvents(artist)) for artist in artists)
	pickle.dump(events, open(output, 'w'))
	return events


# Right now, this is just broken. I don't really know where, but it is really, really is.
# Just ignore this method.
def getBillboardHistory(artist, times):
	byChart={}
	byWeek={}
	curPage = 0
	pastTour = 0
	trackz = 0
	notrack=0
	stime = date.fromtimestamp(times[0])
	etime = date.fromtimestamp(times[1])
	sdate = str(stime.year)+"-"+str(stime.month)+"-"+str(stime.day)
	edate = str(etime.year)+"-"+str(etime.month)+"-"+str(etime.day)
	query = "artist="+artist+"&format=json&sdate="+sdate+"&edate="+edate
	while not pastTour:
		query = query+"&start="+str(1+(50*curPage))
		json= billboardQuery(query)
		totalResults = json["searchResults"]["totalRecords"]
		json=json["searchResults"]["chartItem"]
		simplifiedjson=[]
		for c in json:
			week = str(c["chart"]["issueDate"])
			chart = str(c["chart"]["name"])
			rank = str(c["rank"])
			#peak = str(c["peak"])
			weeks = str(c["weeksOn"])
			if "song" in c:
				track = str(c["song"])
			else:
				track = None
			info = [track, week, chart, rank, weeks]
			addToDict(byChart, (chart,track), info)
			addToDict(byWeek, week, info)
		curPage+=1
		timee.sleep(.4) #CHANGE FOR NO JSON
		if curPage>10 or 1+(50*(curPage))>totalResults:
			pastTour = 1
	return byWeek, byChart


# As lastfmQuery above.
def billboardQuery(query):
	url= "http://api.billboard.com/apisvc/chart/v1/list?"
	key= bkey
	try:
		search_results = urllib.urlopen(url+key+"&"+query)
	except IOError:
		print "Socket Error: Delay Period Passed, Retying Query "+url+query+key
		return billboard(query)
	return simplejson.loads(search_results.read())


# Creates a dict of tagTime:tagChart pairs, and dumps it to a pickle file
def storeTagChart(tag, tagTimes, output):
	charts={}
	for i in range(len(tagTimes)-1):
		json = lastfmQuery("tag.getWeeklyArtistChart&limit=100&tag="+tag+
							"&from="+str(tagTimes[i])+"&to="+str(tagTimes[i+1]))
		if "weeklyartistchart" in json:
			chartDict = {}
			for entry in json["weeklyartistchart"]["artist"]:
				chartDict[entry["name"]] = int(entry["@attr"]["rank"])
			charts[tagTimes[i]] = chartDict
	pickle.dump(charts, open(output, "w"))
	return charts


# Well, okay. The billboardHistory function above works fine for collecting billboard data, it's
# everything down here that fails miserably.
def billboardArtistChart(artist, bbdata):
	singles={}
	general={}
	bbdata = bbdata[0]
	if not bbdata ==({},{}):
		for time in bbdata:
			for chart in bbdata[time]:
				if "songs" in chart[2].lower() or "single" in chart[2].lower():
					if time in singles:
						if chart[3]<singles[time]:
							singles[time]=chart[3]
					else:
						singles[time] = chart[3]
				else:
					if time in general:
						if chart[3] < general[time]:
							general[time]=chart[3]
					else:
						general[time] = chart[3]
	return singles, general

# Formats billboard output to a form usable by our visualization code
def formatBillboardData(singles, general, events, artist, tagTimes):
	return None, None # Because it is broken
	fsingles = []
	fgeneral = []
	bbtimes = list(set(singles.keys()+general.keys()))
	bbtimes.sort()
	candidatetimes = list((t["date"] for t in events[artist]))
	candidatetimes.sort()
	doneEvents=[]
	for event in events[artist]:
		stop = 0
		for time in bbtimes:
			d = datetime.datetime(int(time[0:4]), int(time[5:7]), int(time[8:]))
			date = timee.mktime(d.timetuple())
			bbtime=time
			for ti in candidatetimes:
				if ti>date and not stop:
					bbtime = time
					bbtimes = bbtimes[bbtimes.index(bbtime):]
					date = ti
					stop =1
		if bbtime in singles:
			fsingles+= [{"time":date, "long":event["long"], "lat":event["lat"], 
					"pop":singles[bbtime], "city":event["city"]}]
		if bbtime in general:
			fgeneral+= [{"time":date, "long":event["long"], "lat":event["lat"], 
					"pop":general[bbtime], "city":event["city"]}]
	return fsingles, fgeneral


def main():
	if len(sys.argv)==1:
		artists = raw_input("Please pass artist names into the command line, separated by commas:\n").split(",")
	else:
		artists = [sys.argv[1]]
		for i in range(2, len(sys.argv)):
			artists+=[sys.argv[i]]
	socket.setdefaulttimeout(5) # To handle hung requests.
	# First, assembles the tags (genres) for all artists.
	try:
		tags = pickle.load(open("fullTags.pkl", "r"))
	except IOError:
		print "Generating fullTags.pkl..."
		tags = storeTags(artists, "fullTags.pkl")
	
	# Then, collects the time stamps for which data is available, for each genre.
	try:
		tagTimes = pickle.load(open("fullTagTimes.pkl", "r"))
	except IOError:
		print "Generating fullEvents.pkl..."
		tagTimes = storeTagTimes(set(tags.values()), "fullTagTimes.pkl")
	
	# Next, stores lists of all events by each artist, as they are stored by last.fm.
	try:
		events = pickle.load(open("fullEvents.pkl", "r"))
	except IOError:
		print "Generating fullEvents.pkl..."
		events = storeEvents(artists, "fullEvents.pkl")
		
	# Now for the more timeconsuming web calls; this section gets the popularity charts from lastfm
	# for each available timeperiod, for each tag.  
	popData = {}
	for tag in set(tags.values()):
		try:
			tagCharts = pickle.load(open("fullTagCharts"+tag+".pkl", "r"))
			popData[tag]=tagCharts
		except IOError:
			print "Generating fullTagCharts"+tag+".pkl..."
			tagCharts = storeTagChart(tag, tagTimes[tag], "fullTagCharts"+tag+".pkl")
			popData[tag]=tagCharts
			
	# Next goes though all artists, and finds their rankings on the charts for their genre.
	fmData= {}
	for artist in artists:
		try:
			lastfmpops = pickle.load(open(artist+"lastfm.pkl", "r"))
		except IOError:
			print "Generating "+artist+"lastfm.pkl..."
			lastfmpops=[]
			tag = tags[artist]
			artEvents = events[artist]
			artCharts = popData[tag]
			for event in artEvents:
				date = event["date"]
				newDate=None
				for t in artCharts.keys():
					if (t-date)>0:
						newDate = t
						break
				if not newDate==None:
					for ar in artCharts[newDate].keys():
						try:
							if str(ar).lower() == artist.lower():
								lastfmpops+=[{"time":event["date"], "long":event["long"], "lat":event["lat"], 
									"pop":artCharts[newDate][ar], "city":str(event["city"])}]
						except:
							print "error parsing artist name: "+ar
							pass
			pickle.dump(lastfmpops, open(artist+"lastfm.pkl", "w"))
			fmData[artist]=lastfmpops
			
		#BillboardData
		# Attempts to do a similar metric to lastfm, but not nearly as well.
		# try:
		# 	bbdata = pickle.load(open(artist+" billboardraw.pkl", "r"))
		# except IOError:
		# 	print "Generating "+artist+" billboard.pkl..."
		# 	bbartist=artist
		# 	bbdata=getBillboardHistory(bbartist, [(events[artist][0]["date"]), (events[artist][-1]["date"])])
		# 	pickle.dump(bbdata, open(artist+" billboardraw.pkl", "w"))
		# try:
		# 	singles = pickle.load(open(artist+" bbsingles.pkl", "r"))
		# 	general = pickle.load(open(artist+" bbgeneral.pkl", "r"))
		# except IOError:
		# 	singles, general = billboardArtistChart(artist, bbdata)
		# 	pickle.dump(singles, open(artist+" bbsingles.pkl", "w"))
		# 	pickle.dump(general, open(artist+" bbgeneral.pkl", "w"))
		# try:
		# 	fsingles = pickle.load(open(artist+" fbbsingles.pkl", "r"))
		# 	fgeneral = pickle.load(open(artist+" fbbgeneral.pkl", "r"))
		# except IOError:
		# 	fsingles, fgeneral = formatBillboardData(singles, general, events, artist, tagTimes[tags[artist]])
		# 	pickle.dump(fsingles, open(artist+" fbbsingles.pkl", "w"))
		# 	pickle.dump(fgeneral, open(artist+" fbbgeneral.pkl", "w"))
			
	# Creates a number of csv files, to be interpreted by WEKA.
	fullwrite = csv.writer(open("fullweka.csv", "w"))
	fullwrite.writerow(["POPULARITY", "LAT", "LONG", "CITY", "TIME", "INCREASE"])
	for artist in artists:
		collection = {}
		collection[artist] = pickle.load(open(artist+"lastfm.pkl", "r"))
		writer = csv.writer(open(artist+"weka.csv", "w"))
		writer.writerow(["POPULARITY", "LAT", "LONG", "CITY", "TIME", "INCREASE"])
		for i in range(len(collection[artist])-1):
			e = collection[artist][i]
			positiveChange = float(e["pop"])<=float(collection[artist][i+1]["pop"])
			writer.writerow([e["pop"], e["lat"], e["long"], e["city"].replace(","," "), e["time"], positiveChange])
			fullwrite.writerow([e["pop"], e["lat"], e["long"], e["city"].replace(","," "), e["time"], positiveChange])



if __name__ == "__main__":
    main()