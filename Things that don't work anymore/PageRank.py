from __future__ import division # Forces float division of ints, I don't really know why...
import urllib
import pickle
import numpy as np
import re

## Helper method for adding/incrementing dict values
def addToDict(d, key, value):
	if key in d:
		if not value in d[key] and not isinstance(value, list):
			d[key]=d[key]+[value]
		elif isinstance(value, list):
			for e in value:
				if e not in d[key]:
					d[key]+=[e]
	else:
		d[key]=[value]
	return d;

## Reads in the target URLs from filepath
def readUrlList(filepath): # Used to be getLinkList but I realized that was confusing...
	f=open(filepath)
	urls = []
	for line in f:
		line=line.split()[0] # Eliminates newline characters
		if not line[-1]=="/" and not ".htm" in line:
			line+="/"
		urls+=[line]
	return urls

# Scrapes all needed content from the URL input, including page title, all links
# with their target pages and anchor text, and a snippet of the page's body text.
# Some of these functions are done with regular expressions, but most are hardcoded.
def scrapeLinks(url):
	urlContents = urllib.urlopen(url)
	links=[]
	title=""
	p = re.compile(r'<.*?>')
	blurb=""
	for line in urlContents:
		if "<p>" in line and "</p>" in line:
			blurb+=line[line.index("<p>")+3:line.index("</p>")]
		if "<title>" in line:
			if "</title>" in line:
				title=line[line.index("<title>")+7:line.index("</title>")]
		while "<a " in line:
			if "</a>" not in line:
				#print " SKIPPED:"
				#print "       "+url
				line=""
			else:
				links+= [line[line.index("<a"):line.index("</a>")+4]]
				line = line[line.index("</a>")+4]
	blurb=p.sub('', blurb)
	return links, title, blurb

# Reads in all link text, and finds what parts of the text correspond to the target page
# and the anchor. Returns a dictionary of url:anchor pairings
def interpretLinks(linkStrings, pageurl, urlList):
	cleanLinks={}
	for link in linkStrings:
		if "href" in link and '"' in link:
			url = link[link.index("href")+6:link[link.index("href")+6:].index('"')+9]
			if "#" in url:
				url = url[:url.index("#")]
			if  "/" in url and url[0]=="/":
				url=url[1:]
			if "../" in url:
				trimmedpageurl = pageurl[0:-1]
				while "../" in url:
					url = url[url.index("../")+3:]
					trimmedpageurl= pageurl[0:trimmedpageurl.rindex("/")]
				url= trimmedpageurl+"/"+url
			if "http://" not in url:
				url = pageurl+url
			anchor = link[link.index(">")+1:link.index("<", 2)]
			if not url[-1]=="/" and not url[-4:]=="html":
				url+="/"
			if url in urlList:
				addToDict(cleanLinks, url, anchor.lower())
	return cleanLinks		

# Adds bidirectionality to links between URLS, as well as assigning anchor text blocks to
# the URL to which they link.
def makeGraph(pages):
	for url in pages:
		for link in pages[url]["outlinks"]:
			addToDict(pages[link], "inlinks", url)
			addToDict(pages[link], "anchors", pages[url]["outlinks"][link])
	return pages

# All-in-one method for reading a URL list file and creating a bi-directional
# graph implemented by a dictionary. Resulting dictionary will map a url to that url's
# ID, all outgoing links, all incomding links, all anchor text of those
# incoming links, and a snippet of the page's body text	
def getPageList(fileName):
	urls=readUrlList(fileName)
	pages={}
	index=0
	for url in urls:
		links, title, blurb = scrapeLinks(url)
		links = interpretLinks(links, url, urls)
		pages[url]= {"id":index, "outlinks":links, "title":title, 
					"inlinks":[], "anchors":[], "blurb": blurb[0:200]}
		index+=1
	return makeGraph(pages)


