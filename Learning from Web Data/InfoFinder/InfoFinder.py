from wikitools import wiki, api, page
import urllib
import simplejson
import sys
import time

# Near little time printer I wrote a while ago for something else.
def printTime(): 
    t= time.localtime()
    return str(t[1])+':'+str(t[2])+', '+str(t[3])+'/'+str(t[3])+'/'+str(t[0])

# Mostly just clears out the tags auto-entered into the API output. Future
# itterations could leave some of those in or add new tags here.
def printOut(st, file):
    st=st.encode(sys.stdout.encoding, 'replace')
    st=st.replace('<span class=\'searchmatch\'>','')
    st=st.replace('</span>','')
    st=st.replace('<b>','')
    st=st.replace('</b>','')
    st=st.replace('  ',' ')
    print st
    file.write(st+'\n')

    

f=open("mythos.csv",'wb')
writer=csv.writer(f)
writer.writerow('Name', 'Origin', 'Description', 'URL')

looping = 1
while(looping):
    keyword = raw_input("Enter a word or phrase you want to know more about: ")

    print("Starting Google Search....")

    # The google code is highly derived from
    # http://dcortesi.com/2008/05/28/google-ajax-search-api-example-python-code/
    # which was an indespensible little code sample.
    url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q='+keyword
    search_results = urllib.urlopen(url)
    json = simplejson.loads(search_results.read())
    results = json['responseData']['results']

    printOut("------ Google Results: ------",f)

    for hit in results:
        resultinfo=("Title: "+hit['title'] + "\n URL: " +
                    hit['url']+"\n"+hit['content']+"\n ") 
        printOut(resultinfo, f)


    print('\n'+"Starting Wikipedia Search....")
    # Used the wikitools documentation examples for reference, but was mostly
    # flying blind for this stuff. Good thing it's straightforward!
    site = wiki.Wiki("http://en.wikipedia.org/w/api.php")
    params = {'format':'json','action':'query', 'srlimit':'4',
              'srprop':'snippet','list':'search','srwhat':'text',
              'srsearch': keyword}
    # We limit the wikipedia results to 4 because a) it's clean and
    #    b) google limits to 4 automatically and I don't know how to
    #    change it.....
    request = api.APIRequest(site, params)
    result = request.query(querycontinue=False)
    results=result['query']

    printOut("------ Wikipedia Results: ------",f)
    printOut(str((results['searchinfo'])['totalhits'])+" Wikipedia hits. ",f)
             # Would have been nice to find a similar number for google...
    for hit in results['search']:
        hitinfo=("Title: "+hit['title']+'\n'+hit['snippet']+'\n ')
        printOut(hitinfo, f)

    loop = raw_input("Would you like to perform another search? (Y/N) ")
    if loop.lower().find('y')<0:
        looping=0

print('\n Fare well! \n')
f.write("\n End session. \n")
f.close()
