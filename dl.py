# fast script to download articles from Belgisch Staatsblad website
# has no Error catching, but verbose output, so that the script can be started
# by just changin the starting date.
# DO NOT FORGET TO ADJUST THE SAVE PATH AND LANGUAGE!!!
#
# Tom Ruette, November 1, 2010

import re
import urllib2
import codecs

def stripHTMLTags (html):
  """Strip HTML tags from any string and transfrom special entities"""

  import re

  text = html.decode("latin-1")

  # apply rules in given order!
  rules = [
    { r'>\s+' : u'>'},                  # remove spaces after a tag opens or closes
    { r'\s{2,}' : u' '},                   # replace consecutive spaces
    { r'\s*<br\s*/?>\s*' : u'\n'},      # newline after a <br>
    { r'</(div)\s*>\s*' : u'\n'},       # newline after </p> and </div> and <h1/>...
    { r'</(p|h\d)\s*>\s*' : u'\n\n'},   # newline after </p> and </div> and <h1/>...
    { r'<head>.*<\s*(/head|body)[^>]*>' : u'' },     # remove <head> to </head>
    { r'<a\s+href="([^"]+)"[^>]*>.*</a>' : r'\1' },  # show links instead of texts
    { r'[ \t]*<[^<]*?/?>' : u'' },            # remove remaining tags
    { r'^\s+' : u'' }                   # remove spaces at the beginning
  ]

  for rule in rules:
    for (k,v) in rule.items():
      regex = re.compile (k, re.IGNORECASE)
      text  = regex.sub (v, text)

  # replace special strings
  special = {
    '&nbsp;' : ' ', '&amp;' : '&', '&quot;' : '"',
    '&lt;'   : '<', '&gt;'  : '>', '&apos;' : "'",
    '&sect;'  : '$'
  }

  for (k,v) in special.items():
    text = text.replace (k, v)

  return text

def getDateTocs(year, month, day):
	"""fill in the url of the perl script so that a table of contents
	of the specific day is shown. From this TOC, download the unique 
	ids of the articles."""

	date = year + "-" + month + "-" +day

	overviewurl = str("http://www.ejustice.just.fgov.be/cgi/summary_body.pl?" + 
			"language=du&pub_date=" + date)

	fin = urllib2.urlopen(overviewurl)
	html = fin.read()
	fin.close()

	regex = re.compile("name=numac value=(\d+?)\n")
	numacvalues = regex.findall(html)
	
	return date, numacvalues

def getArticle(date, numac):
	"""from the date and the unique value of the article, one can get
	the html and thus the full text of the article"""

	# change the language=du value into language=nl or language=fr to download
	# other languages
	url = str("http://www.ejustice.just.fgov.be/cgi/article_body.pl?" +
		"language=nl&caller=summary&pub_date=" + date + 
		"&numac=" + numac)

	fin = urllib2.urlopen(url)
	html = fin.read()
	fin.close()

	return stripHTMLTags(html)

###############################################################################

# some main code that calls the above methods
# do not forget to change in this main code:
# - the place where to save stuff
# do not forget to change in the routines above:
# - the language that you want to download

# what date do you want to start
y = 2005	#year
m = 1		#month
d = 1		#day

# loop until 2004, 12, 31 (so until > 2005, 13, 32)
while y < 2012:
	while m < 13:
		while d < 32:
			# for this date, get the articles
			day = str("0" + str(d))[-2:]
			date, tocs = getDateTocs(str(y), str(m), str(day))
			# for each article, get the text and write it out
			for toc in tocs:
				art = getArticle(date, toc)
# !!! change this save path if you want to!
				fname = str("/home/sociolectormetry/corpora/staatsblad-be/nl-files/" +
					str(y) + "-" + str(m) + "-" + str(d) + 
					"-" + str(toc) + ".txt")
				fout = codecs.open(fname, "w", "utf-8")
				fout.write(art)
				fout.close()
				print "wrote", fname
			d = d + 1
		m = m + 1
		d = 1
	y = y + 1
	m = 1
