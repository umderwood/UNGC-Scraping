#Seth Lyles
#2016 June 22

from bs4 import BeautifulSoup
import urllib3, certifi, psycopg2, string
from dateutil.parser import parse

# Open a pool manager object; create a socket requiring certificates
http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

# Use the try if we might not connect to the db
#try:

# db login info
connect_str = "dbname='ungc_test' user='ducttapecreator' host='localhost' " #+ \
#			  "password='OLIVIA'"

# use our connection values to establish a connection
conn = psycopg2.connect(connect_str)
# create a psycopg2 cursor that can execute queries
cursor = conn.cursor()

# First half of URL of search page of participants
BASE_URL = 'https://www.unglobalcompact.org/what-is-gc/participants/search?page='

# Root page of UNGC, need for links to non-communicating and delisted entities
UNGC_URL = 'https://www.unglobalcompact.org'
def fix(stri):
	'''stri to clean for db entry
		db not so good with apostrophes
		get rid of spaces and ., other punctuation too, preventatively
		may cause complications for country ID but postgres doesn't case sensitive
		underscores will be difficult, let's deal with that later.'''
	# Python interprets 'None' as None for some reason;
	# 'None' was listed as reason for delisting so script errored out.
	if stri is not None:
		stri = stri.lower()
		stri = "".join(l for l in stri if l not in string.punctuation)
		stri = stri.replace(' ','_')
	
		return(stri)
	else:
		return("none")
	
def data_getter(url):
	''' Returns the page data from URL '''
	ld = http.request('GET', url)
	sp = BeautifulSoup(ld.data, "lxml")
	return(sp)

def scrape_data(url):
	''' Finds the date that the entity became delisted at URL '''
	sp = data_getter(url)
	# Find all the relevant locations in web page source
	#name, date joined, and date due/delisted are in different locations
	nm = sp.find('header', {'class':'main-content-header'})
	start = sp.find('div', {'class':'company-information-since'})
	ldtext = sp.find('div',  {'class':'company-information-cop-due'})
	othertext = sp.find('div', {'class':'company-information-overview'})
	# all other data is together, so we make list of key and value
	keys = othertext.findAll('dt')
	vals = othertext.findAll('dd')
	
	# clean dates so they are accepted by db
	dd = parse(ldtext.time.string).strftime('%Y/%m/%d')
	dj = parse(start.time.string).strftime('%Y/%m/%d')
	
	# build dict so we can return only one thing
	d = {'name': fix(nm.h1.string), 'date_due':dd, 'date_joined':dj}
	
	# add rest of data to dict
	for i in range(len(keys)):
		d[fix(keys[i].string)] = fix(vals[i].string)
	
	# return dictionary of keys (name, country, sector, etc.) with assoc. values ("tims_auto", "spain", "manufacturing", etc.)
	return(d)

def add_table():
	''' Adds the UNGC participants to a database, using a new table called 'active' '''
	# create a new table with columns called name, type, sector, country, and date
	# Fill table with members of UNGC
	# Can add fields to active, noncomm or delisted by looking at status!
	# or is it better to only have one table?
	fields = ('name', 'org_type', 'sector', 'country', 'global_compact_status', 'date_joined', 'date_due', 'employees', 'ownership')
	cursor.execute('''drop table if exists UNGC;''')
	cursor.execute("CREATE TABLE UNGC (%s char(250), %s char(150), %s char(150), %s char(150), %s char(150), %s date, %s date, %s int, %s char(150));" % fields)
			
	# The half of active link after page number
	THE_REST = 	'&search[keywords]=&search[per_page]=50&search[sort_direction]=asc&search[sort_field]=&utf8='
	
	# Is there a way to know how many pages without going to site?
	# Maybe do while loop, checking for 50 things? Probably not worth it, but could be more elegant
	
	for i in range(439): #439 as of 26 June 2016
	
		# observe which page we're parsing
		print(i)
		
		# get data from ith page
		soup = data_getter(BASE_URL + str(i+1) + THE_REST)
		
		# get name tags, for links are stored there
		nf = soup.findAll("th", 'name')
		
		# build list of links to get important dates, # employees, etc.
		links = [UNGC_URL + th.a['href'] for th in nf[1:]]
		
		# the list of dates for those delistings
		
		for link in links:
			data = ()
			d = scrape_data(link)
			
			# make new tuple of dictionary values
			# Do we really need a dictionary here? should be able to use a list so we don't have to build anything...
			for f in fields:
				data += (d[f], )
			
			#  ('name', 'org_type', 'sector', 'country', 'global_compact_status', 'date_joined', 'date_due', 'employees', 'ownership')
			# postgres wasn't accepting the string unless it was done in 2 pieces, parentheses maybe?
			cmd0 = "INSERT INTO UNGC (%s, %s, %s, %s, %s, %s, %s, %s, %s) " % fields
			cmd1 = "VALUES (%r, %r, %r, %r, %r, %r, %r, %s, %r)" % data
			cmd = cmd0 + cmd1	
			
			# Add to our db:
			cursor.execute(cmd)
								
		
		# make sure that we're getting the same number of each of these; names had same tag in headings and content of table
		# print(len(names), len(types), len(sectors), len(countries), len(dates))
		# print(names[0], types[0], sectors[0], countries[0], dates[0])
		

		# Save db
		conn.commit()
		
add_table()

# show that we have stuff in db:
cursor.execute("""SELECT date_joined
					 from active
					 where date_joined < '2014/01/01'
					 limit 50;""")
cs = cursor.fetchall()
for c in cs:
	print(c)

cursor.close()
conn.close()

#except Exception as e:
#    print("Uh oh, can't connect. Invalid dbname, user or password?")
#    print(e)





#def get_category_links(section_url):
    



