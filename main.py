import psycopg2											#Required libraries
import urllib2
import re

region = "boston"

domain = "craigslist.org"

site = 'http://' + region + '.' + domain

def parse(regex, text):									#Parses line, splits using regex
	line = re.findall(regex,text)
	if len(line)==0:
		line=""
	else:
		line = line[0]
	return line.replace("\'","")

conn = psycopg2.connect("dbname=root user=root")		#Default database
cur = conn.cursor()

#createTable = "CREATE TABLE cars2(id text, time text, title text, year text, price text, url text, miles text, transmission text)"
#cur.execute(createTable)
#conn.commit()
#cur.close()

response = urllib2.urlopen(site + '/search/cto')	#Reads first page
html = response.read()

totalPages = int(re.findall("<a href='//www.craigslist.org/about/help/results' class='totalcount'>(\d+)</a>", html)[0])/100

for x in range(0,totalPages):
	cur = conn.cursor()
	currentPageURL = site + '/search/cto?s='+ str(x*100) + '&'
	page = urllib2.urlopen(currentPageURL).read()

	items = re.split('</p>', re.split('<div class="content">', page)[1])
	for item in items[:-1]:
		command = ""
		itemNum = parse('<p class="row" data-pid="(\d+)">',item)

		itemURL = parse('<a href="(/\w+/\w+/\d+.html)" class="i"',item)

		itemTime = parse('<time datetime="(\d{4}-\d{2}-\d{2} \d{2}:\d{2})"',item)

		itemTitle = parse('class="hdrlnk">([^<]+)</a>',item)

		itemYear = parse('\d+',itemTitle)

		itemPrice = parse('<span class="price">&#x0024;(\d+)</span>',item)

		itemURL = "http://boston.craigslist.org" + parse('<a href="(/\w+/\w+/\d+.html)" class="i"',item)

		itemPage = urllib2.urlopen(itemURL).read()

		itemMiles = parse("odometer: ?<b>(\d+k?)</b>",itemPage)

		if itemMiles=="":
			itemMiles = parse("(\d+k?) miles",itemPage)

		#print itemMiles

		itemTransmission = parse("transmission ?: ?<b>(\w+)</b>",itemPage)

		command = command + "INSERT INTO cars2 VALUES(" + "'" + itemNum + "'" "," + "'" + itemTime + "'" + "," + "'" + itemTitle + "'" + "," + "'" + itemYear + "'" + "," + "'" + itemPrice + "'" + "," + "'" + itemURL + "'" + "," + "'" + itemMiles + "'" + "," + "'" +itemTransmission + "'" + ");"

		#print command

		try:
			cur.execute(command)
			conn.commit()
		except psycopg2.IntegrityError:
			print "INTEGRITY ERROR"
		except psycopg2.ProgrammingError:
			print "PROMGRAMMING ERROR - " + command + "\n"
		except psycopg2.InternalError:
			print "INTERNAL ERROR - " + command + "\n"
			conn.rollback()
