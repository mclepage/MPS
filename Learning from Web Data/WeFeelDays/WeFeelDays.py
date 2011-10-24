from BeautifulSoup import BeautifulStoneSoup
import urllib
import urllib2
import simplejson
import csv


feelings = ['happy','sad','depressed','stressed','good','bad','tired','hurt','important', 'drunk','afraid']
feelingString='happy,sad,depressed,stressed,good,bad,tired,hurt,important,drunk,afraid'
fullFeelings=list(feelings)

from datetime import date

oldDate = date(1911, 11, 11)  # year, month, <strong class="highlight">day</strong>

weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
months=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sept","Oct","Nov","Dec"]
#daysoftheweek={0:"",1:"",2:"",3:"",4:"",5:"",6:""}
daysoftheweek={0:[],1:[],2:[],3:[],4:[],5:[],6:[]}

for i in range(1,366):
	d = date.fromordinal(i).replace(year=2010)
	datestring = "2010-"+(str(d.month) if d.month>10 else "0"+str(d.month))+"-"+(str(d.day) if d.day>10 else "0"+str(d.day))
	daysoftheweek[date.weekday(d)]+=[datestring]
#print daysoftheweek

dayFeelings={0:[],1:[],2:[],3:[],4:[],5:[],6:[]}
monthFeelings={1:[],2:[],3:[],4:[],5:[],6:[],7:[],8:[],9:[],10:[],11:[],12:[] }
for weekday in daysoftheweek:
	#print weekday
	#print daysoftheweek[weekday]
	#query = "display=text&returnfields=feeling&limit=1500&postdate="+daysoftheweek[weekday]#+"&feeling="+feelingString
	for day in daysoftheweek[weekday]:
		query = "display=text&returnfields=feeling&limit=1500&postdate="+day#+"&feeling="+feelingString
		url = 'http://api.wefeelfine.org:8080/ShowFeelings?'+ query
		print url
		search_results = urllib.urlopen(url)
		soup =  BeautifulStoneSoup(search_results).prettify()
		#print soup
		for i in str(soup).split():
			#print i
			if "br" not in i:
				if i not in fullFeelings:
					print i
					fullFeelings+=[i]
				dayFeelings[weekday]+= [i] 
				monthFeelings[int(day[5:7])]+= [i]
			##dayFeelings[weekday]+= [i] if i in feelings else ''
			##monthFeelings[int(day[5:7])]+= [i] if i in feelings else ''
		#print dayFeelings

#print dayFeelings

f=open("moodstats Direct.csv",'wb')
fp=open("moodstats Proportional.csv",'wb')
writer=csv.writer(f)
writer.writerow(["Day of the Week"]+feelings)
writerp=csv.writer(fp)
writerp.writerow(["Day of the Week"]+feelings)

for day in dayFeelings:
	#print weekdays[day]
	curRow=[weekdays[day]]
	curRowp=[weekdays[day]]
	for mood in feelings:
		#print "   "+mood+" "+str((dayFeelings[day]).count(mood))
		curRow+=[str((dayFeelings[day]).count(mood))]
		if len(dayFeelings[day])>0:
			curRowp+=[str( (float(dayFeelings[day].count(mood)))/float(len(dayFeelings[day])) )]
		else:
			curRowp+=[0]
	writer.writerow(curRow)
	writerp.writerow(curRowp)

f=open("moodstats DirectFULL.csv",'wb')
fp=open("moodstats ProportionalFULL.csv",'wb')
writer=csv.writer(f)
writer.writerow(["Day of the Week"]+feelings)
writerp=csv.writer(fp)
writerp.writerow(["Day of the Week"]+feelings)

for day in dayFeelings:
	#print weekdays[day]
	curRow=[weekdays[day]]
	curRowp=[weekdays[day]]
	for mood in fullFeelings:
		#print "   "+mood+" "+str((dayFeelings[day]).count(mood))
		curRow+=[str((dayFeelings[day]).count(mood))]
		if len(dayFeelings[day])>0:
			curRowp+=[str( (float(dayFeelings[day].count(mood)))/float(len(dayFeelings[day])) )]
		else:
			curRowp+=[0]
	writer.writerow(curRow)
	writerp.writerow(curRowp)
	
fm=open("moodstats Monthly.csv",'wb')
writerm=csv.writer(fm)
writerm.writerow(["Month"]+feelings)
for month in monthFeelings:
	print month
	curRow=[months[month-1]]
	print months[month]
	print "here"
	for mood in feelings:
		if len(monthFeelings[month])>0:
			curRow+=[str( (float(monthFeelings[month].count(mood)))/float(len(monthFeelings[month])) )]
		else:
			curRow+=[0]
	writerm.writerow(curRow)

fm=open("moodstats MonthlyFULL.csv",'wb')
writerm=csv.writer(fm)
writerm.writerow(["Month"]+feelings)
for month in monthFeelings:
	print month
	curRow=[months[month-1]]
	#print months[month]
	#print "here"
	for mood in fullFeelings:
		if len(monthFeelings[month])>0:
			curRow+=[str( (float(monthFeelings[month].count(mood)))/float(len(monthFeelings[month])) )]
		else:
			curRow+=[0]
	writerm.writerow(curRow)


#feelingList=[]
#for feeling in [1]:
#	for month in range(1,12):
#		for day in range(1,2):
#			if month<10:
#				month="0"+str(month)
#			if day<10:
#				day="0"+str(day)
			#query = "display=text&returnfields=feeling&limit=5&postdate=2010-"+str(month)+"-"+str(day)+"&feeling="+feelingString
			#url = 'http://api.wefeelfine.org:8080/ShowFeelings?'+ query
			#search_results = urllib.urlopen(url)
			#print search_results
			#soup =  BeautifulStoneSoup(search_results).prettify()
			#for i in str(soup).split():
			#	print i
			#	feelingList+= [i] if i in feelings else ''
#print feelingList
#print len(feelingList)
	#for i in range(0, len(soup.contents)):
	#print soup.contents[2].contents[2]
	#print""
	#print soup.contents[2].contents[2]