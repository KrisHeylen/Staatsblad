# fast script to download articles from Belgisch Staatsblad website
# based on script by Tom Ruette, November 1, 2010
#
# Extensions 
# - makes an index of all files downloaded 
# - adds information to index from the Belgisch Staatsblad TOC web pages about the edition, section and source department from which the document originated
# - larger set of html codes converted to unicode
# - has error catching for temporarily unreachable sites
# - also collects index information for previously downloaded files without overwriting these files
# - script can be restarted based on last downlaoded file in index
#
# Kris Heylen, March 28, 2013

import re
import urllib2
import codecs
import time
import os

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
    '&quot;' : u'\x22',
    '&amp;' : u'\x26',
    '&lt;' : u'\x3C',
    '&gt;' : u'\x3E',
    '&euro;' : u'\x80',
    '&sbquo;' : u'\x82',
    '&fnof;' : u'\x83',
    '&bdquo;' : u'\x84',
    '&hellip;' : u'\x85',
    '&dagger;' : u'\x86',
    '&Dagger;' : u'\x87',
    '&circ;' : u'\x88',
    '&permil;' : u'\x89',
    '&Scaron;' : u'\x8A',
    '&lsaquo;' : u'\x8B',
    '&OElig;' : u'\x8C',
    '&lsquo;' : u'\x91',
    '&rsquo;' : u'\x92',
    '&ldquo;' : u'\x93',
    '&rdquo;' : u'\x94',
    '&bull;' : u'\x95',
    '&ndash;' : u'\x96',
    '&mdash;' : u'\x97',
    '&tilde;' : u'\x98',
    '&trade;' : u'\x99',
    '&scaron;' : u'\x9A',
    '&rsaquo;' : u'\x9B',
    '&oelig;' : u'\x9C',
    '&Yuml;' : u'\x9F',
    '&nbsp;' : u'\xA0',
    '&iexcl;' : u'\xA1',
    '&cent;' : u'\xA2',
    '&pound;' : u'\xA3',
    '&curren;' : u'\xA4',
    '&yen;' : u'\xA5',
    '&brvbar;' : u'\xA6',
    '&sect;' : u'\xA7',
    '&uml;' : u'\xA8',
    '&copy;' : u'\xA9',
    '&ordf;' : u'\xAA',
    '&laquo;' : u'\xAB',
    '&not;' : u'\xAC',
    '&shy;' : u'\xAD',
    '&reg;' : u'\xAE',
    '&macr;' : u'\xAF',
    '&deg;' : u'\xB0',
    '&plusmn;' : u'\xB1',
    '&sup2;' : u'\xB2',
    '&sup3;' : u'\xB3',
    '&acute;' : u'\xB4',
    '&micro;' : u'\xB5',
    '&para;' : u'\xB6',
    '&middot;' : u'\xB7',
    '&cedil;' : u'\xB8',
    '&sup1;' : u'\xB9',
    '&ordm;' : u'\xBA',
    '&raquo;' : u'\xBB',
    '&frac14;' : u'\xBC',
    '&frac12;' : u'\xBD',
    '&frac34;' : u'\xBE',
    '&iquest;' : u'\xBF',
    '&Agrave;' : u'\xC0',
    '&Aacute;' : u'\xC1',
    '&Acirc;' : u'\xC2',
    '&Atilde;' : u'\xC3',
    '&Auml;' : u'\xC4',
    '&Aring;' : u'\xC5',
    '&AElig;' : u'\xC6',
    '&Ccedil;' : u'\xC7',
    '&Egrave;' : u'\xC8',
    '&Eacute;' : u'\xC9',
    '&Ecirc;' : u'\xCA',
    '&Euml;' : u'\xCB',
    '&Igrave;' : u'\xCC',
    '&Iacute;' : u'\xCD',
    '&Icirc;' : u'\xCE',
    '&Iuml;' : u'\xCF',
    '&ETH;' : u'\xD0',
    '&Ntilde;' : u'\xD1',
    '&Ograve;' : u'\xD2',
    '&Oacute;' : u'\xD3',
    '&Ocirc;' : u'\xD4',
    '&Otilde;' : u'\xD5',
    '&Ouml;' : u'\xD6',
    '&times;' : u'\xD7',
    '&Oslash;' : u'\xD8',
    '&Ugrave;' : u'\xD9',
    '&Uacute;' : u'\xDA',
    '&Ucirc;' : u'\xDB',
    '&Uuml;' : u'\xDC',
    '&Yacute;' : u'\xDD',
    '&THORN;' : u'\xDE',
    '&szlig;' : u'\xDF',
    '&agrave;' : u'\xE0',
    '&aacute;' : u'\xE1',
    '&acirc;' : u'\xE2',
    '&atilde;' : u'\xE3',
    '&auml;' : u'\xE4',
    '&aring;' : u'\xE5',
    '&aelig;' : u'\xE6',
    '&ccedil;' : u'\xE7',
    '&egrave;' : u'\xE8',
    '&eacute;' : u'\xE9',
    '&ecirc;' : u'\xEA',
    '&euml;' : u'\xEB',
    '&igrave;' : u'\xEC',
    '&iacute;' : u'\xED',
    '&icirc;' : u'\xEE',
    '&iuml;' : u'\xEF',
    '&eth;' : u'\xF0',
    '&ntilde;' : u'\xF1',
    '&ograve;' : u'\xF2',
    '&oacute;' : u'\xF3',
    '&ocirc;' : u'\xF4',
    '&otilde;' : u'\xF5',
    '&ouml;' : u'\xF6',
    '&divide;' : u'\xF7',
    '&oslash;' : u'\xF8',
    '&ugrave;' : u'\xF9',
    '&uacute;' : u'\xFA',
    '&ucirc;' : u'\xFB',
    '&uuml;' : u'\xFC',
    '&yacute;' : u'\xFD',
    '&thorn;' : u'\xFE',
    '&yuml;' : u'\xFF'
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
    while True:
        try:
            fin = urllib2.urlopen(overviewurl)
            html = fin.read()
            fin.close()
            break
        except:
            time.sleep(5)
            print 'waiting for url TOC of',date,language
    return date, html

