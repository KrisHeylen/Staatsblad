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
        
        
    
    
def getDateTocs(year, month, day,language):
	"""fill in the url of the perl script so that a table of contents
	of the specific day is shown. From this TOC, download the unique 
	ids of the articles."""
	date = year + "-" + month + "-" +day
	overviewurl = str("http://www.ejustice.just.fgov.be/cgi/summary_body.pl?" + 
			"language="+language+"&pub_date=" + date)
	fin = urllib2.urlopen(overviewurl)
	html = fin.read()
	fin.close()
	return date, html

def getSectionNames(TOChtml,namesDic,date):
    """Get different editions, if any, from the table of contents page and return these as a list of html strings"""
    editions = TOChtml.split("<a name=EDITION")
    for edition in editions:
        if re.match("\d>EDITI",edition[0]):
            curEdition = edition[0]
        else:
            curEdition = '0'
        regex = re.compile("<A name=(\d+)></a>(.+?)<input type=submit name=numac value=(\d+)",re.DOTALL)
        articles = regex.findall(edition)
        curSection = 'NA'
        curSource = 'NA'
        for article in articles:
            if (len(article) == 3):
                if article[0] == article[2]:
                    numac = article[0]
                    lines = stripHTMLTags(article[1])
                    lines = lines.split('\n')
                    artTile = []
                    section = []
                    source = []
                    for line in lines:
                        line = line.strip()
                        if (len(line) > 0) and (line[0] != '<'):
                            if float(len(re.findall('[A-Z]',line)))/float(len(line))> 0.5: # if it is a Section title or source
                                if not namesDic.has_key(line):
                                    namesDic[line] = [0]
                                namesDic[line][0] += 1
                                namesDic[line].append(date)




# what date do you want to start
y = 2010	#year
m = 12		#month
d = 1		#day
language = 'nl'
namesDic = {}
# loop until 2004, 12, 31 (so until > 2005, 13, 32)
while y < 2013:
	while m < 13:
		while d < 32:
			# for this date, get the articles
			day = str("0" + str(d))[-2:]
			date, html = getDateTocs(str(y), str(m), str(day),language)
			getSectionNames(html,namesDic,date)
			d = d + 1
		m = m + 1
		d = 1
	y = y + 1
	m = 1

import operator
import codecs
sortedNamesDic = sorted(namesDic.iteritems(), key=operator.itemgetter(1))
sortedNamesDic.reverse()
o = open('StaatsbladSectionNamesNL.txt','w')
for pair in sortedNamesDic:
    o.write((pair[0]+'\t'+str(pair[1][0])+'\t'+','.join(pair[1][1:])+'\n').encode('utf8'))

o.close()


y = 2010	#year
m = 12		#month
d = 1		#day
language = 'fr'
namesDic = {}
# loop until 2004, 12, 31 (so until > 2005, 13, 32)
while y < 2013:
	while m < 13:
		while d < 32:
			# for this date, get the articles
			day = str("0" + str(d))[-2:]
			date, html = getDateTocs(str(y), str(m), str(day),language)
			getSectionNames(html,namesDic,date)
			d = d + 1
		m = m + 1
		d = 1
	y = y + 1
	m = 1

import operator
import codecs
sortedNamesDic = sorted(namesDic.iteritems(), key=operator.itemgetter(1))
sortedNamesDic.reverse()
o = open('StaatsbladSectionNamesFR.txt','w')
for pair in sortedNamesDic:
    o.write((pair[0]+'\t'+str(pair[1][0])+'\t'+','.join(pair[1][1:])+'\n').encode('utf8'))

o.close()

y = 2010	#year
m = 12		#month
d = 1		#day
language = 'du'
namesDic = {}
# loop until 2004, 12, 31 (so until > 2005, 13, 32)
while y < 2013:
	while m < 13:
		while d < 32:
			# for this date, get the articles
			day = str("0" + str(d))[-2:]
			date, html = getDateTocs(str(y), str(m), str(day),language)
			getSectionNames(html,namesDic,date)
			d = d + 1
		m = m + 1
		d = 1
	y = y + 1
	m = 1

import operator
import codecs
        sortedNamesDic = sorted(namesDic.iteritems(), key=operator.itemgetter(1))
        sortedNamesDic.reverse()
        o = open('StaatsbladSectionNamesDE.txt','w')
        for pair in sortedNamesDic:
            o.write((pair[0]+'\t'+str(pair[1][0])+'\t'+','.join(pair[1][1:])+'\n').encode('utf8'))

        o.close()
