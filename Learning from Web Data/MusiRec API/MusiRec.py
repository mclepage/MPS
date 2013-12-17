import urllib
import simplejson

bkey=raw_input("Billboard key (blank for default): ")
if bkey=="":
	bkey="api_key=bvk4re5h37dzvx87h7rf5dqz"
else:
	bkey="api_key="+bkey
	
fmkey=raw_input("Last.fm key (blank for default): ")	
if fmkey=="":
	fmkey="api_key=9568bc1b5cf4f554c3d3cc7477d67dce"
else:
	fmkey="api_key="+fmkey
	
tkey=raw_input("TinySong key (blank for none): ")

artist = raw_input("Artist Name: ")
track = raw_input("Track Name: ")
if artist == "" and track == "":
	artist = "Temper Trap"
	track = "Sweet Disposition"
div='\n'+"--------------------------------------------------------------------------"+'\n'
div=div+div
testing=1
testfm=1
testtiny=1
testspot=1
testbill=1
testraw=1

def printJson(json):
	#this code lifted from simplejson.readthedocs.org
	s = simplejson.dumps(json, sort_keys=True, indent=4 * ' ')
	return '\n'.join([l.rstrip() for l in  s.splitlines()])


def lastfmQuery(query):
	url= "http://ws.audioscrobbler.com/2.0/?method="
	key="&format=json&"+fmkey
	search_results = urllib.urlopen(url+query+key)
	return simplejson.loads(search_results.read())


def lastfmTrackInfo(track, artist):
	query="track.getInfo&autocorrect=1&artist="+artist+"&track="+track
	json = lastfmQuery(query)
	if "error" in json:
		return "Error:: "+json["message"]
	return json["track"]


if testing and testfm and testraw and 1:
	print div
	trackinfo=lastfmTrackInfo(track, artist)
	print "lastfmTrackInfo: "+printJson(trackinfo)


def lastfmTrackSimilar(track, artist, limit=5):
	#based on 'listening data'
	similarityDict = {}
	query="track.getsimilar&autocorrect=1&limit="+str(limit)+"&artist="+artist+"&track="+track
	json = lastfmQuery(query)
	if "error" in json:
		return "Error:: "+json["message"]
	simData=[]
	for t in json["similartracks"]["track"]:
		simData+= [{"artist":t["artist"]["name"], "track": t["name"]}]
	return simData


if testing and testfm and 1:
	print div
	print "lfmTrackSimilar: " +printJson(lastfmTrackSimilar(track,artist))

def lastfmArtistInfo(artist):
	query="artist.getInfo&autocorrect=1&artist="+artist
	json = lastfmQuery(query)
	if "error" in json:
		return "Error:: "+json["message"]
	return json["artist"]


if testing and testraw and testfm and 1:
	print div
	print "lfmArtistInfo: " + printJson(lastfmArtistInfo(artist))

def lastfmArtistSimilar(artist, limit=5):
	similarityDict = {}
	query="artist.getsimilar&autocorrect=1&artist="+artist+"&limit="+str(limit)
	json = lastfmQuery(query)
	if "error" in json:
		return "Error:: "+json["message"]
	simData=[]
	for t in json["similarartists"]["artist"]:
		simData+= [{"artist":t["name"], "match": t["match"]}]
	if 1:
		return simData


if testing and testfm and 1:
	print div
	print "lfmArtistSimilarity: " +printJson(lastfmArtistSimilar(artist))

def tinysongSuggestQuery(query, limit=5):
	url="http://tinysong.com/s/"
	query=query.replace(" ","+")
	key="?format=json&limit="+str(limit)+"&key="+tkey
	search_results = urllib.urlopen(url+query+key)
	json=simplejson.loads(search_results.read())
	if "error" in json:
		return "Error:: "+json["error"]
	suggestionLib=[]
	for i in json:
		suggestionLib+=[{"artist":i["ArtistName"], "track":i["SongName"]}]
	return suggestionLib


if testing and testtiny and 1:
	print div
	print "tinysongSuggestQuery(artist): "+printJson(tinysongSuggestQuery(artist))
	print "tinysongSuggestQuery(track): "+printJson(tinysongSuggestQuery(track))
	print "tinysongSuggestQuery(track+\" \"+artist): "+printJson(tinysongSuggestQuery(track+" "+artist))