def getArticle(date, numac,language):
    """from the date and the unique value of the article, one can get
    the html and thus the full text of the article"""
    url = str("http://www.ejustice.just.fgov.be/cgi/article_body.pl?" +
        "language="+language+"&caller=summary&pub_date=" + date + 
        "&numac=" + numac)
    while True:
        try:
            fin = urllib2.urlopen(url)
            html = fin.read()
            fin.close()
            break
        except:
            time.sleep(5)
            print 'waiting for url document of',date, numac,language
    return stripHTMLTags(html)

def getEditions(TOChtml,docDic,language,date):
    """Get different editions, if any, from the table of contents page (TOChtml) in a given language for a given date
    parse the section and source info (in bold face) and download articles contained in each edition/section/source
    add article (converted to unicode) and corresponding meta-information to the dictionary (docDic) with numac-date as key"""
    sectionNames = ["ANDERE BESLUITEN","WETTEN, DECRETEN, ORDONNANTIES EN VERORDENINGEN","OFFICIELE BERICHTEN","AGENDA'S","AUTRES ARRETES","LOIS, DECRETS, ORDONNANCES ET REGLEMENTS","AVIS OFFICIELS","ORDRES DU JOUR"]
    regionNames = ['VLAAMSE GEMEENSCHAP','DUITSTALIGE GEMEENSCHAP','WAALS GEWEST','BRUSSELS HOOFDSTEDELIJK GEWEST','FRANSE GEMEENSCHAP','VLAAMS GEWEST','REGION WALLONNE','REGION DE BRUXELLES-CAPITALE','COMMUNAUTE FLAMANDE',u'COMMUNAUTE FRAN\xc7AISE','COMMUNAUTE GERMANOPHONE','REGION FLAMANDE',"DEUTSCHSPRACHIGE GEMEINSCHAFT","WALLONISCHE REGION","DEUTSCHPRACHIGE GEMEINSCHAFT"]
    levelNames = ['GEMEENSCHAPS- EN GEWESTREGERINGEN','GOUVERNEMENTS DE COMMUNAUTE ET DE REGION','GEMEINSCHAFTS- UND REGIONALREGIERUNGEN']
    editions = TOChtml.split("<a name=EDITION")
    for edition in editions:
        if re.match("\d>EDITI",edition):
            curEdition = edition[0]
        else:
            curEdition = '0'
        regex = re.compile("<A name=(\d+)></a>(.+?)<input type=submit name=numac value=(\d+)",re.DOTALL)
        articles = regex.findall(edition)
        curSection = 'NA'
        curRegion = 'NA'
        curSource = 'NA'
        curLevel = 'NA'
        curTitle = 'NA'
        url = 'NA'
        for article in articles:
            if (len(article) == 3):
                if article[0] == article[2]:
                    numac = article[0]
                    lines = stripHTMLTags(article[1])
                    lines = lines.split('\n')
                    title = []
                    section = []
                    region = []
                    level = []
                    source = []
                    for line in lines:
                        line = line.strip()
                        if (len(line) > 0) and (line[0] != '<'):
                            if float(len(re.findall('[A-Z]',line)))/float(len(line))> 0.5: # if it is a Section title or source
                                if line in sectionNames:
                                    section.append(line)
                                elif line in regionNames:
                                    region.append(line)
                                elif line in levelNames:
                                    level.append(line)
                                else:
                                    source.append(line)
                            else:
                                title.append(line)
                    if len(section) > 0:
                        curSection = ' '.join(section)
                        curRegion = 'NA'
                        curSource = 'NA'
                    if len(level) > 0:
                        curLevel = ' '.join(level)
                        curRegion = 'NA'
                        curSource = 'NA'
                    if len(region) > 0:
                        curRegion = ' '.join(region)
                        curSource = 'NA'
                    if len(source) > 0:
                        curSource = ' '.join(source)
                    if len(title) > 0:
                        curTitle = ' '.join(title)
                    artID = date+'-'+str(numac)
                    if not docDic.has_key(artID):
                        docDic[artID] = {'nl':{},'fr':{},'du':{}}
                    docDic[artID][language]['edition'] = curEdition
                    docDic[artID][language]['section'] = curSection
                    docDic[artID][language]['region'] = curRegion
                    docDic[artID][language]['source'] = curSource
                    docDic[artID][language]['title'] = curTitle
                    docDic[artID][language]['article'] = getArticle(date, numac,language)
                    url = str("http://www.ejustice.just.fgov.be/cgi/article_body.pl?" +"language="+language+"&caller=summary&pub_date=" + date + "&numac=" + numac)
                    docDic[artID][language]['url'] = url
                    curTitle = 'NA'
                    url = 'NA'
                                                
