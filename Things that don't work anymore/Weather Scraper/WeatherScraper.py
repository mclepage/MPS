import urllib, csv, pickle, os, sys, socket, random
from datetime import datetime

weatherHistory={}
eventTypes=[]
conditionTypes=[]

''' 
	A handler method for generating and sending weather queries. This function will return
	a urllib reader for the contents of the wunderground history page for loc on the day
	year-month-day.
'''
def wunderQuery(loc, year, month, day):
	url = "http://www.wunderground.com/history/airport/"+loc+"/"+str(year)+"/"+str(month)+"/"+str(day)+"/DailyHistory.html?format=1"
	try:
		return urllib.urlopen(url)
	except IOError:
		print "Socket Error: Delay Period Passed, Retying Query:"
		print "\t"+url
		return wunderQuery(loc, year, month, day)


'''
	Gathers and parses the by-hour weather data for a given place-time combination.
	The wunderground/history?format=1 variable allows for data to be returned in 
	comma-separated format, as opposed to our earlier scripts reliance of html parsing.
	the global variable weatherHistory acts as a form of memoization, storing a hash
	of all past weather queries.
'''
def getHourlyWeather(loc, year, month, day):
	global weatherHistory
	global eventTypes
	global conditionTypes
	if not loc in weatherHistory:
		weatherHistory[loc]={}
	if (year, month, day) in weatherHistory[loc]:
		return weatherHistory[loc][(year, month, day)]
		
	page = wunderQuery(loc, year, month, day)
	hourlyWeather = {}
	for line in page:
		if "," in line and "Time" not in line:
			weatherInfo=[]
			line = line.split(",")
			d = datetime.strptime(str(year)+" "+str(month)+" "+str(day)+" "+str(line[0]),
			 							"%Y %m %d %I:%M %p")
			#d = d.replace(minute=0)
			try:
				weatherInfo+=[float(line[1])] # Temperature
				weatherInfo+=[float(line[5])] # Visibility
				if line[7]=="Calm":
					weatherInfo+=[0.0] # WindSpeed
				else:
					weatherInfo+=[float(line[7])] # WindSpeed
				if "." not in line[9]:
					weatherInfo+=[0.0] # Precipitation
				else:
					weatherInfo+=[float(line[9])] # Precipitation

				weatherInfo+=[line[-3]] # Condition
				weatherInfo+=[line[-4]] # Event
				
				if line[-3] not in conditionTypes:
					conditionTypes+=[line[-3]]
				if line[-4] not in eventTypes:
					eventTypes+=[line[-4]]
				
				# Output is: [Temp, Vis, WindSpeed, Precip, Cond, Event]
				hourlyWeather[d] = weatherInfo
			except:
				print "getHourlyWeather error: ", sys.exc_info()[0]
				print line
	weatherHistory[loc][(year, month, day)] = hourlyWeather
	return hourlyWeather
	

'''
	Parses all csv files in directory, looking for the airport codes in airports and printing
	data points for these codes in their own files, one for each unique code.
'''
def mergeAllCSVsByAirport(directory, airports, outputfile):
	csvs = os.listdir(directory)
	outfiles = dict((airport, csv.writer(open(airport+outputfile, "w"))) for airport in airports)
	out = csv.writer(open(outputfile, "w"))
	gotHeader = 0
	for fname in csvs:
		if ".csv" in fname:
			infile = csv.reader(open(directory+"/"+fname, "r"))
			for line in infile:
				if "MONTH" in line:
					if not gotHeader:
						gotHeader=1
						for code in outfiles:
							outfiles[code].writerow(line)
				else:
					outfiles[line[6]].writerow(line)


'''
	Looks up and adds weather data to all datapoints in all csvs in dirctory, provided
	those datapoints have a departing variable contained in airportList.
'''
def addWeatherData(airportList, directory, outDirectory):
	csvs = os.listdir(directory)
	header=""
	global weatherHistory
	for fname in csvs:
		print "Generating w"+fname+"..."
		if ".csv" in fname and "L_" not in fname:
			outfile = csv.writer(open(outDirectory+"/W"+fname, 'w'))
			year = fname.split("-")[0]
			infile = csv.reader(open(directory+"/"+fname, "r"))
			for line in infile:
				line = line[:-1]
				
				if "MONTH" in line:
					outfile.writerow(line+["TEMPERATURE","VISIBILITY", "WINDSPEED", "PRECIPITATION", "CONDITION", "EVENT"])
				else:
					for i in [1]:
						loc = line[6]
						if not loc in airportList:
							break
						month = line[0]
						day = line[1]
						time = datetime(int(year), int(month), int(day), int(line[8][:2]), int(line[8][2:]))
						if not loc in weatherHistory or not (year, month, day) in weatherHistory[loc]:
							
							weather = getHourlyWeather(loc, year, month, day)
						else:
							weather = weatherHistory[loc][(year, month, day)]
						tweather= getWeatherTime(weather, time)
						outfile.writerow(line+tweather)
					#except:
					#	print "addWeatherData error: ", sys.exc_info()[0]
					#	print line
	global eventTypes
	global conditionTypes
	print eventTypes
	print conditionTypes


'''
	A quick helper method for associating a depart time to a weather time, as they rarely
	directly overlapped.
'''
def getWeatherTime(hourlyWeather, departDateTime):
	closest = sorted(hourlyWeather.keys(), key=lambda d: abs(departDateTime - d))[0]
	return hourlyWeather[closest] 



def main():
	socket.setdefaulttimeout(3)
	airports = ["LAX", "ATL", "ORD", "DEN", "PHX", "IAH", "CLT", "MIA", "MCO", "SFO", "JFK", "DFW"]
	addWeatherData(airports, "2010-current", "2010-merged5")
	mergeAllCSVsByAirport("2010-merged5", airports, "complete.csv")



if __name__ == "__main__":
    main()