def spotifyTrackQuery(query, limit=5):
	if query=="":
		return
	url="http://ws.spotify.com/search/1/track.json?q="
	search_results = urllib.urlopen(url+query)
	json=simplejson.loads(search_results.read())
	json["tracks"] = json["tracks"][:limit]
	simplifiedjson = []
	for i in json["tracks"]:
		# Takes only the first artist, this won't often be a problem but might
		# need to be changed at some point.
		simplifiedjson+=[{"album":i["album"]["name"], "artist":i["artists"][0]["name"],
			"track":i["name"], "popularity":i["popularity"], "year":i["album"]["released"]
		}]
	return simplifiedjson


if testing and testspot and 1:
	print div
	print "spotifyTrackQuery(): "+printJson(spotifyTrackQuery(track))

def spotifyArtistQuery(query, limit=5):
	if query=="":
		return
	url="http://ws.spotify.com/search/1/artist.json?q="
	search_results = urllib.urlopen(url+query)
	json=simplejson.loads(search_results.read())
	json["artists"] = json["artists"][:limit]
	simplifiedjson = []
	for i in json["artists"]:
		# Takes only the first artist, this won't often be a problem but might
		# need to be changed at some point.
		simplifiedjson+=[{"artist":i["name"], "popularity":i["popularity"] }]
	return simplifiedjson

if testing and testspot and 1:
	print div
	print "spotifyArtistQuery(): "+printJson(spotifyArtistQuery(artist))

def spotifyAlbumQuery(query, limit=5):
	if query=="":
		return
	url="http://ws.spotify.com/search/1/album.json?q="
	search_results = urllib.urlopen(url+query)
	json=simplejson.loads(search_results.read())
	json["albums"] = json["albums"][:limit]
	simplifiedjson = []
	for i in json["albums"]:
		# Takes only the first artist, this won't often be a problem but might
		# need to be changed at some point.
		simplifiedjson+=[{"album":i["name"], "artist":i["artists"][0]["name"],
		 "popularity":i["popularity"] }]
	return simplifiedjson

if testing and testspot and 1:
	print div
	print "spotifyAlbumQuery(): "+printJson(spotifyAlbumQuery(track))


def billboardSearch(track = "", artist="", limit=5, stime=2010, etime=""):
	url="http://api.billboard.com/apisvc/chart/v1/list?"
	if etime=="":
		etime=str(stime+1)
	query="format=json&sdate="+str(stime)+"-1-1&edate="+etime+"-1-1&count="+str(limit)+"&"
	if track!="":
		query+="track="+track+"&"
	if artist!="":
		query+="artist="+artist+"&"
	key=bkey
	print url+query+key
	search_results = urllib.urlopen(url+query+key)
	try:
		json=simplejson.loads(search_results.read())
	except:
		return "Billboard failed"
	json=json["searchResults"]["chartItem"]
	simplifiedjson=[]
	for c in json:
		simplifiedjson+=[{"artist":c["artist"], "track":c["song"], "chart":c["chart"]["name"], 
			"charttime":c["chart"]["issueDate"], "chartpeak":c["peak"], "weekson":c["weeksOn"]}]
	return simplifiedjson


if testing and testbill and 0:
	print div
	print "billboardSearch(title, artist)): "+ printJson(billboardSearch(track, artist))

def getSimilarTracks(trackname):
	json = spotifyTrackQuery(trackname)
	if len(json)<1:
		print "No track with name "+trackname+" found."
		return
	track, artist, year = json[0]["track"], json[0]["artist"], json[0]["year"]
	simTracks = lastfmTrackSimilar(track, artist)
	simTracksSpotified = []
	for track in simTracks:
		print simTracks
		simTracksSpotified+=spotifyTrackQuery(track["track"], 1)
	print div
	print "getSimilarTracks:"
	print printJson(simTracks)
	print printJson(simTracksSpotified)
	print div
	print "Results for " + trackname + " by " + artist + ":"
	print "\n Last.fm recommends:"
	for track in simTracksSpotified:
		print track["track"] + " - " + track["artist"] + ", " + track["year"] + " (" + track["popularity"] + ")"
	
getSimilarTracks(track)