def writeDic(docDic,targetDir,index,languages):
    """write out the information in the dictionary (docDic)
    meta-information per numac-date is written to index
    article is written to targetDir/language-files/date-numac.txt"""
    fixedcolumns = ['docID','pubDate','numac']
    langcolumns = ['articleURL','filelocation','edition','section','region','source','title']
    if not os.path.exists(index):
        o = codecs.open(index, "w", "utf-8")
        o.write('\t'.join(fixedcolumns))
        for language in languages:
            o.write('\t'+language+'.url')
            o.write('\t'+language+'.filelocation')
            o.write('\t'+language+'.edition')
            o.write('\t'+language+'.section')
            o.write('\t'+language+'.region')
            o.write('\t'+language+'.source')
            o.write('\t'+language+'.title')
        o.write('\n')
        o.close()
    o = codecs.open(index,'a','utf-8')
    docs = docDic.keys()
    for doc in docs:
        o.write(doc)
        date = ''.join(doc.split('-')[:3])
        o.write('\t'+date)
        numac = doc.split('-')[3]
        o.write('\t'+numac)
        for language in languages:
            if len(docDic[doc][language]) == 0:
                o.write(''.join(['\tNA']*len(langcolumns)))
            else:
                o.write('\t'+docDic[doc][language]['url'] )
                filelocation = targetDir+'/'+language+'-files/'+doc+'.txt'
                if not os.path.exists(filelocation):
                    fout = codecs.open(filelocation, "w", "utf-8")
                    fout.write(docDic[doc][language]['article'] )
                    fout.close()
                o.write('\t'+filelocation)
                for col in langcolumns[2:]:
                    o.write('\t'+docDic[doc][language][col])
        o.write('\n')
    o.close()
        
        
    
    
###############################################################################

# some main code that calls the above methods
# do not forget to change in this main code:
# - the place where to save stuff (targetDir)
# do not forget to change in the routines above:
# - the languages that you want to download (languages)

# what date do you want to start 
y = 1997	#year
m = 10		#month
d = 01	#day
#which languages do you want to collect?
languages = ['nl','fr','du']
#where are the files and index written to?
targetDir = '/home/sociolectormetry/corpora/staatsblad-be'
index = '/home/sociolectormetry/corpora/staatsblad-be/index'
# loop until 2012 12, 31 (so until > 2013, 13, 32)

#in case of restart, get from index to which date was alreaday downloaded
#also removes all documents from new start date from index!!!!
#otherwise they will occur twice in the index
i = codecs.open(index,'r','utf-8')
lns = i.readlines()
i.close
[y,m,d,numac] = lns[-1].split('\t')[0].split('-')
date = y+'-'+m+'-'+d+'-'
lastlnr = -1
while True:
    lastlnr -= 1
    [cy,cm,cd,cnumac]  = lns[lastlnr].split('\t')[0].split('-')
    curDate = cy+'-'+cm+'-'+cd+'-'
    if curDate != date:
        break
lastlnr += 1
o = codecs.open(index,'w','utf-8')
o.write(''.join(lns[:lastlnr]))
o.close()
y = int(y)
m = int(m)
d = int(d)

while y < 2013:
    while m < 13:
        while d < 32:
            # for this date, get the articles
            day = str("0" + str(d))[-2:]
            month = str("0" + str(m))[-2:]
            docDic = {}
            for language in languages:
                date, TOChtml = getDateTocs(str(y), str(month), str(day),language)
                getEditions(TOChtml,docDic,language,date)
            writeDic(docDic,targetDir,index,languages)
            time.sleep(.5)
            print date+' processed'
            d = d + 1
        m = m + 1
        d = 1   
    y = y + 1
    m = 1