# Generates the transition matrix for the page graph. Consults urls because
# iterations of a dictionary are not always in a straightforward order, so this
# ensures correct ID linking.
def transitionMatrix(pages, a, urls):
	transitionMatrix = []
	for url in urls:
		transrow =[0.0]*len(urls)
		probPerLink= 0.0 if not len(pages[url]["outlinks"]) else 1.0/len(pages[url]["outlinks"])
		for outlink in pages[url]["outlinks"]:
			transrow[urls.index(outlink)] = probPerLink
		if len(pages[url]["outlinks"])==0:
			transrow=[1/len(urls)]*len(transrow)
		for i in range(len(transrow)):
			transrow[i] = (1.0-a)*transrow[i] + (a/len(urls))
		transitionMatrix+=[transrow]
		if not str(sum(transrow))==str(1.0): # for whatever reason, leaving as numberic values caused issues
			print "PROBLEM"
	return transitionMatrix

# Applies the power method to generate a page rank vector for the input
# transition matrix. Uses numpy array methods for multiplication.
def pageRankMatrix(transMat):
	x = np.array([1.0/len(transMat)]*len(transMat))
	transMat = np.array(transMat)	
	looping = True
	count = 0
	while looping:
		count+=1
		looping = False
		newx = np.dot(x,transMat)
		for i in range(len(x)):
			if not x[i]==newx[i]:
				looping=True
		x=newx
	return list(x)

# Adds page rank values to the input page dictionary.
def addPageRanks(pages, urls, pageranks):
	for url in urls:
		#print np.where(pageranks==(url))[0]
		pages[url]["rank"]=pageranks[urls.index(url)]
	return pages

# Writes the metadata file using data from the pages dictionary.
def writeMetadataFile(pages, filename):
	f=open(filename, 'w')
	print "Metadata file created at "+filename
	for url in pages:
		info = "ID: "+str(pages[url]['id'])+", Rank: "+str(pages[url]['rank'])+", Anchors: "
		if  "404 Not Found" in pages[url]["title"] :
			print url
		for anchor in pages[url]['anchors']:
			if not anchor=="":
				info+=anchor+", "
		f.write(info+"\n")
	f.close()

# Performs a search of title and anchor strings for the input string query, going
# word by word.
def search(pages, string):
	candidates = []
	print "Searching for: "+string
	for term in (string.lower()).split():
		for url in pages:
			match = 0
			if term in pages[url]["title"].lower():
				match =1
			for a in pages[url]["anchors"]:
				if term in a:
					match=1
			if match:
				pair = (pages[url]["rank"], url)
				if pair not in candidates:
					candidates+=[(pages[url]["rank"], url)]
			
	candidates.sort(reverse=True)
	for c in candidates:
		print "Title: "+pages[c[1]]["title"]
		print "    URL: "+c[1]
		print "    Preview: "+ pages[c[1]]["blurb"]+"..."
	if len(candidates)==0:
		print "No pages found."



def main():
	pages=None
	if 'y' in raw_input("Would you like to generate new set of pagerank files?").lower():
		f = raw_input("What text file would you like to use? (Blank for 'test3.txt')")
		if f=="":
			f="test3.txt"
		pages = getPageList(f)			
		#pickle.dump(pages, open("Graph.txt","w"))
		#pages = pickle.load(open("Graph.txt", 'r'))
		urls=pages.keys()
		ranks=pageRankMatrix(transitionMatrix(pages, .15,urls))
		pages = addPageRanks(pages, urls, ranks)
		pickle.dump(pages, open("Pageranks.txt", 'w'))
		#pages = pickle.load(open("Pageranks.txt", 'r'))
		writeMetadataFile(pages, "meta.txt")
	query=""
	if pages==None:
		pages = pickle.load(open("Pageranks.txt", 'r'))	
	while 1:
		query = raw_input("Query ('ZZZ' to exit): ")
		if query=="ZZZ":
			return
		search(pages, query)


if __name__ == "__main__":
    main()