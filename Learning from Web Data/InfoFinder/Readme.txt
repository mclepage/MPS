InfoFinder.py is a quick little script that takes a key word or phrase and returns the first 4 responses to searching this key on Google or Wikipedia. The output, which is both printed within the python terminal and written to a file (Findings.txt), includes: the titles for both wikipedia articles and google results, the first sentence or two from each (of lengths based on what is returned by the 2 system's APIs), as well as URLs for the results from google. After displaying results, the code will ask the user if they want to perform another search, and react accordingly.

 The script requires the external libraries for wikitools and simplejson, as well as the preinstalled python libraries urllib, sys and time. NOTE: Though wikitools claims otherwise, I had consistent trouble getting wikitools to install properly on python 3.2, or any version besides 2.7 for that matter. More on this in the postmortem below.

Code borrowed from Damon Cortesi's blog at http://dcortesi.com/2008/05/28/google-ajax-search-api-example-python-code/ as well as from the official documentation of wikitools.

